from typing import TypedDict, Literal

RESERVED_KEY_MAP: dict[str, str] = {
    "from_": "from",
    "class_": "class",
    "def_": "def",
    "return_": "return",
    "import_": "import",
    "with_": "with"
}

def serialize_dict_to_json(params) -> dict[str, any]:
  converted: dict = {}
  for k, v in params.items():
    if type(params[k]) == dict:
      converted[new_key:=RESERVED_KEY_MAP.get(k, k)] = serialize_dict_to_json(params[k])
    else:
      converted[new_key:=RESERVED_KEY_MAP.get(k, k)] = v
  return converted


class DateFilter(TypedDict):
  from_: None | int | str
  to_: None | int | str

class OrderFilter(TypedDict):
  complete_till: None | Literal["asc", "desc"]
  created_at: None | Literal["asc", "desc"]
  updated_at: None | Literal["asc", "desc"]
  id: None | Literal["asc", "desc"]

class TaskFilter(TypedDict):
  responsible_user_id: None | int | list
  is_completed: Literal[False, True]
  type: None | str | list
  task_type: None | int | list
  entity_type: None | int | list
  entity_id: None | int | list
  task_id: None | int | list
  updated_at: None | int | DateFilter
  id: None | str | list
  created_at: None | int | DateFilter
  created_by: None | int | list
  entity: None | str | list
  value_before: None | str | list
  value_after: None | str | list
  with_: None | str
  order: None | OrderFilter
  query: None | int | str
  pipeline_id: None | int | str
  price: None | int
  name: None | str
  statuses: None | int | list
  closed_at: None | int | DateFilter
  closest_task_at: None | int | DateFilter