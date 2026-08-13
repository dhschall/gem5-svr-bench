

set -x


GEM5=/home/david/g5/tmp/gem5-phast/build/ARM/gem5.opt
CONFIG=./gem5-configs/all-simpoint-run.py

SIMPOINT_SPEC=/share/david/spec/arm64/simpoints_200M_v2/
CHECKPOINT_SPEC=/share/david/spec/arm64/checkpoints_200M_v2/
SIMPOINT_SVR=/share/david/svr/arm64/v2/simpoints_200M/
CHECKPOINT_SVR=/share/david/svr/arm64/v2/checkpoints_200M/
KERNEL=/share/david/svr/arm64/v2/kernel
DISK_IMAGE=/share/david/svr/arm64/v2/disk.img

ARCH="arm64"
CPU_TYPE="o3"
FLAGS=""
PGROUP="test"


#------------------------




BMS=()
BMS+=("nodeapp")

BMS+=("mediawiki")
BMS+=("proto")
# lusearch - voter not run for exploration
BMS+=("dacapo-lusearch")
BMS+=("swissmap")
BMS+=("benchbase-otmetrics")

BMS+=("tcmalloc")
BMS+=("benchbase-voter")
BMS+=("stl")

## Java BMS

BMS+=("dacapo-h2")
BMS+=("dacapo-h2o")
BMS+=("dacapo-kafka")
BMS+=("dacapo-luindex")

BMS+=("dacapo-spring")
BMS+=("dacapo-tomcat")
BMS+=("renaissance-http")
BMS+=("benchbase-twitter")

BMS+=("benchbase-tatp")
BMS+=("benchbase-resourcestresser")
BMS+=("benchbase-epinions")
BMS+=("benchbase-ycsb")
BMS+=("benchbase-seats")

BMS+=("benchbase-sibench")
BMS+=("benchbase-noop")
BMS+=("benchbase-smallbank")


##### SPEC
BMS+=("502.gcc_r.gcc-pp.opts-O3_-finline-limit_36000")
BMS+=("505.mcf_r.inp")
BMS+=("523.xalancbmk_r.xalanc")
BMS+=("531.deepsjeng_r.ref")
BMS+=("541.leela_r.ref")

BMS+=("500.perlbench_r.checkspam")
# BMS+=("500.perlbench_r.diffmail")
BMS+=("557.xz_r.cpu2006docs")
BMS+=("525.x264_r.x264")

# BMS=()

BMS+=("520.omnetpp_r.general")
# BMS+=("557.xz_r.cld")
BMS+=("557.xz_r.input")

BMS+=("508.namd_r.apoa1")
BMS+=("510.parest_r.ref")
BMS+=("511.povray_r.ref")
BMS+=("519.lbm_r.ref")
BMS+=("526.blender_r.ref")
BMS+=("538.imagick_r.ref")
BMS+=("544.nab_r.ref")



# ## SUBSET
# BMS=()
# BMS+=("nodeapp")
# # BMS+=("mediawiki")
# # BMS+=("compression")
# # BMS+=("dacapo-spring")
# # BMS+=("dacapo-luindex")
# # BMS+=("dacapo-lusearch")
# # BMS+=("renaissance-http")
# # BMS+=("renaissance-chirper")
# # BMS+=("benchbase-epinions")

# # BMS+=("500.perlbench_r.checkspam")
# BMS+=("502.gcc_r.gcc-pp.opts-O3_-finline-limit_36000")
# # BMS+=("505.mcf_r.inp")
# # BMS+=("523.xalancbmk_r.xalanc")
# # BMS+=("531.deepsjeng_r.ref")
# # BMS+=("541.leela_r.ref")
# # BMS+=("557.xz_r.cpu2006docs")


## Baseline ------------------
FLAGS=" "
EXPERIMENT="baseline-noFDP"

# ## Baseline ------------------
# FLAGS="--fdp "
# EXPERIMENT="baseline"


## BP latency ------------------
FLAGS="--fdp --modelBpuLatency"
EXPERIMENT="baseline-bpuLat"

# ## Two taken ------------------
# FLAGS="--fdp --takenPredPerCycle=2 --feParallelism=4"
# EXPERIMENT="twoTaken"

## Two taken, fetch in FTQ ------------------
FLAGS="--fdp --takenPredPerCycle=2 --feParallelism=4 --fetchDataInFTQ"
EXPERIMENT="twoTaken-parallelfetch"

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


# GEM5="${GEM5} --debug-file=dbg.out --debug-flags=O3PipeView"

# Define the output file of your run
RESULTS_DIR="./results/$EXPERIMENT"


if ! pgrep -x "pueued" > /dev/null
then
    pueued -d
fi

# PGROUP="yongji-l1BTB"


pueue group add -p 100 "$PGROUP" || true

sudo chown $(id -u) /dev/kvm


for bm in "${BMS[@]}"; do

    if [[ $bm == 5* ]]; then
        CHECKPOINT_BASE=$CHECKPOINT_SPEC
        SIMPOINT_BASE=$SIMPOINT_SPEC
    else
        CHECKPOINT_BASE=$CHECKPOINT_SVR
        SIMPOINT_BASE=$SIMPOINT_SVR
    fi

    #find sid with the max weight
    WEIGHT_FILE="${SIMPOINT_BASE}${bm}/results.weights"

    SIMPTS_FILE="${SIMPOINT_BASE}${bm}/results.simpts"

    # Find the sid with the max weight
    WEIGHT_FILE="${SIMPOINT_BASE}${bm}/results.weights"
    if [ ! -f "$WEIGHT_FILE" ]; then
        echo "Warning: Weight file $WEIGHT_FILE not found. Skipping $bm."
        continue
    fi

    # results.simpts: <phase> <index>
    # results.weights: <weight> <index>
    max_phase=$(join -1 2 -2 2 <(sort -k2,2 "$SIMPTS_FILE") <(sort -k2,2 "$WEIGHT_FILE") | sort -k3,3nr | head -n 1 | awk '{print $2}')

    sid=$(awk '{print $1}' "$SIMPTS_FILE" | sort -n | grep -nx "$max_phase" | cut -d: -f1)
    sid=$((sid - 1))

    echo "For benchmark $bm, running single simpoint sid $sid with max weight"


    RESDIR=${RESULTS_DIR}/$bm/

    mkdir -p $RESDIR

    pueue add -g "$PGROUP" -l "$EXPERIMENT-$bm-sid$sid" -- "$GEM5 \
        --outdir=$RESDIR \
        ${CONFIG} \
        --workload $bm \
        --sid $sid \
        $FLAGS \
        --kernel $KERNEL --disk $DISK_IMAGE --isa=Arm \
        --checkpoint-dir $CHECKPOINT_BASE \
        --simpoint-dir $SIMPOINT_BASE \
        > $RESDIR/gem5.log 2>&1"

done
