"""
Created by: Noelle Milton Vega
Organization: PRISMALYTICS, LLC (http://www.prismalytics.io)
Last updated: 05/30/2017
"""

import boto3
from botocore.exceptions import ClientError
import urllib.parse, json, logging
import subprocess, shlex, sys

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(sns_event, context):
    """ AWS LAMBDA function that is run when the SNS topic to which it is subscribed -- 'video-transcoded-notification' --
        receives a message. This extracts metadata from the just-trancoded video into a JSON file; then uploads it to s3.
        The AWS Lambda Handler field for this function should be set to: extract_metadata_lambda.lambda.lambda_hamdler
        (For book listing 3.7).
    """
    logger.info('Entered LAMBDA handler: %s()' % sys._getframe().f_code.co_name)
    s3_resource = boto3.Session().resource('s3')
    
    def cp_s3obj_to_localfile(s3_bucket, s3_key, localfile):
        logger.info('Entered PYTHON function: %s()' % sys._getframe().f_code.co_name)
        logger.info('Downloading s3 path (%s/%s) to local file (%s)' % (s3_bucket, s3_key, localfile,))
        try:
            s3_object = s3_resource.Bucket(s3_bucket).Object(s3_key)
            s3_object.download_file(localfile)
        except ClientError as e:
            logger.error("Received error: %s", e, exc_info=False)
            logger.error("e.response['Error']['Code']: %s", e.response['Error']['Code'])

    def extract_and_upload_metadata(localfile, s3_bucket, s3_key):
        logger.info('Entered PYTHON function: %s()' % sys._getframe().f_code.co_name) 
        logger.info('Extracting and uploading metadata from local file: %s' % (localfile,))
        try:
            cmd = shlex.split('bin/ffprobe -v quiet -print_format json -show_format ' + localfile)
            s3_object = s3_resource.Bucket(s3_bucket).Object(s3_key)
            process = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            s3_object.upload_fileobj(process.stdout) # The file-like version is needed to read process.stdout stream.
        except Exception as e:
            logger.error("Received error: %s", e, exc_info=False)
            if hasattr(e, 'response'):
                logger.error("e.response['Error']['Code']: %s", e.response['Error']['Code'])

    s3_event  = sns_event['Records'][0]['Sns']['Message']      # Get s3 event that wrote to this SNS-topic.
    s3_event  = json.loads(s3_event)                           # It's enclosed as JSON in a string; so convert to JSON/dict().
    s3_bucket = s3_event['Records'][0]['s3']['bucket']['name'] # Bucket
    s3_key    = s3_event['Records'][0]['s3']['object']['key']  # Filename with '+' for space.
    source_key = urllib.parse.unquote_plus(s3_key)             # Replace '+' with space.
    basename = s3_key.split('/')[-1].strip()                   # In case nested key/file, get just the leaf-name.
    media_localfile = '/tmp/' + basename                       # Will never already exist b/c it's a new lambda container.
    metadata_s3key = basename.rpartition('.')[0] + '.json'
    
    cp_s3obj_to_localfile(s3_bucket, source_key, media_localfile) # Download the media file.
    extract_and_upload_metadata(media_localfile, s3_bucket, metadata_s3key) # Extract metadata and upload it.
    logger.info('Completed LAMBDA handler: %s()' % sys._getframe().f_code.co_name)
