CREATE DATABASE mantarray_recordings IF NOT EXISTS;

CREATE Table s3_objects {
  bucket varchar PK
  object_key varchar PK
  stored_at datetime
  kilobytes int64
  crc32 varchar
  crc32_embedded_position uint8 : 0 - not embedded, 1 - final 4 bytes, 2 - first 4 bytes

}

CREATE Table uploaded_s3_objects {
  bucket varchar PK
  object_key varchar PK
  ad_completed_at datetime
  created_at datetime
  crc32_confirmed_after_upload_at datetime
  upload_interruptions int
  crc32_failures int
  upload_started_at datetime
  original_file_path varchar
  uploading_computer_name varchar
}

Ref: s3_objects.(bucket, object_key) - uploaded_s3_objects.(bucket, object_key)

CREATE Table mantarray_frontend_log_files {
  frontend_log_id varchar PK
  bucket varchar
  object_key varchar
}
Ref: uploaded_s3_objects.(bucket, object_key) - mantarray_frontend_log_files.(bucket, object_key)


CREATE Table mantarray_backend_log_files {
  backend_log_id varchar PK
  bucket varchar
  object_key varchar
  frontend_log_id varchar
  exit_code tinyint
  software_version varchar
  file_format_version varchar
  started_at datetime
  ended_at datetime
  last_used_customer_account_id varchar
  last_used_user_account_id varchar
}
Ref: uploaded_s3_objects.(bucket, object_key) - mantarray_backend_log_files.(bucket, object_key)
Ref: mantarray_backend_log_files.frontend_log_id - mantarray_frontend_log_files.frontend_log_id

CREATE Table mantarray_raw_files {
  bucket varchar PK
  object_key varchar PK
  well_index smallint
  length_centimilliseconds int32
  recording_started_at datetime
  mantarray_recording_session_id varchar
}
Ref: uploaded_s3_objects.(bucket, object_key) - mantarray_raw_files.(bucket, object_key)

CREATE Table mantarray_recording_sessions {
  mantarray_recording_session_id varchar PK
  customer_account_id varchar
  user_account_id varchar
  instrument_serial_number varchar
  experiment_labware_id varchar
  backend_log_id varchar
  acquisition_started_at datetime
  length_centimilliseconds int32
  recording_started_at datetime

  Indexes {
    (instrument_serial_number, recording_started_at) [unique]
  }

}
Ref: experiment_labware.experiment_labware_id < mantarray_recording_sessions.experiment_labware_id
Ref: mantarray_backend_log_files.backend_log_id < mantarray_recording_sessions.backend_log_id
Ref: mantarray_raw_files.mantarray_recording_session_id > mantarray_recording_sessions.mantarray_recording_session_id


CREATE Table experiment_labware {
  experiment_labware_id varchar PK
  barcoded_sbs_labware_id varchar PK
}


CREATE Table barcoded_sbs_labware {
  barcoded_sbs_labware_id varchar PK
  labware_name varchar
}
Ref: barcoded_sbs_labware.barcoded_sbs_labware_id < experiment_labware.barcoded_sbs_labware_id
Ref: labware_definitions.labware_name < barcoded_sbs_labware.labware_name

CREATE Table labware_definitions {
  labware_definition_id varchar PK
  labware_name varchar unique
  row_count int
  column_count int
}

CREATE Table sbs_labware_barcodes {
  barcoded_sbs_labware_id varchar
  barcode varchar PK
  barcode_position varchar PK

}
Ref: barcoded_sbs_labware.barcoded_sbs_labware_id < sbs_labware_barcodes.barcoded_sbs_labware_id
