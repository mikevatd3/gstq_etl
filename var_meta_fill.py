from pathlib import Path
import pandas as pd
from great_start_to_quality.schema import Providers
from great_start_to_quality.reference import FIELD_RENAME


datadict_path = Path("V:") / "DATA" / "Childcare" / "Great start to quality" / "GSQPublicExportDataDictionary.csv"



df = pd.read_csv(datadict_path)

description_reference = {
   FIELD_RENAME[row["Data Point"]]: row["Definition"]
   for _, row in df.iterrows()
}

fields = Providers.to_json_schema()["properties"].keys()

result = []
for field in fields:
    result.append(f'[[tables.providers.variables]]')
    result.append(f'name = "{field}"')
    result.append(f'description = "{description_reference.get(field, "")}"')
    result.append("\n")

print("\n".join(result))