import os, sys, logging, json
import extract_metadata_lambda

""" An ASYNCHRONOUS/EVENT-based tester for the 'extract_metadata_lambda.lambda_handler' python3.6 handler.
    It employs the two JSON event files located in the ./json.d subdirectory; both of which are properly
    configured to allow this tester to end-to-end work (i.e. hit AWS and return), as long as the named s3 bucket
    (prismalytics-video-transcoded/) and object (sintel_trailer_v16_2k_480p24-720p.mp4) are present. And,
    as long as the effective AWS IAM-User credentials that runs this tester has permission to interact
    with the aforementioned bucket and object (which might require adjusting AWS CRED UNIX environment variables).

    It's just one educational approach to testing these Lambda Python programs manually.
"""

logger = logging.getLogger()
logger.setLevel(logging.INFO)

child_logger = logging.StreamHandler(sys.stdout)
child_logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
child_logger.setFormatter(formatter)
logger.addHandler(child_logger)    

os.chdir('./chapter-03.d/')
sns_event = json.load(open('./json.d/event.to.sns.topic.json', 'r')) # Read in SNS-topic event.
s3_event = json.load(open('./json.d/event.s3.ObjectCreated:Put.json', 'r')) # Read in upstream S3-event (which notifies above SNS-topic).
sns_event['Records'][0]['Sns']['Message'] = json.dumps(s3_event) # Embed upstream S3-event into SNS-event, as a JSON-string.
extract_metadata_lambda.lambda_handler(sns_event, None)
