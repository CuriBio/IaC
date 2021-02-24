Preqequisites:
  * terragrunt
  * an aws admin account that will be used to assume role of the different deploy environments
    * have an aws profile setup for this account, e.g. `curi_admin`
  * aws account(s) profile for each environment with iam user and api access (access_key/secret_key)
    Currently the environments use these profile names, e.g.

      .. code-block:: bash

        $ cat ~/.aws.credentials
        [curi_modl]
        aws_access_key_id=<curi_modl access key>
        aws_secret_access_key=<curi_modl secret access key>

        [curi_prod]
        aws_access_key_id=<curi_prod access key>
        aws_secret_access_key=<curi_prod secret access key>

        [curi_test]
        aws_access_key_id=<curi_prod access key>
        aws_secret_access_key=<curi_prod secret access key>

To bootstrap infrastructure for each environment:
  * set `TF_VAR_account_id` to the value of the admin account, e.g. `export TF_VAR_account_id=123456789012`
  * `cd ./bootstrap/<env>`
  * check ./bootstrap/<env>/terragrunt.hcl is using the correct profile, change if you want to use different names
  * run `terragrunt plan --terragrunt-non-interactive`
  * verify the plan makes sense
  * run `terragrunt apply --terragrunt-non-interactive`
  * Note the arn output value, for each env add the arn string to
    `./environment/<env>/terragrunt.hcl` for the `role_arn` key in the `assume_role` block for the aws provider


To provision an environment, after it has been bootstrapped:
  * `cd ./bootstrap/<env>`
  * optionally you can export the `AWS_PROFILE` environment variable to the aws profile you plan to deploy with,
    `export AWS_PROFILE=curi_admin` or provide that value when running the terragrunt command.
  * run `AWS_PROFILE=curi_admin terragrunt run-all plan --terragrunt-non-interactive`
  * verify plan looks good
  * run `AWS_PROFILE=curi_admin terragrunt run-all apply --terragrunt-non-interactive`


If all the command ran successfully the infrastructure is fully deployed, make a pr to check-in the changes to the `terragrunt.hcl`
files with the new arn values.
