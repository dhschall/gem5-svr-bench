
#!/bin/bash

# MIT License
#
# Copyright (c) 2025 Technical University of Munich
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

set -xu

GEM5=./../build/ARM/gem5.opt
GEM5_CONFIG=./gem5-configs/fs-fdp-multi.py

WIDTH=32
FACTOR=4
PREDPERCYCLE=4
SET=""
DATA_POINTS=10

ARCH="arm64"
CPU_TYPE="o3"

INF_TAGE=0 
BIG_SQUASH=0 
INF_PHAST=0
GIANT_CACHE=0
fbInFTQ=0

BENCHMARKS=()
BENCHMARKS+=("nodeapp")
#BENCHMARKS+=("nodeapp-nginx")
#BENCHMARKS+=("proto")
#BENCHMARKS+=("swissmap")
BENCHMARKS+=("libc")
#BENCHMARKS+=("tcmalloc")
BENCHMARKS+=("compression")
#BENCHMARKS+=("hashing")
#BENCHMARKS+=("stl")
#BENCHMARKS+=("dacapo-cassandra")
#BENCHMARKS+=("dacapo-h2")
#BENCHMARKS+=("dacapo-h2o")
#BENCHMARKS+=("dacapo-kafka")
BENCHMARKS+=("dacapo-luindex")
BENCHMARKS+=("dacapo-lusearch")
#BENCHMARKS+=("dacapo-spring")
#BENCHMARKS+=("dacapo-tomcat")
#BENCHMARKS+=("renaissance-http")
#BENCHMARKS+=("renaissance-chirper")

declare -A ticks
ticks["nodeapp"]=156519779329548
#ticks["nodeapp-nginx"]=0
ticks["proto"]=88168143393873
#ticks["swissmap"]=0
ticks["libc"]=88198009891479 
#ticks["tcmalloc"]=0
ticks["compression"]=88049036099394
#ticks["hashing"]=0
ticks["stl"]=87949837500957
ticks["dacapo-cassandra"]=3524023900880667
ticks["dacapo-h2"]=2050521473086200
ticks["dacapo-h2o"]=142466000732325
ticks["dacapo-kafka"]=340527892913658
ticks["dacapo-luindex"]=146136460986936
ticks["dacapo-lusearch"]=386843744812212
ticks["dacapo-spring"]=409195183575969
ticks["dacapo-tomcat"]=817015457226816
ticks["renaissance-http"]=174877618558770
ticks["renaissance-chirper"]=174782875564602



# Parsing args
# i set inf_tage, -b set big squash, -g set giant cache -m set inf_phast
while getopts "w:f:p:s:d:ibmgq" opt; do
    case $opt in
    w) WIDTH=$OPTARG ;;
    f) FACTOR=$OPTARG ;;
    p) PREDPERCYCLE=$OPTARG ;;
    s) SET=$OPTARG ;;
    d) DATA_POINTS=$OPTARG ;;
    i) INF_TAGE=1 ;;
    b) BIG_SQUASH=1 ;;
    m) INF_PHAST=1 ;;
    g) GIANT_CACHE=1 ;;
    q) fbInFTQ=1 ;;
    ?) echo "invalid option" ;;
    esac
done

SIM_FLAGS=""
if [ "$INF_TAGE" -eq 1 ]; then
    SIM_FLAGS="$SIM_FLAGS --inf_tage"
fi
if [ "$BIG_SQUASH" -eq 1 ]; then
    SIM_FLAGS="$SIM_FLAGS --big_squash"
fi
if [ "$INF_PHAST" -eq 1 ]; then
    SIM_FLAGS="$SIM_FLAGS --inf_phast"
fi
if [ "$GIANT_CACHE" -eq 1 ]; then
    SIM_FLAGS="$SIM_FLAGS --giant_cache"
fi
if [ "$fbInFTQ" -eq 1 ]; then
    SIM_FLAGS="$SIM_FLAGS --fbInFTQ"
fi

# Set experiment name

EXPERIMENT="w${WIDTH}_f${FACTOR}_ppc${PREDPERCYCLE}"

# ---------------------

# Architecture to ISA mapping
if [ "$ARCH" == "amd64" ]; then
    ISA="X86"
elif [ "$ARCH" == "arm64" ]; then
    ISA="Arm"
elif [ "$ARCH" == "risc" ]; then
    ISA="RiscV"
else
    echo "Unsupported architecture: $ARCH"
    exit 1
fi

KERNEL="./wkdir/$ARCH/kernel"
DISK_IMAGE="./wkdir/$ARCH/disk.img"

# Define the output file of your run
RESULTS_DIR="./results/$ARCH/$EXPERIMENT"

if [ "$SET" != "" ]; then 
    RESULTS_DIR="./results/$ARCH/$SET/${SET}_${EXPERIMENT}"
fi

if ! pgrep -x "pueued" > /dev/null
then
    pueued -d
fi

PGROUP="$ARCH-$EXPERIMENT"

if [ "$SET" != "" ]; then 
    PGROUP="$ARCH-$SET-$EXPERIMENT"
fi
pueue group add -p 100 "$PGROUP" || true

sudo chown $(id -u) /dev/kvm


for bm in "${BENCHMARKS[@]}"; 
do
    OUTDIR=$RESULTS_DIR/${bm}/

    ## Create output directory
    mkdir -p $OUTDIR

    pueue add -g "$PGROUP" -l "$EXPERIMENT-$bm" -- "$GEM5 \
        --outdir=$OUTDIR \
            $GEM5_CONFIG \
                --width $WIDTH \
                --factor $FACTOR \
                --ppc $PREDPERCYCLE \
                --fdp \
                --kernel $KERNEL \
                --disk $DISK_IMAGE \
                --workload ${bm} \
                --isa $ISA \
                --cpu-type $CPU_TYPE \
                --mode=eval \
                --data_point $DATA_POINTS \
                ${SIM_FLAGS} \
            > $OUTDIR/gem5.log 2>&1"

done


