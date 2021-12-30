import uuid

import pandas as pd
from pulse3D.constants import COMPUTER_NAME_HASH_UUID
from pulse3D.constants import MANTARRAY_SERIAL_NUMBER_UUID
from pulse3D.constants import MICRO_TO_BASE_CONVERSION
from pulse3D.constants import PLATE_BARCODE_UUID
from pulse3D.constants import UTC_BEGINNING_RECORDING_UUID
from pulse3D.constants import WELL_INDEX_UUID
from pymysql import NULL


def load_data_to_dataframe(file_name, pr):
    df = pd.read_excel(file_name, sheet_name=None, engine="openpyxl")

    recording_length = int(df["continuous-waveforms"]["Time (seconds)"].iloc[-1]) * MICRO_TO_BASE_CONVERSION
    formatted_metadata = format_metadata(df["metadata"], pr, recording_length)
    formatted_well_data = format_well_data(pr, recording_length)

    return formatted_metadata, formatted_well_data


def format_metadata(meta_sheet, pr, recording_length: int):
    well_file = pr.__next__()

    return {
        "barcode": well_file.get(PLATE_BARCODE_UUID, NULL),
        "recording_started_at": well_file[UTC_BEGINNING_RECORDING_UUID],
        "file_format_version": well_file.version,
        "instrument_serial_number": well_file.get(MANTARRAY_SERIAL_NUMBER_UUID, NULL),
        "length_microseconds": recording_length,
        "file_creation_timestamp": meta_sheet.iloc[11, 2],
        "mantarray_recording_session_id": uuid.uuid4(),
        "uploading_computer_name": well_file.get(COMPUTER_NAME_HASH_UUID, NULL),
    }


def format_well_data(pr, recording_length: int):
    well_data = list()
    for _, well_file in enumerate(pr):
        if well_file is None:
            continue

        well_dict = {
            "well_index": well_file.get(WELL_INDEX_UUID, NULL),
            "recording_started_at": well_file[UTC_BEGINNING_RECORDING_UUID],
            "length_microseconds": recording_length,
        }
        well_data.append(well_dict)

    return well_data
