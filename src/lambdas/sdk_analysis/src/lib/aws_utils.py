import json
import logging

import boto3
from botocore.exceptions import ClientError

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", level=logging.INFO)
logger = logging.getLogger()


def get_ssm_secrets():
    # Get db credentials to connect
    creds_secret_name = "db-creds"

    # Create a ssm client
    ssm_client = boto3.client("secretsmanager")

    try:
        get_creds_secret_value_response = ssm_client.get_secret_value(SecretId=creds_secret_name)

    except ClientError as e:
        logger.error(f"Error retrieving aws secrets: {e}")

    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        creds_secret = get_creds_secret_value_response["SecretString"]
        parsed_creds_secret = json.loads(creds_secret)

        username = parsed_creds_secret["username"]
        password = parsed_creds_secret["password"]

        return {"username": username, "password": password}


def get_remote_aws_host():
    # Create rds client to access DNS name
    rds_client = boto3.client("rds")

    try:
        rds_cluster_id = (
            rds_client.describe_db_cluster_endpoints().get("DBClusterEndpoints")[0].get("DBClusterIdentifier")
        )
        instance_id = rds_cluster_id + "-1"

        instances = rds_client.describe_db_instances(DBInstanceIdentifier=instance_id)
        rds_host = instances.get("DBInstances")[0].get("Endpoint").get("Address")

    except ClientError as e:
        logger.error(f"Error retrieving remote aws endpoints for ec2 and aurora db: {e}")

    return rds_host


def get_s3_object_contents(bucket: str, key: str):
    # Grab s3 object metadata from aws
    s3_client = boto3.client("s3")

    try:
        s3_obj_size = s3_client.head_object(Bucket=bucket, Key=key).get("ContentLength") / 1000
    except ClientError as e:  # Get content size in bytes to kb    except ClientError as e:
        logger.error(f"Error retrieving s3 object size: {e}")

    return s3_obj_size
