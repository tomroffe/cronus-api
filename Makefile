VERSION = latest
PROJECT = cronus
NAME = $(PROJECT)-api
ECR_REGION = eu-west-1
ECR_ACCOUNT_NUMBER = 625174228527
ECR_REPO = $(ECR_ACCOUNT_NUMBER).dkr.ecr.$(ECR_REGION).amazonaws.com
APP_IMAGE = $(ECR_REPO)/$(NAME):$(VERSION)
NO_CACHE = false
GIT_VERSION = $(shell git rev-parse --short HEAD)

build:
	docker build -t $(NAME) .
	docker tag $(NAME):$(VERSION) $(APP_IMAGE)
.PHONY: build

run:
	#docker run -p 8844:8844 -it cronus-api:latest gunicorn -w 1 -b 0.0.0.0:8844  backend.app:app
	docker run -p 8844:8844 cronus-api
.PHONY: run

push: build
	$(shell aws ecr get-login --no-include-email --region eu-west-1)
	docker push $(APP_IMAGE)
	#aws ecs update-service --cluster $(CLUSTER) --service $(NAME) --force-new-deployment
.PHONY: push

ver:
	@echo '$(APP_IMAGE)'
	@echo '$(GIT_VERSION)'
.PHONY: ver

