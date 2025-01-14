from pathlib import Path
from itertools import islice
import json
import logging
import logging.config
from sqlalchemy import create_engine
import tomli


with open(Path().cwd() / "config.toml", "rb") as f:
    config = tomli.load(f)


db_engine = create_engine(
    f"postgresql+psycopg2://{config['db']['user']}:{config['db']['password']}"
    f"@{config['db']['host']}:{config['db']['port']}/{config['db']['name']}",
    connect_args={'options': f'-csearch_path={config["app"]["name"]}'},
)

metadata_engine = create_engine(
    f"postgresql+psycopg2://{config['db']['user']}:{config['db']['password']}"
    f"@{config['db']['host']}:{config['db']['port']}/{config['db']['name']}",
    connect_args={'options': f'-csearch_path={config["db"]["metadata_schema"]}'},
)


def setup_logging():
    with open(Path.cwd() / "logging_config.json") as f:
        logging_config = json.load(f)

    logging.config.dictConfig(logging_config)

    return logging.getLogger(config["app"]["name"])


def yes_no_to_bool(yes_no):
    """
    Some datasets have Yes and No instead of booleans -- this fixes that.
    """
    if yes_no == "Yes":
        return True
    elif yes_no == "No":
        return False
    raise ValueError(f"{yes_no} is not 'Yes' or 'No.'")


def text_to_months(text):
    years, _, months, _ = text.split()

    return int(years) * 12 + int(months)


if __name__ == "__main__":
    print(text_to_months("0 years 0 months"))