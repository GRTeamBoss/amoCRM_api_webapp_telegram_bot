from datetime import datetime, date, timedelta

from config.config import Config
from middleware import token_validate
from core.data import AmoDataParsing
from core.analyzer import ExtractParams, ExtractData


URI = [
   "https://cspacesales.amocrm.ru/leads/pipeline/9695630/?filter%5Bpipe%5D%5B9695630%5D%5B%5D=77295806&filter%5Bpipe%5D%5B9695630%5D%5B%5D=77295810&filter%5Bpipe%5D%5B9695630%5D%5B%5D=77295814&filter%5Bpipe%5D%5B9695630%5D%5B%5D=77295818&filter%5Bpipe%5D%5B9695630%5D%5B%5D=77295842&filter_date_from=11.08.2025&filter_date_to=11.08.2025&useFilter=y"
]

CELL_FILTER = [
  [
   ("key", "leads"),
   ("pipeline_id", [9695630]),
   ("status_id", [77295806, 77295810, 77295814, 77295818, 77295842]),
   ("end", [""])
  ]
]

@token_validate
def main():
    config = Config()
    config.reload()
    get_data = ExtractData()
    date_from = "21.8.2025"
    date_to = "21.8.2025"
    date_from_range = datetime.strptime(date_from, "%d.%m.%Y").date()
    date_to_range = datetime.strptime(date_to, "%d.%m.%Y").date()
    delta = date_to_range - date_from_range
    data_parser = AmoDataParsing({}, date_from=date_from, date_to=date_to)
    leads = data_parser.update_info()
    if leads:
      data_parser.save_info_to_json(leads)
    for i in range(delta.days + 1):
      date_key = date_from_range + timedelta(days=i)
      date_string = date_key.strftime("%-d.%-m.%Y")
      for item in CELL_FILTER:
        print(get_data.filter_and_get_total_count(date_string, item))



if __name__ == "__main__":
  main()