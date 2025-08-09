

set -x

GEM5=./../build/ARM/gem5.opt
CONFIG=./gem5-configs/spec-run.py

SIMPOINT_BASE=/share/david/spec/arm64/simpoints_200M/
CHECKPOINT_BASE=/share/david/spec/arm64/checkpoints_200M/


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


# ------------Benchmarks---------------

BMS=()
BMS+=("500.perlbench_r.checkspam")
BMS+=("500.perlbench_r.diffmail")
# BMS+=("500.perlbench_r.splitmail")
BMS+=("502.gcc_r.gcc-pp.opts-O3_-finline-limit_0")
BMS+=("502.gcc_r.gcc-pp.opts-O3_-finline-limit_36000")
BMS+=("502.gcc_r.gcc-smaller.c-O3_-fipa-pta")
BMS+=("502.gcc_r.ref32.c_-O5")
BMS+=("502.gcc_r.ref32.c_-O3")
BMS+=("505.mcf_r.inp")
# BMS+=("520.omnetpp_r.general")
# BMS+=("523.xalancbmk_r.xalanc")
BMS+=("525.x264_r.x264_pass1")
# BMS+=("525.x264_r.x264_pass2")
BMS+=("525.x264_r.x264")
BMS+=("531.deepsjeng_r.ref")
BMS+=("541.leela_r.ref")
# BMS+=("548.exchange2_r.general")
BMS+=("557.xz_r.cld")
BMS+=("557.xz_r.cpu2006docs")
BMS+=("557.xz_r.input")
BMS+=("999.specrand_ir.rand")

#------------------------


declare -A simpoints

simpoints["500.perlbench_r.checkspam"]=4
simpoints["500.perlbench_r.diffmail"]=4
simpoints["500.perlbench_r.splitmail"]=1
simpoints["502.gcc_r.gcc-pp.opts-O3_-finline-limit_0"]=4
simpoints["502.gcc_r.gcc-pp.opts-O3_-finline-limit_36000"]=4
simpoints["502.gcc_r.gcc-smaller.c-O3_-fipa-pta"]=4
simpoints["502.gcc_r.ref32.c_-O5"]=4
simpoints["502.gcc_r.ref32.c_-O3"]=4
simpoints["505.mcf_r.inp"]=4
simpoints["520.omnetpp_r.general"]=1
simpoints["523.xalancbmk_r.xalanc"]=4
simpoints["525.x264_r.x264_pass1"]=4
simpoints["525.x264_r.x264_pass2"]=1
simpoints["525.x264_r.x264"]=4
simpoints["531.deepsjeng_r.ref"]=4
simpoints["541.leela_r.ref"]=4
simpoints["548.exchange2_r.general"]=1
simpoints["557.xz_r.cld"]=4
simpoints["557.xz_r.cpu2006docs"]=4
simpoints["557.xz_r.input"]=4
simpoints["999.specrand_ir.rand"]=1


# Parsing args
# i set inf_tage, -b set big squash, -g set giant cache -m set inf_phast
while getopts "w:f:p:s:d:ibmg" opt; do
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

for bm in "${BMS[@]}"; do
for sid in $(seq 0 ${simpoints["$bm"]}); do 
   RESDIR=${RESULTS_DIR}/$bm/sid$sid

   mkdir -p $RESDIR

   pueue add -g "$PGROUP" -l "$EXPERIMENT-$bm-sid$sid" -- "$GEM5 \
    --outdir=$RESDIR \
    ${CONFIG} \
    --workload $bm \
    --sid $sid \
    --width $WIDTH \
    --factor $FACTOR \
    --ppc $PREDPERCYCLE \
    --fdp \
    --isa $ISA \
    --cpu-type $CPU_TYPE \
    --checkpoint-dir $CHECKPOINT_BASE \
    --simpoint-dir $SIMPOINT_BASE \
    ${SIM_FLAGS} \
    > $RESDIR/gem5.log 2>&1"

done
done
