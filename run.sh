#!/bin/bash

sudo docker run -it --mount type=bind,source=/proc,target=/sandbox/proc,readonly \
	--mount type=bind,source=/sys,target=/sandbox/sys,readonly \
	--mount type=bind,source=/dev,target=/sandbox/dev,readonly chroot
