from unittest.mock import Mock, patch

import pytest

from aw_watcher_steam.main import get_currently_played_game


@patch("aw_watcher_steam.main.requests.get")
def test_current_game(request_get):
    response = Mock()
    response.json.return_value = {
        "response": {
            "players": [{"gameextrainfo": "Portal 2", "gameid": "620"}]
        }
    }
    request_get.return_value = response

    assert get_currently_played_game("secret", "123") == {
        "currently-playing-game": "Portal 2",
        "game-id": "620",
    }
    request_get.assert_called_once_with(
        "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/",
        params={"key": "secret", "steamids": "123"},
        timeout=15,
    )


@patch("aw_watcher_steam.main.requests.get")
def test_not_playing(request_get):
    response = Mock()
    response.json.return_value = {"response": {"players": [{}]}}
    request_get.return_value = response

    assert get_currently_played_game("secret", "123") == {}


@patch("aw_watcher_steam.main.requests.get")
def test_missing_player(request_get):
    response = Mock()
    response.json.return_value = {"response": {"players": []}}
    request_get.return_value = response

    with pytest.raises(RuntimeError, match="no player"):
        get_currently_played_game("secret", "123")
