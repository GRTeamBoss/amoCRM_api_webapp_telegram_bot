import json
from pathlib import Path
from urllib.parse import urlparse, unquote_plus, parse_qs

from core import EVENTS_TYPES


class ExtractParams:

  SERIALIZE_KEY_URI_TO_FILTER_KEY = {
    "pipe": "status_id",
    "pipe_id": "pipeline_id",
    "main_user": "created_by",
    "event_type": "type",
    "status_lead": "lead_status",
    "entity": "entity_type",
    "task_type": "task_type_id",
    "filter_date_switch": "is_completed"
  }

  SERIALIZE_VALUE_URI_TO_FILTER_VALUE = {
    "closed": "True",
    "created": "False"
  }

  def __init__(self, uri: str = None) -> None:
    self.uri = uri


  def analyze(self, uri: str = None) -> list[tuple[str, str]]:

    def _get_serialize_key(params: dict[str, list[str]] | list, param_key: str):
      result = []
      if isinstance(params, dict):
        for k, v in params.items():
          if "filter[" in k:
            if param_key in ["tasks", "leads"]:
              k =k.replace("main_user", "responsible_user_id")
            k_subkey= k.replace("]", "").rstrip().split("[")[1::]
            k_subkey= [x for x in k_subkey if x != ""]
            k_new = _get_serialize_key(k_subkey, param_key)
            if k_new[0] == "type":
              v_new = []
              for v_item in v:
                v_new.extend( x.get("key", v[0]) for x in EVENTS_TYPES if x.get("type", -1) == int(v_item))
              result.append((k_new, v_new))
            elif k_new[0] == "entity_type":
              v_new = []
              for v_item in v:
                v_new.extend(x.get("key", v[0]).split("_")[0] for x in EVENTS_TYPES if x.get("type", -1) == int(v_item))
              result.append((k_new, v_new))
            elif k_new.count("value_before") == 1:
              _index = k_new.index("value_before")
              k_new.insert(_index+1, int(0))
              if k_new.count("statuses") == 1:
                k_new.pop(_index+2)
                k_new.pop(_index+2)
              if k_new.count("lead_status") == 1:
                slp_list = set()
                sls_list = set()
                slp_key = []
                sls_key = []
                slp_key.extend(k_new)
                slp_key.append("pipeline_id")
                sls_key.extend( k_new)
                sls_key.append("id")
                for v_item in v:
                  if ":" in v_item:
                    status_lead_pipeline = v_item.split(":")[0]
                    status_lead_status = v_item.split(":")[1]
                    slp_list.add(status_lead_pipeline)
                    sls_list.add(status_lead_status)
                result.append((slp_key, list(slp_list)))
                result.append((sls_key, list(sls_list)))
            elif k_new.count("value_after") == 1:
              _index = k_new.index("value_after")
              k_new.insert(_index+1, int(0))
              if k_new.count("statuses") == 1:
                k_new.pop(_index+2)
                k_new.pop(_index+2)
              if k_new.count("lead_status") == 1:
                slp_list = set()
                sls_list = set()
                slp_key = []
                sls_key = []
                slp_key.extend(k_new)
                slp_key.append("pipeline_id")
                sls_key.extend( k_new)
                sls_key.append("id")
                for v_item in v:
                  if ":" in v_item:
                    status_lead_pipeline = v_item.split(":")[0]
                    status_lead_status = v_item.split(":")[1]
                    slp_list.add(status_lead_pipeline)
                    sls_list.add(status_lead_status)
                result.append((slp_key, list(slp_list)))
                result.append((sls_key, list(sls_list)))
            else:
              result.append((k_new, v))
          else:
            if k == "filter_date_switch":
              if param_key == "tasks":
                k_new = self.SERIALIZE_KEY_URI_TO_FILTER_KEY.get(k, k)
                v_new = self.SERIALIZE_VALUE_URI_TO_FILTER_VALUE.get(v[0], v[0])
                result.append(([k_new], [v_new]))
      if isinstance(params, list):
        new_params = []
        for item in params:
          new_params.append(self.SERIALIZE_KEY_URI_TO_FILTER_KEY.get(item, item))
        return new_params
      return result
    
    if uri:
      if uri == "Skip":
        return None
      self.uri = uri
    path = unquote_plus(urlparse(self.uri).path)
    path_key = path.split("/")[1]
    if path_key == "todo":
      path_key = "tasks"
    path_pipeline_id = path.split("pipeline/")[1].split("/")[0] if "pipeline" in path else None
    params = parse_qs(unquote_plus(urlparse(self.uri).query))
    frag = parse_qs(unquote_plus(urlparse(self.uri).fragment))
    params.update(frag)
    result: list = []
    result.append(("key", path_key))
    if path_pipeline_id:
      result.append(("pipeline_id", [path_pipeline_id]))
    params_serialize = _get_serialize_key(params, path_key)
    result.extend(params_serialize)
    result.append(("end", [""]))
    return result
  

class ExtractData:

  def __init__(self) -> None:
    pass

  def filter_and_get_total_count(self, date: str, params: list[tuple[str, str]], filename: str="stages.json") -> int:
    def _value_exist(crmitem: dict[str, any], key: list | str, value: list):
      crm_value = False
      if isinstance(crmitem, dict):
        if isinstance(key, list):
          if len(key) == 0:
            return str(crmitem) in value
          else:
            crm_value = _value_exist(crmitem.get(key[0], None), key[1::], value)
        elif isinstance(key, str):
          crm_value = _value_exist(crmitem.get(key, None), [], value)
      elif isinstance(crmitem, list):
        crm_value = _value_exist(crmitem[int(key[0])], key[1::], value)
      elif isinstance(crmitem, (str, int, bool)):
        return str(crmitem) in value
      return crm_value

    content = json.loads(Path(filename).read_text(encoding="utf-8"))
    params_key = params[0][1]
    params_filter = params[1::]
    crmcontent = content[date][params_key]["items"]
    ids = set()
    for crmitem in crmcontent:
      for key, value in params_filter[::]:
        if key == "end":
          ids.add(crmitem["id"])
          break
        else:
          if _value_exist(crmitem, key, value) == False:
            break
    return len(ids)


