import argparse
import logging
import os
import subprocess
import sys

def subprocess_stream(*args, capture=False, **kwargs):
    output = []
    try:
        with subprocess.Popen(*args, **kwargs, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as p:
            for line in p.stdout: 
                sys.stdout.buffer.write(line)
                sys.stdout.flush()
                output.append(line)
    except subprocess.CalledProcessError as e:
        logger.error(f'Failed {args}, {e}')
        sys.exit(1)

    return b''.join(output) if capture else None

def main():
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description='tf-deploy-env')
    parser.add_argument('--workspace', default='test', type=str, help='Terraform workspace name')
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--destroy', action='store_true')
    parser.add_argument('--no-color', action='store_true')
    parser.add_argument('--infra_dir', default='./infra/environments/', type=str, help='Terraform infrastructure directory')
    args = parser.parse_args()

    if args.workspace in ['prod', 'test', 'modl'] and args.destroy:
        logger.error(f"Workspace {args.workspace} can't be destroyed")
        sys.exit(1)

    #tfvars = '-var-file=' + {'prod': 'prod.tfvars', 'modl': 'modl.tfvars'}.get(args.workspace, 'test.tfvars')
    tfvars = ''
    shell_args = {'shell': True, 'cwd': args.infra_dir, 'env': os.environ}

    # init terraform and select workspace, create if it doesn't exist
    subprocess_stream(f'terragrunt run-all init --terragrunt-non-interactive {tfvars}', **shell_args)
    subprocess_stream(f'terragrunt run-all workspace select {args.workspace} || terragrunt run-all workspace new {args.workspace}', **shell_args)

    # if destroy then teardown and exit
    if args.destroy:
        subprocess_stream(f'terragrunt run-all destroy --terragrunt-non-interactive --auto-approve {tfvars}', **shell_args)
        subprocess_stream('terragrunt run-all workspace select default', **shell_args)
        subprocess_stream(f'terragrunt run-all workspace delete {args.workspace}', **shell_args)
        sys.exit(0)

    if not args.apply: # plan only
        colorize = '-no-color' if args.no_color else ''
        plan = subprocess_stream(f'terragrunt run-all plan --terragrunt-non-interactive {colorize} {tfvars}', capture=True, **shell_args)
        print(f'echo "::set-output name=plan_output::{plan.decode()}"')
    else: # apply infra
        subprocess_stream(f'terragrunt run-all apply --terragrunt-non-interactive --auto-approve {tfvars}', **shell_args)

if __name__ == "__main__":
    main()
