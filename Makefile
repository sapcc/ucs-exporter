SHELL       := /bin/sh
IMAGE       := ucs-exporter
VERSION     := 0.1

### Executables
DOCKER := docker

### Docker Targets 

.PHONY: build
build: 
	$(DOCKER) build -t $(IMAGE):$(VERSION) --no-cache --rm .

.PHONY: push 
push: 
	$(DOCKER) push $(IMAGE):$(VERSION)
