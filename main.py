from config.config import Config
from middleware import token_validate
from core.data import AmoDataParsing



@token_validate
def main():
    config = Config()
    config.reload()
    data_parser = AmoDataParsing({}, date_from="7.9.2025", date_to="7.9.2025")
    leads = data_parser.update_leads()
    if leads:
        data_parser.save_pipelines_to_json(leads)


if __name__ == "__main__":
  main()