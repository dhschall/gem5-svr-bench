

set -x


GEM5=/home/david/g5/tmp/gem5-phx/build/ALL/gem5.opt
# GEM5=/home/david/g5/tmp/gem5-decoupled-fe/build/ARM/gem5.opt
# GEM5=/home/david/g5/tmp/gem5-llbp-x/build/ARM/gem5.opt
# GEM5=/home/david/g5/tmp/gem5-yongji/build/ARM/gem5.opt
CONFIG=./gem5-configs/simpoint-run-phx.py

SIMPOINT_SPEC=/share/david/spec/arm64/simpoints_200M_v2/
CHECKPOINT_SPEC=/share/david/spec/arm64/checkpoints_200M_v2/
SIMPOINT_SVR=/share/david/svr/arm64/v2/simpoints_200M/
CHECKPOINT_SVR=/share/david/svr/arm64/v2/checkpoints_200M/
KERNEL=/share/david/svr/arm64/v2/kernel
DISK_IMAGE=/share/david/svr/arm64/v2/disk.img

ARCH="arm64"
CPU_TYPE="o3"



LFACTOR=1
# LFACTOR=full

FACTOR=8
WIDTH=$(($FACTOR * 8))
PPC=$FACTOR
INF_PRED=0
# INF_PRED=1



BMS=()
BMS+=("nodeapp")
BMS+=("mediawiki")
BMS+=("compression")
BMS+=("dacapo-spring")
BMS+=("dacapo-luindex")
BMS+=("dacapo-lusearch")
BMS+=("renaissance-http")
BMS+=("renaissance-chirper")

BMS+=("502.gcc_r.gcc-pp.opts-O3_-finline-limit_36000")
BMS+=("505.mcf_r.inp")
BMS+=("523.xalancbmk_r.xalanc")
BMS+=("531.deepsjeng_r.ref")
BMS+=("541.leela_r.ref")



#------------------------


declare -A simpoints

simpoints["502.gcc_r.gcc-pp.opts-O3_-finline-limit_36000"]=3
simpoints["505.mcf_r.inp"]=2
simpoints["523.xalancbmk_r.xalanc"]=3
simpoints["531.deepsjeng_r.ref"]=2
simpoints["541.leela_r.ref"]=2


simpoints["nodeapp"]=1
simpoints["mediawiki"]=3
simpoints["compression"]=4
simpoints["dacapo-luindex"]=3
simpoints["dacapo-lusearch"]=1
simpoints["dacapo-spring"]=3
simpoints["renaissance-http"]=1
simpoints["renaissance-chirper"]=3



EXPERIMENT="LF${LFACTOR}_f${FACTOR}_w${WIDTH}_ppc${PPC}_infp${INF_PRED}_RD_X3"

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


# Define the output file of your run
RESULTS_DIR="./results_phx/$ARCH/$EXPERIMENT"


if ! pgrep -x "pueued" > /dev/null
then
    pueued -d
fi

PGROUP="$ARCH-$EXPERIMENT"


pueue group add -p 100 "$PGROUP" || true
sudo chown $(id -u) /dev/kvm


for bm in "${BMS[@]}"; do
    sid=${simpoints["$bm"]}

    if [[ $bm == 5* ]]; then
        CHECKPOINT_BASE=$CHECKPOINT_SPEC
        SIMPOINT_BASE=$SIMPOINT_SPEC
    else
        CHECKPOINT_BASE=$CHECKPOINT_SVR
        SIMPOINT_BASE=$SIMPOINT_SVR
    fi


    RESDIR=${RESULTS_DIR}/$bm/

    mkdir -p $RESDIR

    pueue add -g "$PGROUP" -l "$EXPERIMENT-$bm-sid$sid" -- "$GEM5 \
        --outdir=$RESDIR \
        ${CONFIG} \
        --workload $bm \
        --sid $sid \
        --fdp \
        --factor=$FACTOR --width=$WIDTH --ppc=$PPC --lfactor=$LFACTOR --inf-pred=$INF_PRED \
        --kernel $KERNEL --disk $DISK_IMAGE --isa=Arm \
        --checkpoint-dir $CHECKPOINT_BASE \
        --simpoint-dir $SIMPOINT_BASE \
        > $RESDIR/gem5.log 2>&1"

done
