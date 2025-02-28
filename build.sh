#!/bin/bash

docker build -t fortis-iso .
docker run --rm --privileged -v $(pwd)/build:/home/builduser/build fortis-iso
