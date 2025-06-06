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
ARCH   ?= $(shell dpkg --print-architecture)

# Go parameters
GOCMD=$(shell which go)
GOCMD=/usr/local/go/bin/go

.PHONY: clean

OUTPUT_DIR=output/$(ARCH)
BIN=$(OUTPUT_DIR)/http-client

dep_install:
	sudo apt-get update \
  	&& sudo apt-get install -y \
		gcc-arm-linux-gnueabihf gcc-aarch64-linux-gnu device-tree-compiler


install_go:
	wget https://golang.org/dl/go1.23.4.linux-$(ARCH).tar.gz
	rm -rf /usr/local/go && tar -C /usr/local -xzf go1.23.4.linux-$(ARCH).tar.gz
	export PATH=$PATH:/usr/local/go/bin
	rm go1.23.4.linux-$(ARCH).tar.gz
	go version

$(OUTPUT_DIR):
	mkdir -p $@

$(BIN): $(OUTPUT_DIR) main.go
	GOOS=linux GOARCH=$(ARCH) go build -o $@ -v main.go

all: $(BIN)

clean:
	go clean
	rm -rf output