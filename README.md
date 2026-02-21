# Linkding Reminder

Daily email reminders for your Linkding bookmarks, filtered by tag.

## Python

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit with your settings
python3 linkding.py
```

| Variable | Required | Default |
|---|---|---|
| `LINKDING_TOKEN` | Yes | — |
| `SMTP_HOST` | Yes | — |
| `SMTP_USERNAME` | Yes | — |
| `SMTP_PASSWORD` | Yes | — |
| `SMTP_SENDER` | Yes | — |
| `SMTP_RECIPIENT` | Yes | — |
| `LINKDING_URL` | No | `http://192.168.50.5:9090` |
| `LINKDING_PUBLIC_URL` | No | same as `LINKDING_URL` |
| `LINKDING_TAGS` | No | `2do` |
| `SMTP_PORT` | No | `465` |

## Google Apps Script

1. Open [script.google.com](https://script.google.com/) → **New project**
2. Paste the contents of `linkding.gs`
3. Add **Script Properties** under ⚙️ Project Settings:

| Property | Required | Default |
|---|---|---|
| `LINKDING_URL` | Yes | — |
| `LINKDING_TOKEN` | Yes | — |
| `EMAIL_RECIPIENT` | Yes | — |
| `LINKDING_PUBLIC_URL` | No | same as `LINKDING_URL` |
| `LINKDING_TAGS` | No | `2do` |

4. Run `setup` to create a daily trigger, then run `main` to test