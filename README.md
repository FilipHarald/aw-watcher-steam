# aw-watcher-steam

An [ActivityWatch](https://activitywatch.net/) watcher that records the Steam
game shown in your online presence. This works across devices, provided your
Steam game details are public and the machine running the watcher is online.

## Install

```sh
pipx install .
```

For an editable development install, use `pipx install --editable .`.

## Configure

Run `aw-watcher-steam` once to create the config, then edit:

```text
~/.config/activitywatch-default/aw-watcher-steam/aw-watcher-steam.toml
```

```toml
[aw-watcher-steam]
steam_id = "YOUR_17_DIGIT_STEAM_ID"
api_key = "YOUR_STEAM_WEB_API_KEY"
poll_time = 5.0
```

The `activitywatch-default` directory is used when the watcher is launched by
current `aw-tauri` releases, which pass the `default` ActivityWatch profile.

- Register a Steam Web API key at https://steamcommunity.com/dev/apikey
  (`localhost` is fine as the domain).
- Find your Steam ID at https://help.steampowered.com/en/faqs/view/2816-BE67-5B69-0FEC

## Start with aw-tauri

`aw-tauri` discovers the executable in `~/.local/bin`. Add it to
`~/.config/activitywatch/aw-tauri/config.toml`:

```toml
[autostart]
modules = ["aw-awatcher", "aw-watcher-steam"]
```

Restart `aw-tauri`, or start the watcher from its **Modules** tray submenu.

## Command-line options

```text
--host HOST     ActivityWatch server host
--port PORT     ActivityWatch server port
--testing       Use ActivityWatch's testing server
```
