from pathlib import Path
from itertools import islice
import json
import logging
import logging.config
from sqlalchemy import create_engine
import tomli



metadata_engine = create_engine(
    f"postgresql+psycopg2://{config['db']['user']}:{config['db']['password']}"
    f"@{config['db']['host']}:{config['db']['port']}/{config['db']['name']}",
    connect_args={'options': f'-csearch_path={config["db"]["metadata_schema"]},public'},
)


def setup_logging():
    with open(Path.cwd() / "logging_config.json") as f:
        logging_config = json.load(f)

    logging.config.dictConfig(logging_config)

    return logging.getLogger(config["app"]["name"])




if __name__ == "__main__":
    print(text_to_months("0 years 0 months"))