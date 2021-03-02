include {
  path = find_in_parent_folders()
}

dependency "ecr" {
  config_path = "../ecr"
}

inputs = {
  ecr_repository_url = dependency.ecr.outputs.ecr_repository_url
}
