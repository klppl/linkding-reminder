# Linkding Reminder

Fetches bookmarks from Linkding and sends them via email as HTML reminders.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and configure your settings.

## Usage

```bash
source venv/bin/activate
python3 linkding.py
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `LINKDING_TOKEN` | Linkding API token | Yes |
| `SMTP_HOST` | SMTP server hostname | Yes |
| `SMTP_USERNAME` | SMTP username | Yes |
| `SMTP_PASSWORD` | SMTP password | Yes |
| `SMTP_SENDER` | Email sender address | Yes |
| `SMTP_RECIPIENT` | Email recipient address | Yes |
| `LINKDING_TAGS` | Comma-separated tags (default: `2do`) | No |
| `LINKDING_URL` | Linkding URL (default: `http://192.168.50.5:9090`) | No |
| `SMTP_PORT` | SMTP port (default: `465`) | No |