from typing import TypedDict, Protocol, Literal, Union, List, Dict, NewType, Any
from dataclasses import dataclass


RESERVED_KEY_MAP = {
    "from_": "from",
    "class_": "class",
    "def_": "def",
    "return_": "return",
    "import_": "import",
    "with_": "with"
}

def serialize_dict_to_json(params: Dict[str, Any]) -> Dict[str, Any]:
  converted = {}
  for k, v in params.items():
    if type(params[k]) == dict:
      converted[new_key:=RESERVED_KEY_MAP.get(k, k)] = serialize_dict_to_json(params[k])
    else:
      converted[new_key:=RESERVED_KEY_MAP.get(k, k)] = v
  return converted



class UpdatedFilter(TypedDict):
  from_: None | int | str
  to_: None | int | str

class CreatedFilter(TypedDict):
  from_: None | int | str
  to_: None | int | str

class OrderFilter(TypedDict):
  complete_till: None | Literal["asc", "desc"]
  created_at: None | int | str
  id: None | int | list

class TaskFilter(TypedDict):
  responsible_user_id: None | int | list
  is_completed: Literal[False, True]
  type: None | str | list
  task_type: None | int | list
  entity_type: None | int | list
  entity_id: None | int | list
  task_id: None | int | list
  updated_at: None | int | UpdatedFilter
  id: None | str | list
  created_at: None | int | CreatedFilter
  created_by: None | int | list
  entity: None | str | list
  value_before: None | str | list
  value_after: None | str | list
  with_: None | str
  order: None | OrderFilter
  query: None | int | str