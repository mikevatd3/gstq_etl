from pathlib import Path
import pandas as pd
import geopandas as gpd
from sqlalchemy import create_engine
import tomllib

WORKING_DIR = Path(__file__).parent


with open(WORKING_DIR.parent / "config.toml", "rb") as f:
    config = tomllib.load(f)


db_engine = create_engine(
    f"postgresql+psycopg://{config['db']['user']}:{config['db']['password']}"
    f"@{config['db']['host']}:{config['db']['port']}/{config['db']['name']}",
    connect_args={'options': f'-csearch_path={config["app"]["name"]},public'},
)


def load_gstq():
    print("Loading childcare into the database.")
    file = pd.read_csv(WORKING_DIR / "output" / "all_childcare.csv")

    file.to_sql(
        "providers", db_engine, schema="childcare", if_exists="replace", index=False
    )


    # print("Loading geocoded file into the database.")
    # file = gpd.read_file(WORKING_DIR / "output" / "geocoded_providers.geojson")

    # file.to_postgis(
        # "providers_geo", db_engine, schema="childcare", if_exists="replace", index=False
    # )


if __name__ == "__main__":
    load_gstq()