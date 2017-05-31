"""
Created by: Noelle Milton Vega
Organization: PRISMALYTICS, LLC (http://www.prismalytics.io)
Last updated: 05/30/2017
"""

import boto3
from botocore.exceptions import ClientError
import urllib.parse, logging, inspect, sys

logger = logging.getLogger()
logger.setLevel(logging.INFO)

aws_region  = 'us-east-1'
pipeline_id = '1494373565723-ygfqt4' # ElasticTranscoder PipelineID

def lambda_handler(s3_event, context):
    """ AWS LAMBDA function that is run when s3 bucket -- 'video-uploaded' -- receives a new object. The AWS
        Lambda Handler field for this function should be set to: transcode_video.lambda.lambda_hamdler
        (For book listing 3.1).
    """
    logger.info('Entered LAMBDA handler: %s()' % sys._getframe().f_code.co_name)
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
    logger.info('Completed LAMBDA handler: %s()' % sys._getframe().f_code.co_name)
