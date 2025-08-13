import json
from pathlib import Path
import geopandas as gpd
import pandas as pd
from pygris.geocode import batch_geocode


WORKING_DIR = Path(__file__).parent


def geocode_providers():
    output_file = WORKING_DIR / "output" / "geocoded_providers.geojson"

    ID_COLUMN = "license_number"
    
    if output_file.exists():
        print(f"Geocoded file already completed at {str(output_file)}. Delete this "
              "if you'd like to re-run the geocode.")
        return
    
    result = []


    cache = pd.DataFrame({
        # Input
        ID_COLUMN: [],
        "address": [],
        "city": [],
        "state": [], # This is text state
        "zip": [],

        # Output
        "id": [], # This is a repeat of ID_COLUMN
        "address": [],
        "status": [],
        "match_quality": [],
        "match_address": [],
        "tiger_line_id": [],
        "tiger_side": [],
        "state_fips": [],
        "county": [],
        "tract": [],
        "block": [],
        "logitude": [],
        "latitude": [],
    })

    keys = [ID_COLUMN, "address", "city", "state", "zip"] # This is text state 
    outputs = [ 
        "id", "address", "status", "match_quality", "match_address", 
        "tiger_line_id", "tiger_side", "state_fips", "county", "tract", "block",
        "logitude", "latitude",
    ]

    for i, chunk in enumerate(pd.read_csv(
        WORKING_DIR / "output" / "all_childcare.csv",
        chunksize=5000
    ), start=1):
        print(f"Processing chunk {i}.")


        geocoded = batch_geocode(chunk, id_column=ID_COLUMN,
                                 address="address", city="city", state="state", 
                                 zip="zip_code")
        
        # Columns returned
        # - id
        # - address
        # - status
        # - match_quality
        # - match_address
        # - tiger_line_id
        # - tiger_side
        # - state
        # - county
        # - tract
        # - block
        # - logitude
        # - latitude

        dated = (
            chunk[[ID_COLUMN, "start_date", "end_date"]]
            .merge(geocoded.rename(columns={"id": ID_COLUMN}),  on=ID_COLUMN)
            [[ID_COLUMN, *list(geocoded.columns.drop("id")), "start_date", "end_date"]]
        )
        
        result.append(dated)
    
    collected = pd.concat(result)
    gdf = gpd.GeoDataFrame(collected, geometry=gpd.points_from_xy(collected["longitude"], collected["latitude"]))
    gdf.to_file(output_file, index=False)

