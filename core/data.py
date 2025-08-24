import json
from pathlib import Path
from collections import Counter
from datetime import date, datetime

import requests

from config.config import Config
from middleware import token_validate


class AmoDataParsing:

  def __init__(self, date_from=date.today().strftime("%d.%m.%Y"), date_to=date.today().strftime("%d.%m.%Y")):
    self.config = Config()
    self.config.reload()
    self.access_token = self.config.TOKEN_DICT.get("access_token")
    self.token_type = self.config.TOKEN_DICT.get("token_type")
    # self.date_from = date_from
    # self.date_to = date_to
    self.date_from = int(datetime.strptime(date_from, "%d.%m.%Y").timestamp())
    self.date_to = int(datetime.strptime(date_to, "%d.%m.%Y").timestamp())+86359


  def get_headers(self):
    return {
        "Content-Type": "application/json",
        "Authorization": f"{self.token_type} {self.access_token}"
    }

  @token_validate
  def update_leads(self):
    result = {}
    pipelines = self.get_pipelines()
    result["date_from"] = datetime.fromtimestamp(self.date_from).strftime("%d.%m.%Y")
    result["date_to"] = datetime.fromtimestamp(self.date_to).strftime("%d.%m.%Y")
    result["pipeline"] = {}
    result["events"] = {}
    leadCounter = []
    for pipeline in pipelines:
      leads = self.get_leads(pipeline_id=pipeline["id"])
      events = self.get_events(pipeline_id=pipeline["id"])
      stages = pipeline.get("_embedded", {}).get("statuses", [])
      if leads:
        leadCounter = Counter(lead.get("status_id", 0) for lead in leads if lead.get("pipeline_id", []) == pipeline["id"])
      result["pipeline"][pipeline["id"]] = {
        "name": pipeline["name"],
        "stages": {
          stage["id"]: {
            "name": stage["name"], 
            "leads": {"length": leadCounter.get(stage["id"], 0)},
          } for stage in stages
        }
      }
      if leads is None:
        pass
      else:
        for lead in leads:
          result["pipeline"][lead["pipeline_id"]]["stages"].get(lead["status_id"], {}).get("leads", {})[lead["id"]] = lead["name"]
      eventCounter = Counter(event["created_by"] for event in events)
      for event in events:
        result["events"].setdefault(event["created_by"], {})["length"] = eventCounter[event["created_by"]]
        result["events"].setdefault(event["created_by"], {}).setdefault(event["entity_type"], {}).setdefault(event["type"], {})[event["id"]] = {
            "entity_id": event["entity_id"],
            "created_by": event["created_by"],
            "account_id": event["account_id"]
        }

    return result

  def get_events(self, pipeline_id):
    page = 1
    per_page = 100
    headers = self.get_headers()
    url = f"{self.config.BASE_URL}/api/v4/events"
    result = []
    while True:
      params = [
          ("filter[pipeline_id][]", pipeline_id),
          ("filter[event_type][]", 14),
          ("filter[created_at][from]", self.date_from),
          ("filter[created_at][to]", self.date_to),
          ("limit", per_page),
          ("page", page)
      ]
      try:
        response = requests.get(url, headers=headers, timeout=30, params=params)
        response.raise_for_status()
        page += 1
        events = response.json().get("_embedded", {}).get("events", [])
        if not events:
          break
        if response.status_code == 200:
            result.extend(events)
      except requests.RequestException as e:
        break
    return result

  def get_pipelines(self):
    headers = self.get_headers()
    url = f"{self.config.BASE_URL}/api/v4/leads/pipelines"
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    if response.status_code == 200:
        return response.json()["_embedded"]["pipelines"]
    return None

  def get_leads(self, pipeline_id):
    headers = self.get_headers()
    url = f"{self.config.BASE_URL}/api/v4/leads"
    params = [
      ("filter[pipeline_id][]", pipeline_id)
    ]
    params.append(("filter[created_at][from]", self.date_from))
    params.append(("filter[created_at][to]", self.date_to))
    params.append(("with[]", "contacts"))
    params.append(("with[]", "tags"))
    params.append(("limit", 500))
    response = requests.get(url, headers=headers, timeout=30, params=params)
    response.raise_for_status()
    if response.status_code == 200:
      return response.json().get("_embedded", {}).get("leads", [])
    elif response.status_code == 204:
      return None

  def save_pipelines_to_json(self, pipelines, filename="stages.json"):
    Path(filename).write_text(json.dumps(pipelines, indent=4, ensure_ascii=False))