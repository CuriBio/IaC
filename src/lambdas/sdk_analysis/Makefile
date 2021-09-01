.PHONY: build push tag
build:
	docker buildx build -t $(IMAGE):$(TAG) . --platform linux/amd64 --load
	#docker build -t $(IMAGE):$(TAG) . 
tag:
	docker tag $(IMAGE):$(TAG) $(ECR_REPO):$(TAG)
