import json
from pathlib import Path
from collections import Counter
from datetime import date, datetime, timedelta
from typing import Literal
from urllib import request

from openpyxl import Workbook
import requests

from config.config import Config
from core import serialize_dict_to_json, TaskFilter
from middleware import token_validate


class AmoDataParsing:

  __EVENTS: list[str] = [
    "id",
    "created_at",
    "created_by",
    "entity",
    "entity_id",
    "type",
    "value_before",
    "value_after"
  ]

  __LEADS: list[str] = [
    "with",
    "query",
    "order",
    "id",
    "name",
    "price",
    "statuses",
    "pipeline_id",
    "created_by",
    "updated_by",
    "responsible_user_id",
    "created_at",
    "updated_at",
    "closed_at",
    "closest_task_at",
    "custom_fields_values"
  ]

  __TASKS: list[str] = [
    "task_type",
    "is_completed",
    "entity_type",
    "entity_id",
    "id",
    "responsible_user_id",
    "updated_at",
    "order",
  ]

  def __init__(self, 
               filter: TaskFilter,
               date_from: str = date.today().strftime("%d.%m.%Y"), 
               date_to: str = date.today().strftime("%d.%m.%Y")
               ):
    self.config: Config = Config()
    self.config.reload()
    self.access_token: str = self.config.TOKEN_DICT.get("access_token")
    self.token_type: str = self.config.TOKEN_DICT.get("token_type")
    self.filter: dict[str, any] = serialize_dict_to_json(filter)
    self.date_from: str = date_from
    self.date_to: str = date_to
    self.wb: Workbook = Workbook()


  def _add_params(self, params: list[tuple[str, any]], params_type: Literal["event", "lead", "task"]) -> list[tuple[str, any]]:
    get_params_type: dict[str, list[str]] = {
      "event": self.__EVENTS,
      "lead": self.__LEADS,
      "task": self.__TASKS
    }
    if self.filter:
      for k, v in self.filter.items():
        if k in get_params_type[params_type]:
          if k in ["updated_at", "created_at", "closed_at", "closest_task_at"]:
            if type(self.filter[k]) != dict:
              params.append((f"filter[{k}]", v))
            else:
              for k1, v1 in self.filter[k].items():
                params.append((f"filter[{k}][{k1}]", self._serialize_date_to_timestamp(None, from_=v1, to_=v1).get(k1, 0)))
          elif k == "order":
            if type(self.filter[k]) != dict:
              pass
            else:
              for k1, v1 in self.filter[k].items():
                params.append((f"order[{k1}]", v1))
          elif k == "query":
            params.append((k, v))
          elif k == "with":
            params.append(("with[]", v))
          else:
            params.append((f"filter[{k}][]", v))
    return params


  
  def _serialize_date_to_timestamp(self, default: None | str, from_: None | str = None, to_: None | str = None) -> int | dict[str, int] | None:
    if default:
      return int(datetime.strptime(default, "%d.%m.%Y").timestamp())
    else:
      if all((from_, to_)):
        return {
          "from": int(datetime.strptime(from_, "%d.%m.%Y").timestamp()),
          "to": int(datetime.strptime(to_, "%d.%m.%Y").timestamp())+86399
        }
      else:
        return None

  def _serialize_timestamp_to_date(self, default: None | int, from_: None | int = None, to_: None | int = None) -> str | dict[str, str] | None:
    if default:
      return datetime.fromtimestamp(int(default)).strftime("%d.%m.%Y")
    else:
      if all((from_, to_)):
        return {
          "from": datetime.fromtimestamp(int(from_)).strftime("%d.%m.%Y"),
          "to": datetime.fromtimestamp(int(to_)).strftime("%d.%m.%Y")
        }
      else:
        return None
      
  def _add_day(self, default: str) -> int:
    return (datetime.strptime(default, "%d.%m.%Y")+timedelta(days=1)).day


  def get_headers(self) -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "Authorization": f"{self.token_type} {self.access_token}"
    }

  @token_validate
  def update_info(self) -> dict[str, any]:
    global_result = {}
    date_from_: str = self.date_from
    date_to_: str = self.date_to
    day_from,  month_from, year_from = date_from_.split(".")
    day_to, month_to, year_to = date_to_.split(".")
    if int(month_to) > int(month_from):
      for month in range(int(month_from), int(month_to)+1):
        next_day = False
        while True:
          if next_day == 1:
            break
          day = next_day or int(day_from)
          temp_result = AmoDataParsing({}, date_from=f"{day}.{month}.{year_from}", date_to=f"{day}.{month}.{year_from}").update_info()
          global_result[f"{day}.{month}.{year_from}"] = temp_result[f"{day}.{month}.{year_from}"]
          next_day = self._add_day(date_from_)
    else:
      if int(day_to) > int(day_from):
        for day in range(int(day_from), int(day_to)+1):
          temp_result = AmoDataParsing({}, date_from=f"{day}.{month_from}.{year_from}", date_to=f"{day}.{month_from}.{year_from}").update_info()
          global_result[f"{day}.{month_from}.{year_from}"] = temp_result[f"{day}.{month_from}.{year_from}"]
    result: dict[str, any] = {}
    pipelines: list[dict[str, any]] | None = self.get_pipelines()
    tasks: list[dict[str, any]] | list = self.get_tasks()
    events: list[dict[str, any]] | list = self.get_events()
    leads: list[dict[str, any]] | list = self.get_leads()
    result.setdefault("pipelines", {})
    result.get("pipelines", {}).setdefault("__total", {})["pipelines"] = len(pipelines)
    result.get("pipelines", {}).setdefault("items", [])
    result.setdefault("events", {})
    result.get("events", {}).setdefault("__total", {})["events"] = len(events)
    result.get("events", {}).setdefault("items", [])
    result.setdefault("leads", {})
    result.get("leads", {}).setdefault("__total", {})["leads"] = len(leads)
    result.get("leads", {}).setdefault("items", [])
    result.setdefault("tasks", {})
    result.get("tasks", {}).setdefault("__total", {})["tasks"] = len(tasks)
    result.get("tasks", {}).setdefault("items", [])
    if pipelines:
      for pipeline in pipelines:
        result.get("pipelines", {})["items"].append(pipeline)
        statuses = pipeline.get("_embedded", {}).get("statuses", [])

        if statuses:
          result.get("pipelines", {}).get("__total", {}).setdefault("statuses", {})[pipeline["id"]] = len(statuses)

    if leads:
      for lead in leads:
        result.get("leads", {})["items"].append(lead)
      
    if events:
      for event in events:
        result.get("events", {})["items"].append(event)

    if tasks:
      for task in tasks:
        result.get("tasks", {}).get("items", []).append(task)
    
    global_result[self.date_from] = result

    return global_result

  def get_events(self, page: int = 1, limit: int = 100) -> list[dict[str, any]] | list:
    if limit > 100:
      raise ValueError("limit should be max 100")
    headers = self.get_headers()
    url = f"{self.config.BASE_URL}/api/v4/events"
    result = []
    params = [
      ("page", page),
      ("limit", limit),
      ("filter[event_type][]", 14),
      ("filter[created_at][from]", self._serialize_date_to_timestamp(self.date_from)),
      ("filter[created_at][to]", int(self._serialize_date_to_timestamp(self.date_to)+86399)),
    ]
    params = self._add_params(params, "event")
    while True:
      try:
        response = requests.get(url, headers=headers, timeout=100, params=params)
        response.raise_for_status()
        page += 1
        params[0]=("page", page)
        events = response.json().get("_embedded", {}).get("events", [])
        if not events:
          break
        if response.status_code == 200:
            result.extend(events)
      except requests.RequestException as e:
        break
    return result


  def get_pipelines(self) -> list[dict[str, any]] | None:
    headers = self.get_headers()
    url = f"{self.config.BASE_URL}/api/v4/leads/pipelines"
    response = requests.get(url, headers=headers, timeout=100)
    response.raise_for_status()
    if response.status_code == 200:
        return response.json()["_embedded"]["pipelines"]
    return None

  def get_leads(self, page: int = 1, limit: int = 250) -> list[dict[str, any]] | list:
    if limit > 250:
      raise ValueError("limit should be 250 max")
    result = []
    headers = self.get_headers()
    url = f"{self.config.BASE_URL}/api/v4/leads"
    params = [
      ("page", page),
      ("limit", limit),
      ("filter[created_at][from]", self._serialize_date_to_timestamp(self.date_from)),
      ("filter[created_at][to]", self._serialize_date_to_timestamp(self.date_to)+86399),
      ("with[]", "contacts"),
      ("with[]", "tags")
    ]
    params = self._add_params(params, "lead")
    while True:
      try:
        response = requests.get(url, headers=headers, timeout=100, params=params)
        response.raise_for_status()
        leads =  response.json().get("_embedded", {}).get("leads", [])
        if not leads:
          break
        page += 1
        params[0] = ("page", page)
        if response.status_code == 200:
          result.extend(leads)
      except requests.RequestException:
        break
    return result
    
  def get_tasks(self, page: int = 1, limit: int = 250) -> list[dict[str, any]] | list:
    if limit > 250:
      raise ValueError("limit should be max 250")
    result = []
    headers = self.get_headers()
    url = f"{self.config.BASE_URL}/api/v4/tasks"
    params = [
      ("page", page),
      ("limit", limit)
    ]
    params = self._add_params(params, "task")
    while True:
      try:
        response = requests.get(url, headers=headers, timeout=100, params=params)
        response.raise_for_status()
        page += 1
        params[0] = ("page", page)
        task = response.json().get("_embedded", {}).get("tasks", [])
        if not task:
          break
        if response.status_code == 200:
          result.extend(task)
      except requests.RequestException:
        break
    return result

  def save_info_to_json(self, pipelines: dict[str, any], filename="stages.json") -> None:
    Path(filename).write_text(json.dumps(pipelines, indent=4, ensure_ascii=False))

  def save_info_to_excel(self, info: dict[str, any], filename="crminfo.xlsx") -> None:
    pass
    # ws = self.wb.active
    # ws.append(list(info.keys()))