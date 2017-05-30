
"""
Created by: Noelle Milton Vega
Organization: PRISMALYTICS, LLC (http://www.prismalytics.io)
Last updated: 05/30/2017
"""

import boto3
from botocore.exceptions import ClientError
import urllib.parse, json, logging, inspect, shlex
import subprocess

logger = logging.getLogger()
logger.setLevel(logging.INFO)

func_name = lambda: inspect.stack()[1][3] # Used to get name of Python function currently inside of.
aws_region  = 'us-east-1'
pipeline_id = '1494373565723-ygfqt4' # ElasticTranscoder PipelineID
s3_resource = boto3.Session().resource('s3')


def transcode_video_lambda(s3_event, context):
    """ AWS LAMBDA function that is run when a s3 bucket,
        'video-uploaded', receives a new object. (Book listing 3.1). """
    logger.info('Entered LAMBDA handler: %s()' % func_name())
    etClient = boto3.client('elastictranscoder', aws_region)
    
    bucket = s3_event['Records'][0]['s3']['bucket']['name'] # Bucket
    key = s3_event['Records'][0]['s3']['object']['key']     # Filename with '+' for space.
    source_key = urllib.parse.unquote_plus(key)             # Replace '+' with space.
    output_key_prefix = source_key.rpartition('.')[0]
    
    logger.info('S3 bucket name: ' + bucket)
    logger.info('Source file name: ' + source_key)
    logger.info('Destination file prefix: ' + output_key_prefix)
    
    et_params = {
        'PipelineId' : pipeline_id,
        'Input' : {'Key': source_key},
        'Outputs': [
             {  # Generic 1080p
               'Key' : output_key_prefix + '-1080p.mp4',
               'PresetId': '1351620000001-000001'},
             {  # Generic 720p
               'Key' : output_key_prefix + '-720p.mp4',
               'PresetId': '1351620000001-000010'},
             {  # Web Friendly 720p
                'Key' : output_key_prefix + '-web-720p.mp4',
                'PresetId': '1351620000001-100070'}
        ]
    }
    
    logger.info('Creating transcoder job.')
    try:
        etClient.create_job(PipelineId = et_params['PipelineId'],
                            Input = et_params['Input'],
                            Outputs = et_params['Outputs'])
    except ClientError as e:
        logger.error("Received error: %s", e, exc_info=False) # exc_info=True will print stack-trace as well.
        logger.error("e.response['Error']['Code']: %s", e.response['Error']['Code'])
    logger.info('Completed LAMBDA handler: %s()' % func_name())




def set_s3_permissions_lambda(sns_event, context):
    """ AWS LAMBDA function that is run when the SNS topic to which it is
        subscribed, 'video-transcoded-notification', receives a message.
        This sets 'public-read' ACL/permission on the transcoded video s3
        object. (Book listing 3.6) """
    logger.info('Entered LAMBDA handler: %s()' % func_name())
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




def extract_metadata_lambda(sns_event, context):
    """ AWS LAMBDA function that is run when the SNS topic to which it is
        subscribed, 'video-transcoded-notification', receives a message. This
        extracts metadata from the just-trancoded video into a JSON file;
        then uploads that to s3. (Book listing 3.7) """
    logger.info('Entered LAMBDA handler: %s()' % func_name())
    
    def cp_s3obj_to_localfile(s3_bucket, s3_key, localfile):
        logger.info('Entered PYTHON function: %s()' % func_name())
        logger.info('Downloading s3 path (%s/%s) to local file (%s)' % (s3_bucket, s3_key, localfile,))
        try:
            s3_object = s3_resource.Bucket(s3_bucket).Object(s3_key)
            s3_object.download_file(localfile)
        except ClientError as e:
            logger.error("Received error: %s", e, exc_info=False)
            logger.error("e.response['Error']['Code']: %s", e.response['Error']['Code'])

    def extract_and_upload_metadata(localfile, s3_bucket, s3_key):
        logger.info('Entered PYTHON function: %s()' % func_name())
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
    logger.info('Completed LAMBDA handler: %s()' % func_name())
