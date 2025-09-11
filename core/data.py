import json
from pathlib import Path
from collections import Counter
from datetime import date, datetime, timedelta
from typing import Union, List, Dict, Optional, Required, Any

from openpyxl import Workbook
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
    # self.wb: Workbook = Workbook()


  
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
      
  def _add_day(self, default: str):
    return (datetime.datetime.strptime(default, "%d.%m.%Y")+timedelta(days=1)).day


  def get_headers(self) -> Dict:
    return {
        "Content-Type": "application/json",
        "Authorization": f"{self.token_type} {self.access_token}"
    }

  @token_validate
  def update_leads(self) -> Dict:
    date_from_ = self.date_from
    date_to_ = self.date_to
    day_from, month_from, year_from = date_from_.split(".")
    day_to, month_to, year_to = date_to_.split(".")
    if int(month_to) > int(month_from):
      for month in range(int(month_from), int(month_to)+1):
        next_day = False
        while True:
          if next_day == 1:
            break
          day = next_day or int(day_from)
          AmoDataParsing({}, date_from=f"{day}.{month}.{year_from}", date_to=f"{day}.{month}.{year_from}").update_leads()
          next_day = self._add_day(date_from_)
    else:
      if int(day_to) > int(day_from):
        for day in range(int(day_from), int(day_to)+1):
          AmoDataParsing({}, date_from=f"{day}.{month_from}.{year_from}", date_to=f"{day}.{month_from}.{year_from}").update_leads()
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
      statuses = pipeline.get("_embedded", {}).get("statuses", [])

      result.get("pipeline", {})[pipeline["id"]] = {
        "name": pipeline["id"],
        "account_id": pipeline["account_id"],
        "statuses": {
          "__total": 0
        }
      }

      for status in statuses:
        result.get("pipeline", {}).get(pipeline["id"], {}).get("statuses", {})[status["id"]] = {
          "name": status.get("name", None),
          "sort": status.get("sort", None),
          "type": status.get("type", None),
          "account_id": status.get("account_id", None),
          "leads": {
            "__total": 0
          }
        }

      if leads:
        leadCounter = Counter((lead["status_id"], lead["pipeline_id"]) for lead in leads)
        leadPipelineCounter = Counter(lead["pipeline_id"] for lead in leads)
        for status in statuses:
          result.get("pipeline", {}).get(pipeline["id"], {}).get("statuses", {})["__total"] = leadPipelineCounter.get(status["pipeline_id"], 0)
          result.get("pipeline", {}).get(pipeline["id"], {}).get("statuses", {}).get(status["id"], {}).get("leads", {})["__total"] = leadCounter.get((status["id"], status["pipeline_id"]), 0)
        for lead in leads:
          result.get("pipeline", {}).get(pipeline["id"], {}).get("statuses", {}).get(lead["status_id"], {}).get("leads", {})[lead["id"]] = lead["name"]

      if leads:
        leadPipelineCounter = Counter(lead["pipeline_id"] for lead in leads)
        leadUserCounter = Counter((lead["pipeline_id"], lead["responsible_user_id"]) for lead in leads)
        leadStatusCounter = Counter((lead["pipeline_id"], lead["responsible_user_id"], lead["status_id"]) for lead in leads)
        for lead in leads:
          result.get("leads", {}).setdefault(lead["pipeline_id"], {})["__total"] = leadPipelineCounter.get(lead["pipeline_id"], 0)
          result.get("leads", {}).setdefault(lead["pipeline_id"], {}).setdefault(lead["responsible_user_id"], {})["__total"] = leadUserCounter.get((lead["pipeline_id"], lead["responsible_user_id"]), 0)
          result.get("leads", {}).setdefault(lead["pipeline_id"], {}).setdefault(lead["responsible_user_id"], {}).setdefault(lead["status_id"], {})["__total"] = leadStatusCounter.get((lead["pipeline_id"], lead["responsible_user_id"], lead["status_id"]), 0)
          result.get("leads", {}).get(lead["pipeline_id"], {}).get(lead["responsible_user_id"], {}).get(lead["status_id"], {})[lead["id"]] = {
            "name": lead["name"],
            "price": lead["price"],
            "group_id": lead["group_id"],
            "is_deleted": lead["is_deleted"],
            "score": lead["score"],
            "created_by": lead["created_by"],
            "custom_fields_values": lead["custom_fields_values"]
          }
      
      if events:
        eventCounter = Counter((event["type"], event["entity_type"], event["created_by"]) for event in events)
        for event in events:
          result.get("events", {}).setdefault(event["created_by"], {}).setdefault(event["entity_type"], {}).setdefault(event["type"], {})[event["id"]] = {
              "entity_id": event["entity_id"],
              "created_by": event["created_by"],
              "account_id": event["account_id"]
          }
          result.get("events", {}).setdefault(event["created_by"], {}).setdefault(event["entity_type"], {})[event["type"]]["__total"] = eventCounter[(event["type"], event["entity_type"], event["created_by"])]

    if tasks:
      taskCounter = Counter(task["created_by"] for task in tasks)
      taskTypeCounter = Counter((task["created_by"], task["entity_type"]) for task in tasks)
      taskCompletedCounter = Counter((task["created_by"], task["entity_type"], task["is_completed"]) for task in tasks)
      taskUserCounter = Counter((task["created_by"], task["entity_type"], task["is_completed"], task["responsible_user_id"]) for task in tasks)
      for task in tasks:
        result.get("tasks", {}).setdefault(task["created_by"], {})["__total"] = taskCounter.get(task["created_by"], 0)
        result.get("tasks", {}).setdefault(task["created_by"], {}).setdefault(task["entity_type"], {})["__total"] = taskTypeCounter.get((task["created_by"], task["entity_type"]), 0)
        result.get("tasks", {}).setdefault(task["created_by"], {}).setdefault(task["entity_type"], {}).setdefault(task["is_completed"], {})["__total"] = taskCompletedCounter.get((task["created_by"], task["entity_type"], task["is_completed"]), 0)
        result.get("tasks", {}).setdefault(task["created_by"], {}).setdefault(task["entity_type"], {}).setdefault(task["is_completed"], {}).setdefault(task["responsible_user_id"], {})["__total"] = taskUserCounter.get((task["created_by"], task["entity_type"], task["is_completed"], task["responsible_user_id"]), 0)
        result.get("tasks", {}).get(task["created_by"], {}).get(task["entity_type"], {}).get(task["is_completed"], {}).get(task["responsible_user_id"], {})[task["id"]] = {
          "text": task["text"],
          "result": task["result"],
          "complete_till": task["complete_till"]
        }

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