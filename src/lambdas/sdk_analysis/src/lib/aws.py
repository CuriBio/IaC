import json
import logging

import boto3
from botocore.exceptions import ClientError


logging.basicConfig(format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


def get_ssm_secrets():

    key_secret_name = "db-ec2-key-pair"
    creds_secret_name = "db-creds"

    # Create a Secrets Manager client
    ssm_client = boto3.client("secretsmanager")

    try:
        get_creds_secret_value_response = ssm_client.get_secret_value(SecretId=creds_secret_name)
        get_key_secret_value_response = ssm_client.get_secret_value(SecretId=key_secret_name)

    except ClientError as e:
        logger.error(f"Error retrieving aws secrets: {e}")

    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        key_secret = get_key_secret_value_response["SecretString"]

        creds_secret = get_creds_secret_value_response["SecretString"]
        parsed_creds_secret = json.loads(creds_secret)

        username = parsed_creds_secret["username"]
        password = parsed_creds_secret["password"]

        return {"username": username, "password": password, "ssh_pkey": key_secret}


def get_remote_aws_endpoints():
    # Create rds and ec2 client to access DNS names
    rds_client = boto3.client("rds")
    ec2_client = boto3.client("ec2")
    try:
        rds_endpoint = rds_client.describe_db_cluster_endpoints(
            Filters=[{"Name": "db-cluster-endpoint-type", "Values": ["writer"]}]
        )["DBClusterEndpoints"][0]["Endpoint"]

        ec2_endpoint = ec2_client.describe_instances(
            Filters=[{"Name": "key-name", "Values": ["db_key_pair"]}]
        )["Reservations"][0]["Instances"][0]["PublicDnsName"]
    except ClientError as e:
        logger.error(f"Error retrieving remote aws endpoints for ec2 and aurora db: {e}")

    return {"rds_endpoint": rds_endpoint, "ec2_endpoint": ec2_endpoint}


def get_s3_object_contents(bucket: str, key: str):
    # Grab s3 metadata from aws
    s3_client = boto3.client("s3")

    try:
        s3_obj_size = s3_client.head_object(Bucket=bucket, Key=key).get("ContentLength") / 1000
    except ClientError as e:  # Get content size in bytes to kb    except ClientError as e:
        logger.error(f"Error retrieving s3 object size: {e}")

    return s3_obj_size
