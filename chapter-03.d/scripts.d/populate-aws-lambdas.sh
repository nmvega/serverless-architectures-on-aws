#! /usr/bin/env bash
#
# =====================================================================
# Created by: Noelle Milton Vega / PRISMALYTICS, LLC.
# Description:
#    Simple batch script to create and upload the zip-file contents
#    for each of the three chapter-03 AWS Lambda functions. Running
#    this assumes that those Lambda functions, named in each stanza
#    below, have already been created on AWS. Modify the environment
#    variables that immediately follow to suit your environment.
# =====================================================================
PROJECT_ROOT_DIR="/path/to/project/root/dir/"
AWS_PROFILE="AWS-IAM-User-with-Lambda:UpdateFunctionCode-and-Lambda:UpdateFunctionConfiguration-permissions"
AWS_REGION="us-east-1" # Modify if you like.
AWS_LAMBDA_PYTHON_VERSION="python3.6"
AWS_OWNER_ACCOUNT_ID="Your-AWS-ID"
ZIP_FILE_NAME="aws.zip"
# ---------------------------------------------------------------------
cd ${PROJECT_ROOT_DIR}/chapter-03.d || exit 1 # Modify subdir if you like.
# ---------------------------------------------------------------------

# ---------------------------------------------------------------------
# Stanza for transcode-video Lambda ...
# ---------------------------------------------------------------------
AWS_LAMBDA_NAME="transcode-video"
rm -f ./${ZIP_FILE_NAME}
zip -r9 ./${ZIP_FILE_NAME} ./transcode_video_lambda.py
aws lambda update-function-code \
       --profile ${AWS_PROFILE} \
       --region ${AWS_REGION} \
       --function-name arn:aws:lambda:${AWS_REGION}:${AWS_OWNER_ACCOUNT_ID}:function:${AWS_LAMBDA_NAME} \
       --zip-file fileb://${ZIP_FILE_NAME}
# ---------------------------------------------------------------------
# Stanza for set_s3_permissions Lambda ...
# ---------------------------------------------------------------------
AWS_LAMBDA_NAME="set_s3_permissions"
rm -f ./${ZIP_FILE_NAME}
zip -r9 ./${ZIP_FILE_NAME} ./set_s3_permissions_lambda.py
aws lambda update-function-code \
       --profile ${AWS_PROFILE} \
       --region ${AWS_REGION} \
       --function-name arn:aws:lambda:${AWS_REGION}:${AWS_OWNER_ACCOUNT_ID}:function:${AWS_LAMBDA_NAME} \
       --zip-file fileb://${ZIP_FILE_NAME}
# ---------------------------------------------------------------------
# Stanza for extract-metadata Lambda ...
# ---------------------------------------------------------------------
AWS_LAMBDA_NAME="extract-metadata"
rm -f ./${ZIP_FILE_NAME}
zip -r9 ./${ZIP_FILE_NAME} ./bin/* ./extract_metadata_lambda.py
aws lambda update-function-code \
       --profile ${AWS_PROFILE} \
       --region ${AWS_REGION} \
       --function-name arn:aws:lambda:${AWS_REGION}:${AWS_OWNER_ACCOUNT_ID}:function:${AWS_LAMBDA_NAME} \
       --zip-file fileb://${ZIP_FILE_NAME}
# ---------------------------------------------------------------------
