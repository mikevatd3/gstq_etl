import click
import pandas as pd
from pandera.errors import SchemaError, SchemaErrors
import tomli

from great_start_to_quality import setup_logging, db_engine, metadata_engine, yes_no_to_bool
from great_start_to_quality.schema import Providers
from great_start_to_quality.reference import FIELD_RENAME, FIELD_NAME_UPDATE
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

    
    yes_noes_to_bools = [
        'cooperative',
        'faith_based',
        'montessori',
        'reggio_inspired',
        'preschool',
        'strong_beginnings',
        'gsrp',
        'early_head_start',
        'head_start',
        'nature_based',
        'school_age'
    ]

    result = (
        pd.read_excel(edition["raw_path"])
        .rename(columns=lambda col: col.strip())
        .rename(columns=FIELD_NAME_UPDATE)
        .rename(columns=FIELD_RENAME) # Review 'reference.py' for details
        .rename(columns={col: f"__{col}" for col in yes_noes_to_bools}) # These are temp col names to make room for assigns
        .assign(
            **{
                col: lambda df: df[f"__{col}"].apply(yes_no_to_bool)
                for col in yes_noes_to_bools
            },
            date=edition["start"],
        )
        .drop([f"__{col}" for col in yes_noes_to_bools], axis=1)
        .drop(["referral_status_note"], axis=1)
        .drop(7102, axis=0)
    )

    logger.info(f"Cleaning {table_name} was successful validating schema.")

    # Validate
    try:
        validated = Providers.validate(result)
        logger.info(
            f"Validating {table_name} was successful. Recording metadata."
        )
    except (SchemaError, SchemaErrors) as e:
        logger.error(f"Validating {table_name} failed.", e)
        return 

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
        logger.info("Metadata recorded, pushing data to db.")

    with db_engine.connect() as db:

        validated.to_sql(  # type: ignore
            table_name, db, index=False, schema="childcare", if_exists="append"
        )


if __name__ == "__main__":
    main()
