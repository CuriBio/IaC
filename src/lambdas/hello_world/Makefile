.PHONY: build push tag
build:
	docker build -t $(IMAGE):$(TAG) .
tag:
	docker tag $(IMAGE):$(TAG) $(ECR_REPO):$(IMAGE)_$(TAG)
