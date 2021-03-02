TAG = $(shell date +%Y-%m-%d)
IMAGE = $(shell basename `pwd`)

.PHONY: build push tag

build:
	docker build -t $(IMAGE):$(TAG) .

tag:
	docker tag $(IMAGE):$(TAG) $(ECR_REPO):$(TAG)

push:
	docker push $(ECR_REPO):$(TAG)

