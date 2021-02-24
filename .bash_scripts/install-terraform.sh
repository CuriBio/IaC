set -ex
# adapted from https://phoenixnap.com/kb/how-to-install-terraform-centos-ubuntu
sudo apt-get update
sudo apt-get install wget unzip
# update this to the version you want to install
sudo wget https://releases.hashicorp.com/terraform/0.14.7/terraform_0.14.7_linux_amd64.zip

sudo unzip terraform_0.14.7_linux_amd64.zip –d /usr/local/bin

terraform –v


# install terragrunt v0.28.7
sudo wget -q -O /usr/local/bin/terragrunt "https://github.com/gruntwork-io/terragrunt/releases/download/v0.28.7/terragrunt_linux_amd64"
sudo chmod +x /usr/local/bin/terragrunt
terragrunt -v
