# Branches

## Main (javascript)

## Dev (python) *Current

# Config

## Files

```plaintext
# .env
TELEGRAM_TOKEN=<TELEGRAM_TOKEN>
ADMINS=[<TELEGRAM_PEER_ID>]
TOKENS_JSON_GET_FILE=<PATH_TO_FILE> ; # .json DEFAULT: tokens.json
URLS_FILE=<PATH_TO_FILE> ; # .txt DEFAULT: urls.txt
DATA_JSON_SAVE_FILE=<PATH_TO_FILE> ; # .json DEFAULT: stages.json
DATA_EXCEL_SAVE_FILE=<PATH_TO_FILE> ; # .xlsx DEFAULT: stages.xlsx
SUBDOMAIN=<SUBDOMAIN> ; # https://<SUBDOMAIN>.amocrm.ru
CLIENT_ID=<CLIENT_ID>
CLIENT_SECRET=<CLIENT_SECRET>
```

```json
// tokens.json
{
  "token_type": ..., // Bearer
  "expires_in": ..., // timestamp
  "server_time": ..., // timestamp
  "access_token": ..., // str
  "refresh_token": ..., // str
  "expires_at": ... // timestamp
}
```

```plaintext
# urls.txt
<URL>
Skip ; print empty line or skip row in excel file
<URL>
```

# Run

```bash
pip install -r requirements.txt
python3 main.py
```
