import uuid

import pandas as pd


def load_data_to_dataframe(file, r):
    data = pd.read_excel(file, sheet_name=None, engine="openpyxl")

    recording_length = int(data["continuous-waveforms"]["Time (seconds)"].iloc[-1]) * 1000
    formatted_metadata = format_data(data["metadata"], recording_length)
    formatted_well_data = format_well_data(r, recording_length)

    return {"metadata": formatted_metadata, "well_data": formatted_well_data}


def format_data(meta_sheet, recording_length: int):

    return {
        "barcode": meta_sheet.iloc[0, 2],
        "recording_started_at": meta_sheet.iloc[1, 2],
        "acquisition_started_at": meta_sheet.iloc[2, 2],
        "file_format_version": meta_sheet.iloc[5, 2],
        "instrument_serial_number": meta_sheet.iloc[6, 2],
        "software_version": meta_sheet.iloc[7, 2],
        "uploading_computer_name": meta_sheet.iloc[10, 2],
        "backend_log_id": meta_sheet.iloc[11, 2],
        "length_centimilliseconds": recording_length,
        "file_creation_timestamp": meta_sheet.iloc[14, 2],
        "mantarray_recording_session_id": uuid.uuid4(),
    }


def format_well_data(r, recording_length: int):
    well_data = list()

    for idx in range(24):
        well = r.get_well_by_index(idx)
        well_dict = {
            "well_index": idx,
            "recording_started_at": well.get_begin_recording(),
            "length_centimilliseconds": recording_length,
        }
        well_data.append(well_dict)

    return well_data
