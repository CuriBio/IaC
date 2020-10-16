#!/bin/bash
# To run: sh create-in-order.sh
set -ex # exit if command fails and display commands https://www.peterbe.com/plog/set-ex
THE_REGION="us-east-1"
THE_STAGE="modl"
THE_BUCKET_NAME_UNIQUIFIER="curi-bio"

# initially create the bucket for cloud formation templates without any server access logging enabled (because the bucket for that does not yet exist)
CURRENT_STACK_NAME=cloud-formation-templates-bucket-$THE_REGION
aws cloudformation deploy --stack-name=$CURRENT_STACK_NAME --parameter-overrides CostCenterTagValue="General Overhead" TheBucketName=cf-templates--$THE_REGION--$THE_BUCKET_NAME_UNIQUIFIER--$THE_STAGE EnableServerAccessLogging=false --template-file=aws/templates/s3/generic-bucket.yaml --no-fail-on-empty-changeset
aws cloudformation update-termination-protection --stack-name $CURRENT_STACK_NAME --enable-termination-protection

# package and deploy the S3 bucket to hold Server Access Logs
CURRENT_STACK_NAME=s3-server-logs-bucket-$THE_REGION
aws cloudformation package --template-file aws/modl-prod/s3/s3-server-logs-bucket.yaml --output-template-file s3-server-logs-bucket.packaged.yaml --s3-bucket cf-templates--$THE_REGION--$THE_BUCKET_NAME_UNIQUIFIER--$THE_STAGE
aws cloudformation deploy --stack-name=$CURRENT_STACK_NAME --template-file=s3-server-logs-bucket.packaged.yaml --parameter-overrides Stage=$THE_STAGE --no-fail-on-empty-changeset
aws cloudformation update-termination-protection --stack-name $CURRENT_STACK_NAME --enable-termination-protection

# Enable server access logging for the CloudFormation templates bucket
aws cloudformation deploy --stack-name=cloud-formation-templates-bucket-$THE_REGION --parameter-overrides CostCenterTagValue="General Overhead" TheBucketName=cf-templates--$THE_REGION--$THE_BUCKET_NAME_UNIQUIFIER--$THE_STAGE EnableServerAccessLogging=true --template-file=aws/templates/s3/generic-bucket.yaml --no-fail-on-empty-changeset


#### S3 Buckets ####

# Static Website Hosting
CURRENT_STACK_NAME=general-downloads-bucket
aws cloudformation package --template-file aws/modl-prod/s3/general-downloads-bucket.yaml --output-template-file general-downloads-bucket.packaged.yaml --s3-bucket cf-templates--$THE_REGION--$THE_BUCKET_NAME_UNIQUIFIER--$THE_STAGE
aws cloudformation deploy --stack-name=$CURRENT_STACK_NAME --template-file=general-downloads-bucket.packaged.yaml --parameter-overrides Stage=$THE_STAGE --no-fail-on-empty-changeset
aws cloudformation update-termination-protection --stack-name $CURRENT_STACK_NAME --enable-termination-protection


# General Build resources (S3 Buckets and SSM Parameters)
## Note: the SSM Parameters need to be changed from String to SecureString and have the values entered (CloudFormation does not yet support SecureString)
CURRENT_STACK_NAME=codebuild-supporting-infrastructure
aws cloudformation package --template-file aws/modl-prod/codebuild-supporting-infrastructure.yaml --output-template-file codebuild-supporting-infrastructure.packaged.yaml --s3-bucket cf-templates--$THE_REGION--$THE_BUCKET_NAME_UNIQUIFIER--$THE_STAGE
aws cloudformation deploy --stack-name=$CURRENT_STACK_NAME --template-file=codebuild-supporting-infrastructure.packaged.yaml --parameter-overrides Stage=$THE_STAGE --no-fail-on-empty-changeset
aws cloudformation update-termination-protection --stack-name $CURRENT_STACK_NAME --enable-termination-protection



# clean up
rm *.packaged.yaml
