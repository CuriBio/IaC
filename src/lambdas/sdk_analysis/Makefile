.PHONY: build push tag
build:
	docker build -t $(IMAGE):$(TAG) . 

	# TODO fix this
	# if you're using an arm based machine you'll have to build with dockerx instead
	# docker buildx build -t $(IMAGE):$(TAG) . --platform linux/amd64 --load
tag:
	docker tag $(IMAGE):$(TAG) $(ECR_REPO):$(TAG)
