import json

import boto3
from botocore.exceptions import ClientError


def get_ssm_secrets():
    # Get db credentials to connect
    creds_secret_name = "db-creds"

    # Create a ssm client
    ssm_client = boto3.client("secretsmanager")

    try:
        get_creds_secret_value_response = ssm_client.get_secret_value(SecretId=creds_secret_name)

    except ClientError as e:
        raise ClientError(f"error retrieving aws secrets: {e}")

    else:
        creds_secret = get_creds_secret_value_response["SecretString"]
        parsed_creds_secret = json.loads(creds_secret)

        username = parsed_creds_secret["username"]
        password = parsed_creds_secret["password"]

        return {"username": username, "password": password}


def get_remote_aws_host(bucket: str):
    # Create rds client to access DNS name
    rds_client = boto3.client("rds")
    workspace = bucket.split("-sdk-analyzed")[0]

    try:
        rds_clusters = rds_client.describe_db_cluster_endpoints().get("DBClusterEndpoints")
        for endpoint in rds_clusters:
            if workspace in endpoint.get("DBClusterIdentifier"):
                instance_id = endpoint.get("DBClusterIdentifier") + "-one"
                db_instances = rds_client.describe_db_instances(DBInstanceIdentifier=instance_id)
                db_host = db_instances.get("DBInstances")[0].get("Endpoint").get("Address")
                return db_host

    except ClientError as e:
        raise ClientError(f"error retrieving remote host: {e}")


def get_s3_object_contents(bucket: str, key: str):
    # Grab s3 object metadata from aws
    s3_client = boto3.client("s3")

    try:
        s3_obj_size = s3_client.head_object(Bucket=bucket, Key=key).get("ContentLength") / 1000
    except ClientError as e:  # Get content size in bytes to kb    except ClientError as e:
        raise ClientError(f"error retrieving s3 object size: {e}")

    return s3_obj_size
