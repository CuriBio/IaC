#!/bin/bash
# To run: sh create-in-order.sh
set -ex # exit if command fails and display commands https://www.peterbe.com/plog/set-ex

# initially create the bucket for cloud formation templates without any server access logging enabled (because the bucket for that does not yet exist)
aws cloudformation deploy --stack-name=cloud-formation-templates-bucket-us-east-1 --parameter-overrides TheBucketName=cf-templates--us-east-1--curi-bio--prod EnableServerAccessLogging=false --template-file=aws/templates/s3/generic-bucket.yaml

# package and deploy the S3 bucket to hold Server Access Logs
aws cloudformation package --template-file aws/modl-prod/s3-server-logs-bucket.yaml --output-template-file s3-server-logs-bucket.packaged.yaml --s3-bucket cf-templates--us-east-1--curi-bio--prod
aws cloudformation deploy --stack-name=s3-server-logs-bucket-us-east-1 --template-file=s3-server-logs-bucket.packaged.yaml --parameter-overrides Stage=prod

# Enable server access logging for the CloudFormation templates bucket
aws cloudformation deploy --stack-name=cloud-formation-templates-bucket-us-east-1 --parameter-overrides TheBucketName=cf-templates--us-east-1--curi-bio--prod EnableServerAccessLogging=true --template-file=aws/templates/s3/generic-bucket.yaml

#### S3 Buckets ####


# Build artifacts and Build Resources
aws cloudformation package --template-file aws/model-prod/s3/build-artifacts-bucket.yaml --output-template-file build-artifacts-bucket.packaged.yaml --s3-bucket cf-templates--us-east-1--curi-bio--prod
aws cloudformation deploy --stack-name=build-artifacts-bucket --template-file=build-artifacts-bucket.packaged.yaml --parameter-overrides Stage=prod

aws cloudformation package --template-file aws/model-prod/build-resources.yaml --output-template-file build-resources.packaged.yaml --s3-bucket cf-templates--us-east-1--curi-bio--prod
aws cloudformation deploy --stack-name=build-resources --template-file=build-resources.packaged.yaml --parameter-overrides Stage=prod

# Static Website Hosting
aws cloudformation package --template-file aws/model-prod/s3/general-downloads-bucket.yaml --output-template-file general-downloads-bucket.packaged.yaml --s3-bucket cf-templates--us-east-1--curi-bio--prod
aws cloudformation deploy --stack-name=general-downloads-bucket --template-file=general-downloads-bucket.packaged.yaml

aws cloudformation package --template-file aws/model-prod/s3/software-downloads-bucket.yaml --output-template-file software-downloads-bucket.packaged.yaml --s3-bucket cf-templates--us-east-1--curi-bio--prod
aws cloudformation deploy --stack-name=software-downloads-bucket --template-file=software-downloads-bucket.packaged.yaml

# clean up
rm *.packaged.yaml
