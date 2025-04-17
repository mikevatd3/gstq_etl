from pathlib import Path
import pandas as pd


WORKING_DIR = Path(__file__).parent


def transform_gstq(logger):
    logger.info("Transforming all instances of GSTQ data")

    data_sources = pd.read_csv(WORKING_DIR / "conf" / "sources.csv")

    for _, source in data_sources.iterrows():
        logger.info(f"Transforming data for {source['start_date']}.")

        try:
            file = pd.read_csv(source["source_file"])

        except FileNotFoundError:
            logger.error(f"File not found for {source['start_date']}")
            continue
