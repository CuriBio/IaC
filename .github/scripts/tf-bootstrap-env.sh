#!/bin/bash
set -ex

SRCDIR=./src
INFRADIR=./infra/environments
ENV_TF=test

function usage() {
  echo "Usage: $(basename $0) [-pwa]" 2>&1
  echo "Provision test environment for workspace"
  echo "  -p              Deploy prod environment"
  echo "  -w WORKSPACE    The terraform workspace name"
  echo "  -a              Apply infrastructure afer plan"
  echo "  -d              Destroy infrastructure"
  exit 1
}

# if no input argument found, exit the script with usage
if [[ ${#} -eq 0 ]]; then
   usage
   exit 1
fi

optstring=":adpw:"
while getopts ${optstring} arg; do
  case ${arg} in
    p)
      ENV_TF=prod
      ;;
    w)
      WORKSPACE=${OPTARG}
      ;;
    a)
      APPLY_PLAN=true
      ;;
    d)
      DESTROY=true
      ;;
  esac
done


if [[ -n $WORKSPACE ]] && [[ $ENV_TF = 'prod' ]]; then
  echo "Prod environment doesn't support workspaces"
  exit 1
fi

echo "$INFRADIR/$ENV_TF"

# terragrunt init and select workspace if in test env
if [[ $ENV_TF = 'test' ]]; then
  # ECR needs to be created first so docker image can be pushed before the lambda is provisioned
  (cd $INFRADIR/$ENV_TF/ecr && terragrunt init --terragrunt-non-interactive)
  (cd $INFRADIR/$ENV_TF/ecr && (terragrunt workspace select $WORKSPACE || terragrunt workspace new $WORKSPACE))
  (cd $INFRADIR/$ENV_TF/ecr && terragrunt apply --terragrunt-non-interactive --auto-approve)


  # get ecr repo url and login
  role_arn=$(cd $INFRADIR/$ENV_TF/ecr && terragrunt output --raw arn)
  TF_VAR_ecr_repository_url=$(cd $INFRADIR/$ENV_TF/ecr && terragrunt output --raw ecr_repository_url)

  (cd $INFRADIR/$ENV_TF/service && terragrunt init --terragrunt-non-interactive)
  (cd $INFRADIR/$ENV_TF/service && (terragrunt workspace select $WORKSPACE || terragrunt workspace new $WORKSPACE))
fi


if [[ $DESTROY = true ]]; then
  if [[ $ENV_TF = 'prod' ]]; then
    echo "Destroy can't be used for prod environment"
    exit 1
  fi

  (cd $INFRADIR/$ENV_TF && terragrunt run-all destroy --terragrunt-non-interactive --auto-approve)
  (cd $INFRADIR/$ENV_TF && terragrunt run-all workspace select default)
  (cd $INFRADIR/$ENV_TF && terragrunt run-all workspace delete $WORKSPACE)
  exit 0
fi



# docker login needs the assumed role to push images to ecr
eval $(aws sts assume-role --role-arn $role_arn --role-session-name terraform | jq -r '.Credentials | "export AWS_ACCESS_KEY_ID=\(.AccessKeyId)\nexport AWS_SECRET_ACCESS_KEY=\(.SecretAccessKey)\nexport AWS_SESSION_TOKEN=\(.SessionToken)\n"')
aws ecr get-login-password --region us-east-1 | docker login --password-stdin --username AWS $TF_VAR_ecr_repository_url
unset AWS_SECRET_ACCESS_KEY AWS_ACCESS_KEY_ID AWS_SESSION_TOKEN

# build images, push docker images to ecr
(cd $SRCDIR/lambdas/hello_world && ECR_REPO=$ecr_repo make build)
(cd $SRCDIR/lambdas/hello_world && ECR_REPO=$ecr_repo make tag)
(cd $SRCDIR/lambdas/hello_world && ECR_REPO=$ecr_repo make push)

# provision services
plan_output=$(cd $INFRADIR/$ENV_TF/service && terragrunt plan --terragrunt-non-interactive)
echo "::set-output name=plan_output::$plan_output"

if [[ $APPLY_PLAN = true ]]; then
  (cd $INFRADIR/$ENV_TF/service && terragrunt apply --terragrunt-non-interactive --auto-approve)
fi

#echo $plan_output
