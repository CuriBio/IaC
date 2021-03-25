set -ex
# adapted from https://terragrunt.gruntwork.io/docs/getting-started/install/
sudo apt-get update
sudo apt-get install wget unzip
# update this to the version you want to install
sudo wget https://github.com/gruntwork-io/terragrunt/releases/download/v0.28.16/terragrunt_linux_amd64

# rename the file
mv terragrunt_linux_amd64 terragrunt

# apply permissions
sudo chmod u+x terragrunt

# move to path
sudo mv terragrunt /usr/local/bin/terragrunt

sudo terragrunt -v
