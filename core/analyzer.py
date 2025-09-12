from collections import Counter
import json
from pathlib import Path
from urllib.parse import urlparse, unquote_plus, parse_qsl


class ExtractParams:

  def __init__(self, uri: str = None) -> None:
    self.uri = uri


  def analyze(self, uri: str = None) -> list[tuple[str, str]]:
    if uri:
      self.uri = uri
    params = parse_qsl(unquote_plus(urlparse(self.uri).query))
    frag = parse_qsl(unquote_plus(urlparse(self.uri).fragment))
    params.extend(frag)
    result: list = []
    for item in params:
      if "[" in item[0]:
        result.append(item)
    return result
  

class ExtractData:

  def __init__(self) -> None:
    pass

  # def _deep_find(self, data, key) -> None | any:
  #   if isinstance(data, dict):
  #     for k, v in data.items():
  #       if k == key:
  #         yield v
  #       if isinstance(v, (dict, list)):
  #         yield from self._deep_find(v, key)
  #   elif isinstance(data, list):
  #     for item in data:
  #       yield from self._deep_find(data, key)


  def filter_and_get_total_count(self, date: str, params: list[tuple[str, str]], filename: str="stages.json") -> int:
    content = json.loads(Path(filename).read_text(encoding="utf-8"))
    params_key = params[0][1]
    params_filter = params[1::]
    crmcontent = content[date][params_key]["items"]
    # keys= [k for k,v in [item for item in params_filter]]
    # values = [v for k,v in [item for item in params_filter]]
    count = 0
    for crmitem in crmcontent:
      for key, value in params_filter[::]:
        if key == "end":
          count += 1
          break
        if crmitem[key] not in value:
          break
    return count


