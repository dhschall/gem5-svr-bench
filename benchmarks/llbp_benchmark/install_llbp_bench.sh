#!/bin/bash -eux

curl https://sh.rustup.rs -sSf | sh -s -- -y

. "$HOME/.cargo/env"

git clone https://github.com/shadowcpy/llbp_benchmark

cd llbp_benchmark

./build.sh