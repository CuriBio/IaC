#!/bin/bash
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
  (cd $INFRADIR/$ENV_TF && terragrunt run-all init --terragrunt-non-interactive)
  (cd $INFRADIR/$ENV_TF && (terragrunt run-all workspace select $WORKSPACE || terragrunt run-all workspace new $WORKSPACE))

  if [[ $DESTROY = true ]]; then
      (cd $INFRADIR/$ENV_TF && terragrunt run-all destroy --terragrunt-non-interactive --auto-approve)
      (cd $INFRADIR/$ENV_TF && terragrunt run-all workspace select default)
      (cd $INFRADIR/$ENV_TF && terragrunt run-all workspace delete $WORKSPACE)
      exit 0
  fi
fi

# provision services
plan_output=$(cd $INFRADIR/$ENV_TF && terragrunt run-all plan --terragrunt-non-interactive)
echo "::set-output name=plan_output::$(echo $plan_output)"

if [[ $APPLY_PLAN = true ]]; then
  (cd $INFRADIR/$ENV_TF && terragrunt run-all apply --terragrunt-non-interactive --auto-approve)
fi

#echo $plan_output
