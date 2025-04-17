from extract import extract_gstq
from transform import transform_gstq
# from load import load_gstq

from great_start_to_quality import setup_logging


logger = setup_logging()


extract_gstq(logger)
transform_gstq(logger)