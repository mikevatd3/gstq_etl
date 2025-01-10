import click
import pandas as pd
from pandera.errors import SchemaError, SchemaErrors
import tomli

from great_start_to_quality import setup_logging, db_engine, metadata_engine, yes_no_to_bool, text_to_months
from great_start_to_quality.schema import Providers
from great_start_to_quality.reference import FIELD_RENAME
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
@click.option("-m", "--metadata_only", is_flag=True, help="Skip uploading dataset.")
def main(edition_date, metadata_only):
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
        'school_age',
        'nature_based',
    ]


    to_convert_to_months = [
        'accepts_from_mos',
        'accepts_to_mos',
        'licensed_from_mos',
        'licensed_to_mos',
    ]


    result = (
        pd.read_excel(edition["raw_path"])
        .rename(columns=lambda col: col.strip())
        .rename(columns=FIELD_RENAME) # Review 'reference.py' for details
        .rename(columns={col: f"__{col}" for col in yes_noes_to_bools + to_convert_to_months}) # These are temp col names to make room for assigns
        .assign(
            **{
                col: lambda df: df[f"__{col}"].apply(yes_no_to_bool)
                for col in yes_noes_to_bools
            },
            **{
                col: lambda df: df[f"__{col}"].apply(text_to_months)
                for col in to_convert_to_months
            },
            date=edition["start"],
        )
        .drop([f"__{col}" for col in yes_noes_to_bools + to_convert_to_months], axis=1)
        .drop(["referral_status_note"], axis=1)
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

    if not metadata_only:
        with db_engine.connect() as db:
            logger.info("Metadata recorded, pushing data to db.")

            validated.to_sql(  # type: ignore
                table_name, db, index=False, schema="childcare", if_exists="append"
            )
    else:
        logger.info("Metadata only specified, so process complete.")


if __name__ == "__main__":
    main()
