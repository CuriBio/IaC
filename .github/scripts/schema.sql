CREATE DATABASE IF NOT EXISTS mantarray_recordings;

USE DATABASE mantarray_recordings;

CREATE TABLE IF NOT EXISTS s3_objects {
  bucket varchar
  object_key varchar
  stored_at datetime
  kilobytes bigint
  crc32 varchar
  crc32_embedded_position tinyint  
  PRIMARY KEY (bucket, object_key)
}

CREATE TABLE IF NOT EXISTS uploaded_s3_objects {
  bucket varchar
  object_key varchar
  created_at datetime
  crc32_confirmed_after_upload_at datetime
  upload_interruptions int
  crc32_failures int
  upload_started_at datetime
  original_file_path varchar
  uploading_computer_name varchar
  PRIMARY KEY (bucket, object_key)
}

-- Ref: s3_objects.(bucket, object_key) - uploaded_s3_objects.(bucket, object_key)

CREATE TABLE IF NOT EXISTS mantarray_frontend_log_files {
  frontend_log_id varchar PRIMARY KEY
  bucket varchar REFERENCES uploaded_s3_objects(bucket)
  object_key varchar REFERENCES uploaded_s3_objects(object_key)
}

-- Ref: uploaded_s3_objects.(bucket, object_key) - mantarray_frontend_log_files.(bucket, object_key)


CREATE TABLE IF NOT EXISTS mantarray_backend_log_files {
  backend_log_id varchar PRIMARY KEY
  bucket varchar REFERENCES uploaded_s3_objects(bucket)
  object_key varchar REFERENCES uploaded_s3_objects(object_key)
  frontend_log_id varchar REFERENCES mantarray_frontend_log_files(frontend_log_id)
  exit_code tinyint
  software_version varchar
  file_format_version varchar
  started_at datetime
  ended_at datetime
  last_used_customer_account_id varchar
  last_used_user_account_id varchar
}
-- Ref: uploaded_s3_objects.(bucket, object_key) - mantarray_backend_log_files.(bucket, object_key)
-- Ref: mantarray_backend_log_files.frontend_log_id - mantarray_frontend_log_files.frontend_log_id

CREATE TABLE IF NOT EXISTS mantarray_raw_files {
  bucket varchar
  object_key varchar
  well_index smallint
  length_centimilliseconds int32
  recording_started_at datetime
  mantarray_recording_session_id varchar REFERENCES mantarray_recording_sessions(mantarray_recording_session_id)
  PRIMARY KEY (bucket, object_key)
}
-- Ref: uploaded_s3_objects.(bucket, object_key) - mantarray_raw_files.(bucket, object_key)

CREATE TABLE IF NOT EXISTS mantarray_recording_sessions {
  mantarray_recording_session_id varchar PRIMARY KEY
  customer_account_id varchar
  user_account_id varchar
  instrument_serial_number varchar
  experiment_labware_id varchar REFERENCES experiment_labware(experiment_labware_id)
  backend_log_id varchar REFERENCES mantarray_backend_log_files(backend_log_id)
  acquisition_started_at datetime
  length_centimilliseconds int32
  recording_started_at datetime
  UNIQUE INDEX (instrument_serial_number, recording_started_at)
}
-- Ref: experiment_labware.experiment_labware_id < mantarray_recording_sessions.experiment_labware_id
-- Ref: mantarray_backend_log_files.backend_log_id < mantarray_recording_sessions.backend_log_id
-- Ref: mantarray_raw_files.mantarray_recording_session_id > mantarray_recording_sessions.mantarray_recording_session_id


CREATE TABLE IF NOT EXISTS experiment_labware {
  experiment_labware_id varchar
  barcoded_sbs_labware_id varchar REFERENCES barcoded_sbs_labware(barcoded_sbs_labware_id)
  PRIMARY KEY (experiment_labware_id, barcoded_sbs_labware_id)
}


CREATE TABLE IF NOT EXISTS barcoded_sbs_labware {
  barcoded_sbs_labware_id varchar PRIMARY KEY
  labware_name varchar REFERENCES labware_definitions(labware_name)
}
-- Ref: barcoded_sbs_labware.barcoded_sbs_labware_id < experiment_labware.barcoded_sbs_labware_id
-- Ref: labware_definitions.labware_name < barcoded_sbs_labware.labware_name

CREATE TABLE IF NOT EXISTS labware_definitions {
  labware_definition_id varchar PRIMARY KEY
  labware_name varchar UNIQUE
  row_count int
  column_count int
}

CREATE TABLE IF NOT EXISTS sbs_labware_barcodes {
  barcoded_sbs_labware_id varchar REFERENCES barcoded_sbs_labware(barcoded_sbs_labware_id)
  barcode varchar
  barcode_position varchar
  PRIMARY KEY (barcode, barcode_position)
}
-- Ref: barcoded_sbs_labware.barcoded_sbs_labware_id < sbs_labware_barcodes.barcoded_sbs_labware_id
