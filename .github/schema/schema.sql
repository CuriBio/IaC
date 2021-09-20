CREATE DATABASE IF NOT EXISTS mantarray_recordings;

USE mantarray_recordings;

CREATE TABLE IF NOT EXISTS s3_objects {
  bucket_id int REFERENCES uploaded_s3_objects(id)
  stored_at datetime
  kilobytes bigint
  crc32 varchar
  crc32_embedded_position tinyint
}

CREATE TABLE IF NOT EXISTS uploaded_s3_objects {
  id int NOT NULL AUTO_INCREMENT,
  bucket varchar
  object_key varchar
  created_at datetime
  crc32_confirmed_after_upload_at datetime
  upload_interruptions int
  crc32_failures int
  upload_started_at datetime
  original_file_path varchar
  uploading_computer_name varchar
  PRIMARY KEY (id)
}

CREATE TABLE IF NOT EXISTS mantarray_frontend_log_files {
  frontend_log_id varchar PRIMARY KEY
  bucket_id int REFERENCES uploaded_s3_objects(id)

}

CREATE TABLE IF NOT EXISTS mantarray_backend_log_files {
  backend_log_id varchar PRIMARY KEY
  bucket_id int REFERENCES uploaded_s3_objects(id)
  frontend_log_id varchar REFERENCES mantarray_frontend_log_files(frontend_log_id)
  exit_code tinyint
  software_version varchar
  file_format_version varchar
  started_at datetime
  ended_at datetime
  last_used_customer_account_id varchar
  last_used_user_account_id varchar
}


CREATE TABLE IF NOT EXISTS mantarray_raw_files {
  bucket_id int REFERENCES uploaded_s3_objects(id)
  well_index smallint
  length_centimilliseconds int32
  recording_started_at datetime
  mantarray_recording_session_id varchar REFERENCES mantarray_recording_sessions(mantarray_recording_session_id)
}

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

CREATE TABLE IF NOT EXISTS experiment_labware {
  experiment_labware_id varchar
  barcoded_sbs_labware_id varchar REFERENCES barcoded_sbs_labware(barcoded_sbs_labware_id)
  PRIMARY KEY (experiment_labware_id, barcoded_sbs_labware_id)
}


CREATE TABLE IF NOT EXISTS barcoded_sbs_labware {
  barcoded_sbs_labware_id varchar PRIMARY KEY
  labware_name varchar REFERENCES labware_definitions(labware_name)
}

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
