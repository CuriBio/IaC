import uuid

import pandas as pd
from pulse3D.constants import UTC_BEGINNING_RECORDING_UUID


def load_data_to_dataframe(file_name, pr):
    df = pd.read_excel(file_name, sheet_name=None, engine="openpyxl")

    recording_length = int(df["continuous-waveforms"]["Time (seconds)"].iloc[-1]) * 1000
    formatted_metadata = format_metadata(df["metadata"], recording_length)
    formatted_well_data = format_well_data(pr, recording_length)

    return formatted_metadata, formatted_well_data


def format_metadata(meta_sheet, recording_length: int):

    return {
        "barcode": meta_sheet.iloc[0, 2],
        "recording_started_at": meta_sheet.iloc[1, 2],
        # "acquisition_started_at": meta_sheet.iloc[2, 2],
        "file_format_version": meta_sheet.iloc[4, 2],
        "instrument_serial_number": meta_sheet.iloc[5, 2],
        "software_version": meta_sheet.iloc[6, 2],
        # "uploading_computer_name": meta_sheet.iloc[10, 2],
        # "backend_log_id": meta_sheet.iloc[11, 2],
        "length_centimilliseconds": recording_length,
        "file_creation_timestamp": meta_sheet.iloc[11, 2],
        "mantarray_recording_session_id": uuid.uuid4(),
    }


def format_well_data(pr, recording_length: int):
    well_data = list()
    for well_idx, well_file in enumerate(pr):
        if well_file is None:
            continue

        well_dict = {
            "well_index": well_idx,
            "recording_started_at": well_file[UTC_BEGINNING_RECORDING_UUID],
            "length_centimilliseconds": recording_length,
        }
        well_data.append(well_dict)

    return well_data
