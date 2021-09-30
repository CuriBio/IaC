CREATE DATABASE IF NOT EXISTS mantarray_recordings;

USE mantarray_recordings;

CREATE TABLE IF NOT EXISTS s3_objects (
  object_id int REFERENCES uploaded_s3_objects(id),
  stored_at datetime,
  kilobytes bigint,
  md5 varchar(255),
  PRIMARY KEY(object_id)
);

CREATE TABLE IF NOT EXISTS uploaded_s3_objects (
  id int NOT NULL AUTO_INCREMENT,
  bucket varchar(255),
  object_key varchar(255),
  md5_confirmed_after_upload_at datetime,
  upload_interruptions int,
  md5_failures int,
  upload_started_at datetime,
  original_file_path varchar(255),
  uploading_computer_name varchar(255),
  PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS mantarray_frontend_log_files (
  frontend_log_id varchar(255) PRIMARY KEY,
  object_id int REFERENCES uploaded_s3_objects(id)
);

CREATE TABLE IF NOT EXISTS mantarray_backend_log_files (
  backend_log_id varchar(255) PRIMARY KEY,
  object_id int REFERENCES uploaded_s3_objects(id),
  frontend_log_id varchar(255) REFERENCES mantarray_frontend_log_files(frontend_log_id),
  exit_code tinyint,
  software_version varchar(255),
  file_format_version varchar(255),
  started_at datetime,
  ended_at datetime,
  last_used_customer_account_id varchar(255),
  last_used_user_account_id varchar(255)
);


CREATE TABLE IF NOT EXISTS mantarray_raw_files (
  well_index smallint,
  object_id int REFERENCES uploaded_s3_objects(id),
  length_centimilliseconds int,
  recording_started_at datetime,
  mantarray_recording_session_id varchar(255) REFERENCES mantarray_recording_sessions(mantarray_recording_session_id),
  PRIMARY KEY (well_index)
);

CREATE TABLE IF NOT EXISTS mantarray_recording_sessions (
  mantarray_recording_session_id varchar(255) PRIMARY KEY,
  customer_account_id varchar(255),
  user_account_id varchar(255),
  instrument_serial_number varchar(255),
  experiment_labware_id varchar(255) REFERENCES experiment_labware(experiment_labware_id),
  backend_log_id varchar(255) REFERENCES mantarray_backend_log_files(backend_log_id),
  acquisition_started_at datetime,
  length_centimilliseconds int,
  recording_started_at datetime,
  UNIQUE INDEX (instrument_serial_number, recording_started_at)
);

CREATE TABLE IF NOT EXISTS experiment_labware (
  experiment_labware_id varchar(255),
  barcoded_sbs_labware_id varchar(255) REFERENCES barcoded_sbs_labware(barcoded_sbs_labware_id),
  PRIMARY KEY (experiment_labware_id, barcoded_sbs_labware_id)
);


CREATE TABLE IF NOT EXISTS barcoded_sbs_labware (
  barcoded_sbs_labware_id varchar(255) PRIMARY KEY,
  labware_name varchar(255) REFERENCES labware_definitions(labware_name)
);

CREATE TABLE IF NOT EXISTS labware_definitions (
  labware_definition_id varchar(255) PRIMARY KEY,
  labware_name varchar(255) UNIQUE,
  row_count int,
  column_count int
);

CREATE TABLE IF NOT EXISTS sbs_labware_barcodes (
  barcoded_sbs_labware_id varchar(255) REFERENCES barcoded_sbs_labware(barcoded_sbs_labware_id),
  barcode varchar(255),
  barcode_position varchar(255),
  PRIMARY KEY (barcode)
);
