from datetime import datetime, date, timedelta
import os
from pathlib import Path

from dotenv import load_dotenv

from config.config import Config
from middleware import token_validate
from core.data import AmoDataParsing
from core.analyzer import ExtractParams, ExtractData
from core.dbdriver import DB

load_dotenv()

dbinfo = DB()

uri = []

_urls = Path(os.getenv("URLS_FILE", "urls.txt")).read_text(encoding="utf-8").splitlines()

for item in _urls:
  uri.append(item)

cell_filter = []

get_params = ExtractParams()

for item in uri:
  item_params = get_params.analyze(item)
  cell_filter.append(item_params)

@token_validate
def main():
    config = Config()
    config.reload()
    get_data = ExtractData()
    date_from = "28.8.2025"
    date_to = "28.8.2025"
    date_from_range = datetime.strptime(date_from, "%d.%m.%Y").date()
    date_to_range = datetime.strptime(date_to, "%d.%m.%Y").date()
    delta = date_to_range - date_from_range
    data_parser = AmoDataParsing({}, date_from=date_from, date_to=date_to)
    leads = data_parser.update_info()
    if leads:
      data_parser.save_info_to_json(leads)
    excel_data = {}
    for i in range(delta.days + 1):
      date_key = date_from_range + timedelta(days=i)
      date_string = date_key.strftime("%-d.%-m.%Y")
      excel_data[date_string] = []
      for item in cell_filter:
        if item is None:
          excel_data[date_string].append(None)
        else:
          total = get_data.filter_and_get_total_count(date_string, item)
          excel_data[date_string].append(total)
    data_parser.save_info_to_excel(excel_data, uri)



if __name__ == "__main__":
  main()