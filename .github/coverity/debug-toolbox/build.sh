#!/bin/bash

set -a
source .env
set +a

#  --no-cache \
docker build \
  --build-arg GITHUB_PAT=${GITHUB_PAT} \
  --build-arg COV_USER=${COV_USER} \
  --build-arg COV_PASS=${COV_PASS} \
  -t cov-test \
  -f Dockerfile \
  ..
