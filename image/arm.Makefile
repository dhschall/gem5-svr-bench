#!/bin/bash

# MIT License
#
# Copyright (c) 2022 David Schall and EASE lab
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

MKFILE 		:= $(abspath $(lastword $(MAKEFILE_LIST)))
ROOT 		:= $(abspath $(dir $(MKFILE))/../)


## User specific inputs
RESOURCES 	?= $(ROOT)/image/
WORKING_DIR ?= $(ROOT)/wkdir/
ARCH		?= arm64

ifeq ($(ARCH), amd64)
	_ARCH=X86
else ifeq ($(ARCH), arm64)
	_ARCH=ARM
endif


## Machine parameter
MEMORY 	:= 16G
CPUS    := 4
CPU 	?= host -enable-kvm


## Required resources
KERNEL 		?= $(RESOURCES)/vmlinux-jammy-arm64
CLIENT 		?= $(RESOURCES)/test-client-arm64
DISK		?= $(RESOURCES)/disk-image.qcow2




## Dependencies -------------------------------------------------
## Check and install all dependencies necessary to perform function
##
# dep_install:
# 	sudo pip install -U niet



##################################################################
## Build the working directory ----------------------------
#
WK_KERNEL 	:= $(WORKING_DIR)/kernel
WK_DISK 	:= $(WORKING_DIR)/disk.img
WK_CLIENT	:= $(WORKING_DIR)/test-client

build-wkdir: $(WORKING_DIR) \
	$(WK_DISK) $(WK_KERNEL) $(WK_CLIENT) \

$(WORKING_DIR):
	@echo "Create folder: $(WORKING_DIR)"
	mkdir -p $@

$(WK_KERNEL): $(KERNEL)
	cp $< $@

$(WK_CLIENT): $(CLIENT)
	cp $< $@


# Create the disk image from the base image
$(WK_DISK): $(DISK)
	qemu-img convert $< $@


## Run Emulator -------------------------------------------------
# Do the actual emulation run
# The command will boot an instance.
# Then it will listen to port 3003 to retive a run script
# This run script will be the one we provided.
# run_emulator:
# 	sudo qemu-system-x86_64 \
# 		-nographic \
# 		-cpu host -enable-kvm \
# 		-smp ${CPUS} \
# 		-m ${MEMORY} \
# 		-drive file=$(WK_DISK),format=raw \
# 		-kernel $(WK_KERNEL) \
# 		-append 'console=ttyS0 root=/dev/hda2'

FLASH0 := $(WORKING_DIR)/flash0.img
FLASH1 := $(WORKING_DIR)/flash1.img

$(FLASH0):
	cp /usr/share/qemu-efi-aarch64/QEMU_EFI.fd $@
	truncate -s 64M $@

$(FLASH1):
	truncate -s 64M $@


run_emulator_arm: $(FLASH0) $(FLASH1)
	sudo qemu-system-aarch64 \
		-nographic \
		-M virt \
		-machine gic-version=max \
		-cpu host -enable-kvm \
		-smp ${CPUS} -m ${MEMORY} \
		-device e1000,netdev=net0 \
    	-netdev type=user,id=net0,hostfwd=tcp:127.0.0.1:5555-:22  \
		-drive file=$(WK_DISK),format=raw \
		-drive file=$(FLASH0),format=raw,if=pflash -drive file=$(FLASH1),format=raw,if=pflash \
		-kernel $(WK_KERNEL) \
		-append 'console=ttyAMA0 earlyprintk=ttyAMA0 lpj=7999923 root=/dev/vda2'



# run_emulator_arm:
# 	sudo qemu-system-aarch64 -M virt -enable-kvm -cpu host -m 2048 \
# 		-kernel $(WK_KERNEL) \
# 		-append 'console=ttyAMA0 earlyprintk=ttyAMA0 lpj=7999923 root=/dev/vda2 rw' \
# 		-drive file=wkdir/disk.img,format=raw,id=hd \
# 		-no-reboot \
# 		-device e1000,netdev=net0 \
# 		-netdev type=user,id=net0,hostfwd=tcp:127.0.0.1:5555-:22  \
# 		-nographic

run: run_emulator_arm
run-arm64: run_emulator_arm


RED=\033[0;31m
GREEN=\033[0;32m
NC=\033[0m # No Color
