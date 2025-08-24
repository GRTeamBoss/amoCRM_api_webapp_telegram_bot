import json
import time
from pathlib import Path

import requests

from config.config import Config


def update_tokens():
    config = Config()
    config.reload()
    if int(time.time()) > config.TOKEN_DICT.get("expires_at", 0):
      payload = {
        "client_id": config.CLIENT_ID,
        "client_secret": config.CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": config.TOKEN_DICT["refresh_token"],
        "redirect_uri": config.REDIRECT_URI,
      }

      response = requests.post(config.TOKEN_ACCESS_URL, json=payload, timeout=30)
      if response.status_code == 200:
          new_tokens = response.json()
          save_tokens(new_tokens)
          return new_tokens
      else:
          raise RuntimeError(f"Error updating tokens: {response.text}")


def save_tokens(data):
    expires_in = int(data.get("expires_in", 0))
    if expires_in > 0:
        data["expires_at"] = int(time.time()) + max(expires_in - 60, 0)
    Path("tokens.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
