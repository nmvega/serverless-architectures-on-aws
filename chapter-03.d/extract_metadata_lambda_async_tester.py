import sys, logging, json
import extract_metadata_lambda

""" An ASYNCHRONOUS/EVENT-based tester for the 'extract_metadata_lambda.lambda_handler' python3.6 handler,
    implemented in ./extract_metadata_lambda.py.

    It employs the two JSON event files located in the ./json.d/ subdirectory; both of which are properly
    configured to allow this tester to end-to-end work (i.e. to connect to AWS and return); as long as the
    s3 Bucket-name, the Bucket-ARN and the Object/Key-name named in the s3 event JSON file are present
    (which, for my case, are 'prismalytics-video-transcoded/' and 'sintel_trailer_v16_2k_480p24-720p.mp4',
    respectively; but which you can edit for your case). And, as long as the effective AWS IAM-User
    credentials that run this tester has permission to interact with the aforementioned s3 Bucket
    ARN and Object/Key. This might require adjusting AWS CRED UNIX environment variables. See next.

    It's a nice educational example for end-to-end testing these Lambda Python programs manually.
    ==========================================================================================
    TO RUN:
    After modifying both JSON files in ./json.d/ to suit your particular values:
    ==========================================================================================
        user$ export AWS_SECRET_ACCESS_KEY=<IAM-User-with-proper-bucket-and-object-access>
        user$ export AWS_ACCESS_KEY_ID=<IAM-User-with-proper-bucket-and-object-access>
        user$ cd ./chapter-03.d/
        user$ python3 ./extract_metadata_lambda_async_tester.py
    ==========================================================================================
"""

logger = logging.getLogger()
logger.setLevel(logging.INFO)

child_logger = logging.StreamHandler(sys.stdout)
child_logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
child_logger.setFormatter(formatter)
logger.addHandler(child_logger)    

sns_event = json.load(open('./json.d/event.to.sns.topic.json', 'r')) # Read in SNS-topic event.
s3_event = json.load(open('./json.d/event.s3.ObjectCreated:Put.json', 'r')) # Read in upstream S3-event (which notifies above SNS-topic).
sns_event['Records'][0]['Sns']['Message'] = json.dumps(s3_event) # Embed upstream S3-event into SNS-event, as a JSON-string.
extract_metadata_lambda.lambda_handler(sns_event, None)
