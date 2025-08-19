

set -x


GEM5=/scratch/david/g5/tmp/gem5-decoupled-fe/build/ALL/gem5.opt
CONFIG=./gem5-configs/svr-simpoint-run.py

SIMPOINT_BASE=/share/david/svr/arm64/v2/simpoints_200M/
CHECKPOINT_BASE=/share/david/svr/arm64/v2/checkpoints_200M/
KERNEL=/share/david/svr/arm64/v2/kernel
DISK_IMAGE=/share/david/svr/arm64/v2/disk.img

ARCH="arm64"
CPU_TYPE="o3"


BMS=()



BMS+=("nodeapp")

BMS+=("mediawiki")
BMS+=("proto")
BMS+=("swissmap")
BMS+=("libc")
BMS+=("tcmalloc")
BMS+=("compression")
BMS+=("hashing")
BMS+=("stl")

## Java BMS
# WORKLOADS="cassandra h2 h2o kafka luindex lusearch spring tomcat"
BMS+=("dacapo-cassandra")
BMS+=("dacapo-h2")
BMS+=("dacapo-h2o")
BMS+=("dacapo-kafka")
BMS+=("dacapo-luindex")
BMS+=("dacapo-lusearch")
BMS+=("dacapo-spring")
BMS+=("dacapo-tomcat")
BMS+=("renaissance-http")
BMS+=("renaissance-chirper")


BMS+=("benchbase-tpcc")
BMS+=("benchbase-twitter")
BMS+=("benchbase-wikipedia")

BMS+=("benchbase-tatp")
BMS+=("benchbase-resourcestresser")
BMS+=("benchbase-epinions")
BMS+=("benchbase-ycsb")
BMS+=("benchbase-seats")
BMS+=("benchbase-auctionmark")
BMS+=("benchbase-chbenchmark")
BMS+=("benchbase-voter")
BMS+=("benchbase-sibench")
BMS+=("benchbase-noop")
BMS+=("benchbase-smallbank")
BMS+=("benchbase-hyadapt")
BMS+=("benchbase-otmetrics")



#------------------------


declare -A simpoints

simpoints["nodeapp"]=2
simpoints["hashing"]=3
simpoints["benchbase-tpcc"]=2
simpoints["benchbase-wikipedia"]=2
simpoints["benchbase-auctionmark"]=2



EXPERIMENT="expv2"

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


if ! pgrep -x "pueued" > /dev/null
then
    pueued -d
fi

PGROUP="$ARCH-$EXPERIMENT"


pueue group add -p 100 "$PGROUP" || true
sudo chown $(id -u) /dev/kvm


for bm in "${BMS[@]}"; do

   # Check if the key exists
   max_sid=4
   if [[ -v simpoints["$bm"] ]]; then
      max_sid=${simpoints["$bm"]}
   fi

   for sid in $(seq 0 $max_sid); do
      RESDIR=${RESULTS_DIR}/$bm/sid$sid

      mkdir -p $RESDIR

      pueue add -g "$PGROUP" -l "$EXPERIMENT-$bm-sid$sid" -- "$GEM5 \
            --outdir=$RESDIR \
            ${CONFIG} \
            --workload $bm \
            --sid $sid \
            --fdp \
            --kernel $KERNEL --disk $DISK_IMAGE --isa=Arm \
            --checkpoint-dir $CHECKPOINT_BASE \
            --simpoint-dir $SIMPOINT_BASE \
            > $RESDIR/gem5.log 2>&1"

   done
done
