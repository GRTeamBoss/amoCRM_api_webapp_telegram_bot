import json
from pathlib import Path
from collections import Counter
from datetime import date, datetime
import time
from typing import Union, List, Dict, Optional, Required, Any

import requests

from config.config import Config
from core import TaskFilter, serialize_dict_to_json
from middleware import token_validate


class AmoDataParsing:

  def __init__(self, 
               filter: TaskFilter, 
               date_from: str = date.today().strftime("%d.%m.%Y"), 
               date_to: str = date.today().strftime("%d.%m.%Y")
               ):
    self.config: Config = Config()
    self.config.reload()
    self.access_token: str = self.config.TOKEN_DICT.get("access_token")
    self.token_type: str = self.config.TOKEN_DICT.get("token_type")
    self.filter: dict = serialize_dict_to_json(filter)
    self.date_from: str = date_from
    self.date_to: str = date_to

  
  def _serialize_date_to_timestamp(self, default: str, from_: str=None, to_: str=None) -> int | Dict | None:
    if default:
      return int(datetime.strptime(default, "%d.%m.%Y").timestamp())
    else:
      if all(from_, to_):
        return {
          "from": int(datetime.strptime(from_, "%d.%m.%Y").timestamp()),
          "to": int(datetime.strptime(to_, "%d.%m.%Y").timestamp())+86399
        }
      else:
        return None

  def _serialize_timestamp_to_date(self, default: None | str | int, from_: str | int = None, to_: str | int = None) -> str | Dict | None:
    if default:
      return datetime.fromtimestamp(int(default)).strftime("%d.%m.%Y")
    else:
      if all(from_, to_):
        return {
          "from": datetime.fromtimestamp(int(from_)).strftime("%d.%m.%Y"),
          "to": datetime.fromtimestamp(int(to_)).strftime("%d.%m.%Y")
        }
      else:
        return None


  def get_headers(self) -> Dict:
    return {
        "Content-Type": "application/json",
        "Authorization": f"{self.token_type} {self.access_token}"
    }

  @token_validate
  def update_leads(self) -> Dict:
    result = {}
    pipelines = self.get_pipelines()
    tasks = self.get_tasks()
    result["date_from"] = self.date_from
    result["date_to"] = self.date_to
    result["pipeline"] = {}
    result["events"] = {}
    result["leads"] = {}
    result["tasks"] = {}
    leadCounter = {}
    for pipeline in pipelines:
      leads = self.get_leads(pipeline["id"])
      events = self.get_events(pipeline["id"])
      stages = pipeline.get("_embedded", {}).get("statuses", [])

      if leads:
        leadCounter = Counter(lead.get("status_id", 0) for lead in leads if lead.get("pipeline_id", []) == pipeline["id"])

      result["pipeline"][pipeline["id"]] = {
        "name": pipeline["name"],
        "stages": {
          stage["id"]: {
            "name": stage["name"], 
            "leads": {"__total": leadCounter.get(stage["id"], 0)},
          } for stage in stages
        }
      }

      if leads:
        for lead in leads:
          result["pipeline"][lead["pipeline_id"]]["stages"].get(lead["status_id"], {}).get("leads", {})[lead["id"]] = lead["name"]
          result["leads"].setdefault(lead["pipeline_id"], {}).setdefault(lead["created_by"], {}).setdefault(lead["status_id"], {}).setdefault(lead["responsible_user_id"], {}).setdefault(lead["account_id"], {})[lead["id"]] = {
            "name": lead["name"],
            "price": lead["price"],
            "group_id": lead["group_id"],
            "is_deleted": lead["is_deleted"],
            "score": lead["score"],
            "custom_fields_values": lead["custom_fields_values"]
          }
      
      if events:
        eventCounter = Counter((event["type"], event["entity_type"], event["created_by"]) for event in events)
        for event in events:
          result["events"].setdefault(event["created_by"], {}).setdefault(event["entity_type"], {}).setdefault(event["type"], {})[event["id"]] = {
              "entity_id": event["entity_id"],
              "created_by": event["created_by"],
              "account_id": event["account_id"]
          }
          result["events"].setdefault(event["created_by"], {}).setdefault(event["entity_type"], {})[event["type"]]["__total"] = eventCounter[(event["type"], event["entity_type"], event["created_by"])]
    if tasks:
      taskCounter = Counter(task["created_by"] for task in tasks)
      taskTypeCounter = Counter((task["created_by"], task["entity_type"]) for task in tasks)
      taskCompletedCounter = Counter((task["created_by"], task["entity_type"], task["is_completed"]) for task in tasks)
      taskUserCounter = Counter((task["created_by"], task["entity_type"], task["is_completed"], task["responsible_user_id"]) for task in tasks)
      for task in tasks:
        result["tasks"].setdefault(task["created_by"], {}).setdefault(task["entity_type"], {}).setdefault(task["is_completed"], {}).setdefault(task["responsible_user_id"], {})[task["id"]] = {
          "text": task["text"],
          "result": task["result"],
          "complete_till": task["complete_till"]
        }
        result["tasks"][task["created_by"]]["__total"] = taskCounter.get(task["created_by"], 0)
        result["tasks"][task["created_by"]][task["entity_type"]]["__total"] = taskTypeCounter.get((task["created_by"], task["entity_type"]), 0)
        result["tasks"][task["created_by"]][task["entity_type"]][task["is_completed"]]["__total"] = taskCompletedCounter.get((task["created_by"], task["entity_type"], task["is_completed"]), 0)
        result["tasks"][task["created_by"]][task["entity_type"]][task["is_completed"]][task["responsible_user_id"]]["__total"] = taskUserCounter.get((task["created_by"], task["entity_type"], task["is_completed"], task["responsible_user_id"]), 0)

    return result

  def get_events(self, pipeline_id: None | int, page: int=1, limit: int=100) -> List | None:
    if limit > 100:
      raise ValueError("limit should be max 100")
    headers = self.get_headers()
    url = f"{self.config.BASE_URL}/api/v4/events"
    result = []
    params = [
      ("page", page),
      ("limit", limit),
      ("filter[pipeline_id][]", pipeline_id),
      ("filter[event_type][]", 14),
      ("filter[created_at][from]", self._serialize_date_to_timestamp(self.date_from)),
      ("filter[created_at][to]", self._serialize_date_to_timestamp(self.date_to)+86399),
    ]
    while True:
      try:
        response = requests.get(url, headers=headers, timeout=100, params=params)
        print(f"event - page {page} - status {response.status_code}")
        response.raise_for_status()
        page += 1
        events = response.json().get("_embedded", {}).get("events", [])
        if not events:
          return None
        if response.status_code == 200:
            result.extend(events)
      except requests.RequestException as e:
        return None
      params[0]=("page", page)


  def get_pipelines(self) -> Dict | None:
    headers = self.get_headers()
    url = f"{self.config.BASE_URL}/api/v4/leads/pipelines"
    response = requests.get(url, headers=headers, timeout=100)
    response.raise_for_status()
    if response.status_code == 200:
        return response.json()["_embedded"]["pipelines"]
    return None

  def get_leads(self, pipeline_id: int, page: int=1, limit: int=250) -> Dict | None:
    if limit > 250:
      raise ValueError("limit should be 250 max")
    headers = self.get_headers()
    url = f"{self.config.BASE_URL}/api/v4/leads"
    params = [
      ("page", page),
      ("limit", limit),
      ("filter[pipeline_id][]", pipeline_id),
      ("filter[created_at][from]", self._serialize_date_to_timestamp(self.date_from)),
      ("filter[created_at][to]", self._serialize_date_to_timestamp(self.date_to)+86399),
      ("with[]", "contacts"),
      ("with[]", "tags")
    ]
    if self.filter:
      for k, v in self.filter.items():
        if k == "updated_at":
          if type(self.filter[k]) != dict:
            params.append((f"filter[{k}]", v))
          else:
            for k1, v1 in self.filter[k].items():
              params.append((f"filter[updated_at][{k1}]", v1))
        elif k == "order":
          if type(self.filter[k]) != dict:
            pass
          else:
            for k1, v1 in self.filter[k].items():
              params.append((f"order[{k1}]", v1))
        elif k == "created_at":
          if type(self.filter[k]) != dict:
            params.append((f"filter[{k}]", v))
          else:
            for k1, v1 in self.filter[k].items():
              params.append((f"filter[created_at][{k1}]", v1))
        elif k == "query":
          params.append((k, v))
        elif k == "with":
          params.append(("with[]", v))
        else:
          params.append((f"filter[{k}][]", v))
    response = requests.get(url, headers=headers, timeout=100, params=params)
    print(f"leads - page {page} - status {response.status_code}")
    response.raise_for_status()
    if response.status_code == 200:
      return response.json().get("_embedded", {}).get("leads", [])
    return None
    
  def get_tasks(self, 
                page: int=1, 
                limit: int=250) -> List[Dict] | None:
    if limit > 250:
      raise ValueError("limit should be max 250")
    headers = self.get_headers()
    url = f"{self.config.BASE_URL}/api/v4/tasks"
    params = [
      ("page", page),
      ("limit", limit)
    ]
    if self.filter:
      for k, v in self.filter.items():
        if k == "updated_at":
          if type(self.filter[k]) != dict:
            params.append((f"filter[{k}]", v))
          else:
            for k1, v1 in self.filter[k].items():
              params.append((f"filter[updated_at][{k1}]", v1))
        elif k == "order":
          if type(self.filter[k]) != dict:
            pass
          else:
            for k1, v1 in self.filter[k].items():
              params.append((f"order[{k1}]", v1))
        elif k == "created_at":
          if type(self.filter[k]) != dict:
            params.append((f"filter[{k}]", v))
          else:
            for k1, v1 in self.filter[k].items():
              params.append((f"filter[created_at][{k1}]", v1))
        else:
          params.append((f"filter[{k}][]", v))
    response = requests.get(url, headers=headers, timeout=100, params=params)
    response.raise_for_status()
    if response.status_code == 200:
      return response.json().get("_embedded", {}).get("tasks", [])
    else:
      return None

  def save_pipelines_to_json(self, pipelines, filename="stages.json"):
    Path(filename).write_text(json.dumps(pipelines, indent=4, ensure_ascii=False))