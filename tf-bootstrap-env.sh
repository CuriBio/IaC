#!/bin/bash
SRCDIR=./src
INFRADIR=./infra/environments

function usage() {
  echo "Usage: $(basename $0) [-pw]" 2>&1
  echo "Provision test environment for workspace"
  echo "  -p              Deploy prod environment"
  echo "  -w WORKSPACE    The terraform workspace name"
  exit 1
}

# if no input argument found, exit the script with usage
if [[ ${#} -eq 0 ]]; then
   usage
fi

# default to running on test environment
ENV_TF=test

optstring=":pw:"
while getopts ${optstring} arg; do
  case ${arg} in
    p)
      ENV_TF=prod
      ;;
    w)
      WORKSPACE=${OPTARG}
      ;;
  esac
done

echo "Using workspace $WORKSPACE"

if [[ -n $WORKSPACE ]] && [[ $ENV_TF = 'prod' ]]; then
  echo "Prod environment doesn't support workspaces"
  exit 1
fi


# terragrunt init and select workspace if in test env
echo "$INFRADIR/$ENV_TF"

(cd $INFRADIR/$ENV_TF && terragrunt run-all init --terragrunt-non-interactive)
if [[ $ENV_TF = 'test' ]]; then
    echo "Select workspace $WORKSPACE"
    (cd $INFRADIR/$ENV_TF && (terragrunt run-all workspace select $WORKSPACE || terragrunt run-all workspace new $WORKSPACE))
fi

# # ECR needs to be created first so docker image can be pushed before the lambda is provisioned
(cd $INFRADIR/$ENV_TF/ecr && terragrunt plan --terragrunt-non-interactive)
(cd $INFRADIR/$ENV_TF/ecr && terragrunt apply --terragrunt-non-interactive --auto-approve)

# get ecr repo url and login
role_arn=$(cd $INFRADIR/$ENV_TF/ecr && terragrunt output --raw arn)
ecr_repo=$(cd $INFRADIR/$ENV_TF/ecr && terragrunt output --raw ecr_repository_url)
eval $(aws sts assume-role --role-arn $role_arn --role-session-name test | jq -r '.Credentials | "export AWS_ACCESS_KEY_ID=\(.AccessKeyId)\nexport AWS_SECRET_ACCESS_KEY=\(.SecretAccessKey)\nexport AWS_SESSION_TOKEN=\(.SessionToken)\n"')
aws ecr get-login-password --region us-east-1 | docker login --password-stdin --username AWS $ecr_repo
unset AWS_SECRET_ACCESS_KEY AWS_ACCESS_KEY_ID AWS_SESSION_TOKEN


# build images, push docker images to ecr
(cd $SRCDIR/lambdas/hello_world && ECR_REPO=$ecr_repo make build)
(cd $SRCDIR/lambdas/hello_world && ECR_REPO=$ecr_repo make tag)
(cd $SRCDIR/lambdas/hello_world && ECR_REPO=$ecr_repo make push)

# provision lambda
(cd $INFRADIR/$ENV_TF/service && terragrunt plan --terragrunt-non-interactive)
(cd $INFRADIR/$ENV_TF/service && terragrunt apply --terragrunt-non-interactive --auto-approve)
