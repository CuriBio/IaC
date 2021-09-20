import boto3
import json
from botocore.exceptions import ClientError


def get_secrets():

    key_secret_name = "db-ec2-key-pair"
    creds_secret_name = "db-creds"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_creds_secret_value_response = client.get_secret_value(
            SecretId=creds_secret_name
        )
        get_key_secret_value_response = client.get_secret_value(
            SecretId=key_secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        key_secret = get_key_secret_value_response['SecretString']

        creds_secret = get_creds_secret_value_response['SecretString']
        parsed_creds_secret = json.loads(creds_secret)
        username = parsed_creds_secret['username']
        password = parsed_creds_secret['password']
    
        return {"username": username, "password": password, "ssh_pkey": key_secret}
