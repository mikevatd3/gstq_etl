import datetime
import geopandas as gpd
import pandas as pd
import pandera as pa
from shapely.geometry import Point


class Providers(pa.DataFrameModel):
    """
    This is one of two tables that make sense to include
    """
    business_name: str = pa.Field(nullable=False) # nullable=False by default
    license_number: str = pa.Field(nullable=False)
    contact_name: str = pa.Field()
    license_type: str = pa.Field()
    profile_link: str = pa.Field()
    phone: str = pa.Field(nullable=True)
    email: str = pa.Field(nullable=True)
    address: str = pa.Field()
    city: str = pa.Field()
    state: str = pa.Field()
    zip_code: str = pa.Field()
    county: str = pa.Field()
    region: str = pa.Field()
    isd_or_esa: str = pa.Field(nullable=True)
    website: str = pa.Field(nullable=True)
    licensed_registered_date: str = pa.Field(nullable=True)
    accepts_from_mos: int = pa.Field()
    accepts_to_mos: int = pa.Field()
    licensed_from_mos: int = pa.Field()
    licensed_to_mos: int = pa.Field()
    capacity: int = pa.Field()
    accreditation: str = pa.Field(nullable=True)
    full_time: bool = pa.Field()
    part_time: bool = pa.Field()
    dropin_hourly: bool = pa.Field()
    before_school: bool = pa.Field()
    after_school: bool = pa.Field()
    evening: bool = pa.Field()
    overnight: bool = pa.Field()
    all_hours: bool = pa.Field()
    weekend: bool = pa.Field()
    cdc_scholarships: bool = pa.Field()
    quality_level: str = pa.Field()
    publish_level_date : datetime.date = pa.Field(nullable=True)
    level_expiration_date : datetime.date = pa.Field(nullable=True)
    cooperative: bool = pa.Field()
    faith_based: bool = pa.Field()
    montessori: bool = pa.Field()
    reggio_inspired: bool = pa.Field()
    preschool: bool = pa.Field()
    strong_beginnings: bool = pa.Field(nullable=True) # Not on pre-2023
    gsrp: bool = pa.Field()
    early_head_start: bool = pa.Field()
    head_start: bool = pa.Field()
    school_age: bool = pa.Field(nullable=True)
    nature_based: bool = pa.Field()
    date: datetime.date = pa.Field(nullable=False)

    class Config:  # type: ignore
        strict = True
        coerce = True

    @pa.dataframe_check
    def accepts_froms_neq_tos(cls, df: pd.DataFrame) -> bool:
        return (df["accepts_from_mos"] != df["accepts_to_mos"]).any()

    @pa.dataframe_check
    def licensed_froms_neq_tos(cls, df: pd.DataFrame) -> bool:
        return (df["licensed_from_mos"] != df["licensed_to_mos"]).any()


class ProvidersGEO(pa.DataFrameModel):
    license_number: str = pa.Field(nullable=False)
    date: datetime.date = pa.Field(nullable=False)
    match_type: str = pa.Field()
    block_geoid: str = pa.Field(nullable=True)
    geom: Point = pa.Field(nullable=True)

    class Config:  # type: ignore
        strict = True
        coerce = True

