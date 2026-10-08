import argparse
import logging
import signal
from datetime import datetime, timezone
from pathlib import Path
from time import sleep

import requests
from aw_client import ActivityWatchClient
from aw_core import dirs
from aw_core.models import Event


CONFIG = """
[aw-watcher-steam]
steam_id = ""
api_key = ""
poll_time = 5.0
"""
STEAM_API_URL = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"


def load_config():
    from aw_core.config import load_config_toml

    return load_config_toml("aw-watcher-steam", CONFIG)


def get_currently_played_game(api_key: str, steam_id: str) -> dict:
    response = requests.get(
        STEAM_API_URL,
        params={"key": api_key, "steamids": steam_id},
        timeout=15,
    )
    response.raise_for_status()
    players = response.json().get("response", {}).get("players", [])
    if not players:
        raise RuntimeError("Steam returned no player for the configured steam_id")

    player = players[0]
    if "gameextrainfo" not in player:
        return {}
    return {
        "currently-playing-game": player["gameextrainfo"],
        "game-id": player["gameid"],
    }


def parse_args():
    parser = argparse.ArgumentParser(description="Track Steam presence in ActivityWatch")
    parser.add_argument("--host", help="ActivityWatch server host")
    parser.add_argument("--port", type=int, help="ActivityWatch server port")
    parser.add_argument("--testing", action="store_true", help="use the testing server")
    return parser.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logger = logging.getLogger("aw-watcher-steam")
    config = load_config()["aw-watcher-steam"]
    poll_time = float(config.get("poll_time", 5.0))
    api_key = str(config.get("api_key", "")).strip()
    steam_id = str(config.get("steam_id", "")).strip()
    config_file = Path(dirs.get_config_dir("aw-watcher-steam")) / "aw-watcher-steam.toml"

    if not api_key or not steam_id:
        logger.error("Set steam_id and api_key in %s", config_file)
        return 1
    if poll_time <= 0:
        logger.error("poll_time must be greater than zero in %s", config_file)
        return 1

    stopping = False

    def stop(_signum, _frame):
        nonlocal stopping
        stopping = True

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    client = ActivityWatchClient(
        "aw-watcher-steam",
        testing=args.testing,
        host=args.host,
        port=args.port,
    )
    bucket_id = f"{client.client_name}_{client.client_hostname}"
    client.create_bucket(bucket_id, event_type="currently-playing-game")

    last_status = None
    with client:
        while not stopping:
            try:
                game_data = get_currently_played_game(api_key, steam_id)
                if game_data:
                    event = Event(timestamp=datetime.now(timezone.utc), data=game_data)
                    client.heartbeat(
                        bucket_id,
                        event,
                        pulsetime=poll_time + 1,
                        queued=True,
                        commit_interval=max(30.0, poll_time * 2),
                    )
                status = game_data.get("currently-playing-game", "not playing")
                if status != last_status:
                    logger.info("Steam status: %s", status)
                    last_status = status
            except requests.RequestException as error:
                logger.warning("Steam API request failed: %s", error)
            except (KeyError, ValueError, RuntimeError) as error:
                logger.warning("Invalid Steam API response: %s", error)

            if not stopping:
                sleep(poll_time)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
