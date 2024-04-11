# EKS SETUP

Currently this is only hosting the webpage aspect as it is smaller than ML
You will need to be logged into an aws account on your command line

## USED FILES
- django-pod.yaml
- django-svc.yaml

## Docker Hub

Currently using colemk/webserver:2.0. I find that pushing new updates to dockerhub (after building with compose) did not update internal python files. To get around this I changed the tag and individually built the docker file with docker build. (I need to test if docker build on its own will fix this internal file not updating thing)

## Needed Tools
- aws command line tools
- eksctl
- kubectl

## Order of Operations

