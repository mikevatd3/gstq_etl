import datetime
import pandera as pa
from pandera.typing import Series


class Providers(pa.DataFrameModel):
    """
    This is one of two tables that make sense to include
    """

    code: str = pa.Field(unique=True)
    title: str = pa.Field()
    description: str = pa.Field(nullable=True)
    date: datetime.date = pa.Field()

    class Config:  # type: ignore
        strict = True
        coerce = True

    @pa.check("description")
    def max_nulls(cls, description: Series[str]) -> bool:
        """
        It's okay for some of these to be null, but if there are too many
        it could indicate a problem.
        """
        return description.isna().sum() < 200


