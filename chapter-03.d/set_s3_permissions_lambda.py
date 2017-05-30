
"""
Created by: Noelle Milton Vega
Organization: PRISMALYTICS, LLC (http://www.prismalytics.io)
Last updated: 05/30/2017
"""

import boto3
from botocore.exceptions import ClientError
import urllib.parse, json, logging, sys

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(sns_event, context):
    """ AWS LAMBDA function that is run when the SNS topic to which it is subscribed -- 'video-transcoded-notification' --
        receives a message. This sets 'public-read' ACL/permission on the s3 object (a transcoded video). The AWS
        Lambda Handler field for this function should be set to: set_s3_permissions_lambda.lambda.lambda_hamdler
        (For book listing 3.6).
    """
    logger.info('Entered LAMBDA handler: %s()' % sys._getframe().f_code.co_name)
    s3Client = boto3.client('s3')
   
    s3_event = sns_event['Records'][0]['Sns']['Message']    # Get s3 event that wrote to this SNS-topic.
    s3_event = json.loads(s3_event)                         # It's enclosed as JSON in a string; so convert to JSON/dict().
    bucket = s3_event['Records'][0]['s3']['bucket']['name'] # Bucket
    key = s3_event['Records'][0]['s3']['object']['key']     # Filename with '+' for space.
    source_key = urllib.parse.unquote_plus(key)             # Replace '+' with space.

    logger.info('S3 bucket name: ' + bucket)
    logger.info('Source file name: ' + source_key)

    try: 
        s3Client.put_object_acl(Bucket=bucket, Key=source_key, ACL='public-read')
    except ClientError as e:
        logger.error("Received error: %s", e, exc_info=False)
        logger.error("e.response['Error']['Code']: %s", e.response['Error']['Code'])
    logger.info('Completed LAMBDA handler: %s()' % func_name())
