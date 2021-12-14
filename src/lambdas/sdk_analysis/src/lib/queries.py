insert_into_uploaded_s3_table = """
    INSERT INTO uploaded_s3_objects(id, bucket, object_key, upload_started_at)
    VALUES (NULL, %s, %s, NOW());
    """

select_last_upload_id = """(SELECT id FROM uploaded_s3_objects ORDER BY id DESC LIMIT 1)"""

insert_into_mantarray_recording_sessions = """
    INSERT INTO mantarray_recording_sessions(mantarray_recording_session_id, customer_account_id, user_account_id, instrument_serial_number, length_centimilliseconds,
    recording_started_at)
    VALUES (%s, %s, %s, %s, %s, %s);
    """

insert_into_mantarray_raw_files = f"""
    INSERT INTO mantarray_raw_files(well_index, upload_id, length_centimilliseconds, recording_started_at, mantarray_recording_session_id)
    VALUES (%s, {select_last_upload_id}, %s, %s, %s);
    """

insert_into_s3_objects = f"""
    INSERT INTO s3_objects(upload_id, kilobytes, stored_at, md5) VALUES ({select_last_upload_id}, %s, %s, %s);
    """
