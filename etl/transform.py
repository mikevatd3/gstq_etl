import json
from pathlib import Path
import pandas as pd


WORKING_DIR = Path(__file__).parent


def yes_no_to_bool(yes_no):
    """
    Some datasets have Yes and No instead of booleans -- this fixes that.
    """
    if yes_no == "Yes":
        return True
    elif yes_no == "No":
        return False
    return None


def text_to_months(text):
    years, _, months, _ = text.split()

    return int(years) * 12 + int(months)


def recode_value(val, mapping):
    """
    Tries to recode from the provided mapping, otherwise returns the
    value unchanged.
    """

    return mapping.get(val, val)


def transform_gstq():
    print("Transforming all instances of GSTQ data")

    output_path = WORKING_DIR / "output" / "all_childcare.csv"

    if output_path.exists():
        print(f"File already exists at {str(output_path)}. Delete it to rerun transform")
        return 

    data_sources = pd.read_csv(WORKING_DIR / "conf" / "sources.csv")

    result = []
    for _, source in data_sources.iterrows():
        print(f"Transforming data for {source['start_date']}.")

        try:
            if (filename := Path(source["source_file"])).suffix == ".xlsx":
                file = pd.read_excel(filename, sheet_name=source["sheet_name"])
            else:
                file = pd.read_csv(filename)
            print(f"Length of childcare file {len(file)}")
        
        except FileNotFoundError:
            print(f"Source file not found for {source['start_date']}")
            continue

        try:
            field_reference = json.loads(
                (WORKING_DIR / "conf" / source["field_reference_file"])
                .read_text()
            )

        except FileNotFoundError:
            print(f"Field reference not found for {source['start_date']}")
            continue

        yes_noes_to_bools = field_reference.get("yes_noes_to_bools", [])
        to_convert_to_months = field_reference.get("to_convert_to_months", [])

        renamed = (
            file
            .rename(columns=field_reference["renames"])
            .rename(
                columns={
                    col: f"__{col}" 
                    for col in  yes_noes_to_bools + to_convert_to_months
                }
            ) # These are temp col names to make room for assigns
            .assign(
                **{
                    col: lambda df, col=col: df[f"__{col}"].apply(yes_no_to_bool)
                    for col in yes_noes_to_bools
                },
                **{
                    col: lambda df, col=col: df[f"__{col}"].apply(text_to_months)
                    for col in to_convert_to_months
                }
            )
            .dropna(subset=["license_number", "business_name", "address"], how="all")
            .drop([f"__{col}" for col in yes_noes_to_bools + to_convert_to_months], axis=1)
        )[list(field_reference["renames"].values())].assign(
                start_date=source["start_date"],
                end_date=source["end_date"],
            )
        
        for col, mapping in field_reference["recodes"].items():
            renamed[col] = renamed[col].map(lambda v: recode_value(v, mapping))

        result.append(renamed)


    all_years = pd.concat(result)

    # Coerce the non-assigned dates to make sure we get something that will validate
    all_years["publish_level_date"] = pd.to_datetime(
        all_years["publish_level_date"], errors="coerce"
    )

    all_years["level_expiration_date"] = pd.to_datetime(
        all_years["level_expiration_date"], errors="coerce"
    )

    all_years.to_csv(output_path, index=False)


if __name__ == "__main__":
    transform_gstq()
