# multijournal

Stream systemd journal logs to a web UI via WebSockets. Configure which services to monitor in a TOML file, and view all logs in a grid layout with full-screen toggle per service.

## Setup

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

## Configuration

Edit `config.toml` to set the host/port and define which systemd services to monitor:

```toml
[settings]
host = "0.0.0.0"
port = 8092
lines = 100

[[services]]
name = "My Service"
unit = "myservice.service"
```

The config path can also be set via the `MULTIJOURNAL_CONFIG` environment variable.

## Running

```bash
uv run multijournal
```

Then open `http://localhost:8092` in a browser.

## Install as a systemd service

```bash
sudo cp multijournal.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now multijournal.service
```

## Updating

After pulling new changes:

```bash
./update.sh
```

This pulls the latest code, syncs dependencies, and restarts the service.

## Development

```bash
uv run ruff check src/   # lint
uv run ruff format src/  # format
uv run mypy src/         # type check
```


## Check Logs

```bash
sudo journalctl -u multijournal.service -n 500 -f
```