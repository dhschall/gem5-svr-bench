#!/bin/bash -eux


## Install bazel for fleetbench

if [ $(uname -m) == "aarch64" ]; then
        ARCH="arm64"
else
        ARCH="amd64"
fi

if [ $ARCH == "amd64" ]; then
  sudo apt install apt-transport-https curl gnupg -y
  curl -fsSL https://bazel.build/bazel-release.pub.gpg | gpg --dearmor >bazel-archive-keyring.gpg
  sudo mv bazel-archive-keyring.gpg /usr/share/keyrings
  echo "deb [arch=amd64 signed-by=/usr/share/keyrings/bazel-archive-keyring.gpg] https://storage.googleapis.com/bazel-apt stable jdk1.8" | sudo tee /etc/apt/sources.list.d/bazel.list
  sudo apt update && sudo apt install -y bazel zip unzip
else
  sudo apt install apt-transport-https curl gnupg -y
  wget https://github.com/bazelbuild/bazel/releases/download/7.4.1/bazel-7.4.1-linux-arm64
  chmod +x bazel-7.4.1-linux-arm64
  sudo apt update && sudo apt install -y zip unzip default-jdk libgoogle-perftools-dev
  sudo apt install -y gcc g++ libz-dev
fi


## Install fleetbench
git clone https://github.com/google/fleetbench.git

cd fleetbench
mkdir -p build

if [ $ARCH == "amd64" ]; then
  VERSION=c1d0f72
  git checkout $VERSION
  git apply ../fleetbench.patch
fi

## Build fleetbench

BENCHMARKS=()
BENCHMARKS+=("proto:proto_benchmark")
BENCHMARKS+=("swissmap:swissmap_benchmark")
BENCHMARKS+=("libc:mem_benchmark")
BENCHMARKS+=("tcmalloc:empirical_driver")
BENCHMARKS+=("compression:compression_benchmark")
BENCHMARKS+=("hashing:hashing_benchmark")
BENCHMARKS+=("stl:cord_benchmark")



if [ $ARCH == "amd64" ]; then
  for BENCHMARK in "${BENCHMARKS[@]}"; do
    BENCHMARK_NAME=$(echo $BENCHMARK | cut -d':' -f1)
    BENCHMARK_TARGET=$(echo $BENCHMARK | cut -d':' -f2)
    bazel --output_base=build run --config=opt fleetbench/${BENCHMARK_NAME}:${BENCHMARK_TARGET}
  done
else
  mv ../bazel-7.4.1-linux-arm64 .
  for BENCHMARK in "${BENCHMARKS[@]}"; do
    BENCHMARK_NAME=$(echo $BENCHMARK | cut -d':' -f1)
    BENCHMARK_TARGET=$(echo $BENCHMARK | cut -d':' -f2)
    ./bazel-7.4.1-linux-arm64 --output_base=build run --config=opt fleetbench/${BENCHMARK_NAME}:${BENCHMARK_TARGET}
    ./bazel-7.4.1-linux-arm64 --output_base=build run --config=opt fleetbench/libc:mem_benchmark
  done
fi


