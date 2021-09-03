# import os
# import logging
# import boto3

# LOGGER = logging.getLogger()
# LOGGER.setLevel(logging.INFO)

# SQS_NAME = os.environ.get('SQS_NAME')
# S3_BUCKET = os.environ.get('S3_BUCKET')
# REGION = os.environ.get('REGION')

# s3 = boto3.resource('s3', region_name=REGION)

# def handler(event, context):
#    LOGGER.info(f'Event structure: {event}')
#    LOGGER.info(f'S3_BUCKET: {S3_BUCKET}')

#    return {
#        'status': 'ok'
#    }
import os
import logging
import boto3
from botocore.exceptions import ClientError


#SQS_NAME = os.environ.get('SQS_NAME')
S3_BUCKET = os.environ.get('S3_BUCKET')
#REGION = os.environ.get('REGION')

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_presigned_url(s3_client, object_key, expires_in):
    """
    Generate a presigned Amazon S3 URL that can be used to perform an action.

    :param s3_client: A Boto3 Amazon S3 client.
    :param client_method: The name of the client method that the URL performs.
    :param method_parameters: The parameters of the specified client method.
    :param expires_in: The number of seconds the presigned URL is valid for.
    :return: The presigned URL.
    """
    try:
        url = s3_client.generate_presigned_post(S3_BUCKET, object_key, Fields=None, Conditions=None, ExpiresIn=expires_in)
        logger.info("Got presigned URL: %s", url)
    except ClientError:
        logger.exception("Couldn't get a presigned URL for client method '%s'.", client_method)
        raise

    return url


def handler(event, context):
    s3_client = boto3.client('s3')
    logger.info(f'event: {event}')
    url = generate_presigned_url(s3_client, object_key=event['file_name'], expires_in=3600)
    return {'status': 'ok', 'url': url}
