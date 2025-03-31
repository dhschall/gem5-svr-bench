
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

# Execute this script using
#   ./setup_all_functions.sh <results>

set -xu

ARCH=$(dpkg --print-architecture)


GEM5=./../build/ALL/gem5.opt
GEM5_CONFIG=./gem5-configs/fs-fdp.py

KERNEL="./wkdir/$ARCH/kernel"
DISK_IMAGE="./wkdir/$ARCH/disk.img"









################################################################################
sudo chown $(id -u) /dev/kvm



BENCHMARKS=()
BENCHMARKS+=("nodeapp")
BENCHMARKS+=("nodeapp-nginx")
BENCHMARKS+=("mediawiki")
BENCHMARKS+=("mediawiki-nginx")
BENCHMARKS+=("proto")
BENCHMARKS+=("swissmap")
BENCHMARKS+=("libc")
BENCHMARKS+=("tcmalloc")
BENCHMARKS+=("compression")
BENCHMARKS+=("hashing")
BENCHMARKS+=("stl")






# Define the output file of your run
RESULTS_DIR="./results/$ARCH/setup"



for bm in "${BENCHMARKS[@]}";
do
    OUTDIR=$RESULTS_DIR/${bm}/

    ## Create output directory
    mkdir -p $OUTDIR

    screen -d -S "setup-$bm" -m bash -c "$GEM5 \
        --outdir=$OUTDIR \
            $GEM5_CONFIG \
                --kernel $KERNEL \
                --disk $DISK_IMAGE \
                --workload ${bm} \
                --mode=setup \
            > $OUTDIR/gem5.log 2>&1"

done


