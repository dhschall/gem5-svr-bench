#!/bin/bash

# MIT License
#
# Copyright (c) 2022 EASE lab, University of Edinburgh
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
#
# Authors: David Schall

MKFILE := $(abspath $(lastword $(MAKEFILE_LIST)))
ROOT 		:= $(abspath $(dir $(MKFILE))/../)

ARCH   ?= amd64

# Go parameters
GOCMD=$(shell which go)
GOCMD=/usr/local/go/bin/go

.PHONY: m5ops
.PHONY: clean
.PHONY: m5files	



dep_install:
	sudo apt-get update \
  	&& sudo apt-get install -y \
		gcc-arm-linux-gnueabihf gcc-aarch64-linux-gnu device-tree-compiler


## Configure the m5 address depending on the architecture
ifeq ($(ARCH), arm64)
M5OP_ADDR=0x10010000
else
M5OP_ADDR=0xffff0000
endif

## Assembly files
m5files:
	cp $(ARCH)/* .


## m5 ops library -------------------------
CC = gcc
AR = ar
RANLIB = ranlib
ifeq ($(ARCH), arm64)
ifeq ($(shell uname -i),x86_64)
CC = aarch64-linux-gnu-gcc
AR = aarch64-linux-gnu-ar
RANLIB = aarch64-linux-gnu-ranlib
endif
endif

CFLAGS = -g -fPIC

%.o : %.S
		$(CC) -o $@ $< -c -g -fPIC

SFILES := m5op.S m5op_addr.S
OBJFILES := m5_mmap.o m5op.o m5op_addr.o




m5_mmap.o : m5_mmap.c
		$(CC) -DM5OP_ADDR=$(M5OP_ADDR) -o $@ $< -c -g -fPIC

m5ops: $(OBJFILES)
		$(AR) rc -o lib$@.a $^
		$(RANLIB) lib$@.a

m5lib: m5files
	$(MAKE) m5ops
## ----------------------------------------



clean:
	rm *.o
	rm *.a
	rm *.S


