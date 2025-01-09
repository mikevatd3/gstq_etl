import click
import pandas as pd
from pandera.errors import SchemaError, SchemaErrors
import tomli

from great_start_to_quality import setup_logging, db_engine, metadata_engine
from great_start_to_quality.schema import Providers
from metadata_audit.capture import record_metadata
from sqlalchemy.orm import sessionmaker

logger = setup_logging()

table_name = "providers"

with open("metadata.toml", "rb") as md:
    metadata = tomli.load(md)


# Every loader script starts with a pydantic model -- This is both to
# validate the clean-up process output and to ensure that fields agree
# with the metadata provided to the metadata system.
@click.command()
@click.argument("edition_date")
def main(edition_date):
    edition = metadata["tables"][table_name]["editions"][edition_date]

    
    result = (pd.read_excel(edition["raw_path"]))

    print(result.head())

    raise Exception("Checkpoint.")

    logger.info(f"Cleaning {table_name} was successful validating schema.")

    # Validate
    try:
        validated = Providers.validate(result)
        logger.info(
            f"Validating {table_name} was successful. Recording metadata."
        )
    except SchemaError | SchemaErrors as e:
        logger.error(f"Validating {table_name} failed.", e)

    with metadata_engine.connect() as db:
        logger.info("Connected to metadata schema.")

        record_metadata(
            Providers,
            __file__,
            table_name,
            metadata,
            edition_date,
            result,
            sessionmaker(bind=db)(),
            logger,
        )

        db.commit()
        logger.info("successfully recorded metadata")

    with db_engine.connect() as db:
        logger.info("Metadata recorded, pushing data to db.")

        validated.to_sql(  # type: ignore
            table_name, db, index=False, schema="great_start_to_quality", if_exists="replace"
        )


if __name__ == "__main__":
    main()
