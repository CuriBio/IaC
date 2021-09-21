import pandas as pd
import uuid
import h5py
import glob

def load_data_to_dataframe(file):
    data = pd.read_excel(file, sheet_name=None, engine="openpyxl")
    
    recording_length = data["continuous-waveforms"]["Time (seconds)"].iloc[-1] * 1000
    formatted_metadata = format_data(data["metadata"], recording_length)
    formatted_well_data = format_well_data(recording_length)


def format_data(meta_sheet, recording_length):
    return {
        "barcode": meta_sheet.iloc[0,2],
        "recording_started_at": meta_sheet.iloc[1,2],
        "file_format_version": meta_sheet.iloc[4,2],
        "instrument_serial_number": meta_sheet.iloc[5,2],
        "software_version": meta_sheet.iloc[6,2],
        "length_centimilliseconds": recording_length,
        "mantarray_recording_session_id": uuid.uuid4()
        }

def format_well_data(recording_length):
    well_data = list()
    all_files = [f for f in glob.glob("test" + "**/*.h5", recursive=True)]

    for file in all_files:
        well_file = h5py.File(file, 'r')
        well_dict = {
            "well_index": well_file.attrs.get("cd89f639-1e36-4a13-a5ed-7fec6205f779"),
            "recording_started_at": well_file.attrs.get("d2449271-0e84-4b45-a28b-8deab390b7c2"),
            "length_centimilliseconds": recording_length,
        }
        well_data.append(well_dict)

    return well_data

