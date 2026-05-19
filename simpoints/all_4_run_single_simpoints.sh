set -x

GEM5=/home/yongjie/gem5-fdp/build/ARM/gem5.opt
# GEM5=/home/yongjie/gem5.opt

# Common Parameters (Latencies from SVR script as requested)
FACTOR=1
WIDTH=8
NUMFTQENTRIES=16
L1NUMENTRIES=128
# L2NUMENTRIES=16384
# L2LATENCY=3
L2NUMENTRIES=6144
L2LATENCY=3
L3NUMENTRIES=16384
L3LATENCY=3
L1ASSOC=8
L2ASSOC=6
MAXTAKENPREDPERCYCLE=1
TAGELATENCY=2
PBUFFER_SIZE=32

ARCH="arm64"
CPU_TYPE="o3"

PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --prefetchBothForCall"
# PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --noPrefetchLatency --useCompressedTagFilter --compressedTagBits 3"
# PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --prefetchOnlyCB"
# PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --prefetchOnlyUB"
PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --prefetchBothForCall --limitRet"
PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --prefetchBothForCall --limitRet --pDepth 2"
PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit"
PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --noPrefetchLatency"
PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --noPrefetchLatency --prefetchOnL1Hit"
# PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --prefetchBothForCall --limitRet --noPrefetchLatency"
# PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --prefetchBothForCall --limitRet --pDepth 3"
PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --prefetchBothForCall --limitRet --prefetchOnL1Hit --pDepth 6"
PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --prefetchBothForCall --limitRet --prefetchOnL1Hit --pDepth 7"
# PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --prefetchBothForCall --limitRet --prefetchOnL1Hit"
# PPOLICY="--noPrefetchLatency --finalMarkov --prefetchAllSuccessors"
# PPOLICY="--pPolicy 6 --noPrefetchLatency"
# PPOLICY="--pPolicy 4 --noPrefetchLatency"
# PPOLICY="--noPrefetchLatency --finalMarkov"
# PPOLICY="--noPrefetchLatency --finalMarkov --prefetchAllSuccessors --limitRet --prefetchOnL1Hit"
# PPOLICY="--noPrefetchLatency --finalMarkov --prefetchAllSuccessors --prefetchOnL1Hit"
# PPOLICY="--noPrefetchLatency --finalMarkov --prefetchOnL1Hit"
# PPOLICY="--noPrefetchLatency --finalMarkov --markovUseRecency"
PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --noPrefetchLatency --prefetchBothForCall --limitRet --newPBits"
PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --prefetchBothForCall --limitRet --newPBits --pDepth 4 --noPrefetchLatency"
PPOLICY="--noPrefetchLatency --finalMarkov --prefetchAllSuccessors --limitRet"
PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --prefetchBothForCall --limitRet --newPBits --prefetchOnL1Hit --pDepth 7"
# PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --prefetchBothForCall --limitRet --newPBits --depthOnlyCall --pDepth 7"
# PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --prefetchBothForCall --limitRet --newPBits --onlyCall --pDepth 5"
# PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --prefetchBothForCall --limitRet --newPBits --onlyCallAndBackward --pDepth 2"
PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --limitRet --newPBits --prefetchOnL1Hit --pDepth 5 --maxChainTrackerEntries 16"
PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --limitRet --newPBits --prefetchOnL1Hit --pDepth 5 --maxChainTrackerEntries 1 --killFullChainOnL1Hit"
PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --limitRet --newPBits --pDepth 14 --maxChainTrackerEntries 8"
# PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --limitRet --newPBits --prefetchOnL1Hit --pDepth 5 --useCompressedTagFilter --compressedTagBits 13"
PPOLICY="--pPolicy 0"
# Experiment 

EXPERIMENT="optimal_BTB-single"
EXPERIMENT="optimal_Both-single"
# EXPERIMENT="baseline-single"
# EXPERIMENT="PBits-noLat-single"
# EXPERIMENT="Markov-noLat-single"
# EXPERIMENT="PBits-single"
# EXPERIMENT="PBits-callRet-2dep-single"
# EXPERIMENT="PBits-callRet-l1hit-single"
# EXPERIMENT="PBits-bothCall-limitRet-16FT-3dep-single"
# EXPERIMENT="PBits-callRet-l1hit-2dep-single"
EXPERIMENT="PBits-callRet-l1hit-3dep-single"
EXPERIMENT="PBits-callRet-l1hit-4dep-single"
EXPERIMENT="PBits-noLat-l1hit-single"
EXPERIMENT="PBits-callRet-l1hit-4dep-test"
# EXPERIMENT="PBits-callRet-l1hit-5dep-test"
EXPERIMENT="PBits-callRet-l1hit-6dep-test"
EXPERIMENT="PBits-callRet-l1hit-7dep-test"
EXPERIMENT="PBits-callRet-l1hit-7dep-test2"
# EXPERIMENT="MarkovAll-l1hit-limitRet-noLat"
# EXPERIMENT="PBits-callRet-l1hit-7dep-noLat"

EXPERIMENT="newPBits-4dep-noLat"
EXPERIMENT="MarkovAll_litRet"

# EXPERIMENT="newPBits-7dep-davi

EXPERIMENT="newPBits-l1hit-5dep-test"
# EXPERIMENT="newPBits-l1hit-5dep-test-filter"
# EXPERIMENT="newPBits-l1hit-5dep-test-filter-64bit"
# EXPERIMENT="newPBits-l1hit-5dep-test-32ass"
# EXPERIMENT="newPBits-l1hit-5dep-test-filter-64bit-more"
# EXPERIMENT="newPBits-l1hit-5dep-old"
# EXPERIMENT="newPBits-l1hit-5dep-test-1filter"
# EXPERIMENT="newPBits-l1hit-5dep-test-2filter"
# EXPERIMENT="newPBits-l1hit-5dep-test-2filter-64bit"
EXPERIMENT="newPBits-l1hit-5dep-test-64btbtag"
EXPERIMENT="newPBits-l1hit-5dep-test-filter-64bit-64btbtag"


EXPERIMENT="baseline"
EXPERIMENT="optimal_BTB"

EXPERIMENT="pf-l1hit-8sz-16"
EXPERIMENT="pf-l1hit-8sz-20"
EXPERIMENT="pf-l1hit-8sz-24"
EXPERIMENT="pf-l1hit-8sz-28"
EXPERIMENT="pf-l1hit-8sz-32"
EXPERIMENT="pf-l1hit-8sz-12"
EXPERIMENT="pf-l1hit-8sz-8"
EXPERIMENT="pf-l1hit-8sz-4"



# EXPERIMENT="pf-8sz-16"
EXPERIMENT="pf-1sz-16"
EXPERIMENT="pf-2sz-16"
EXPERIMENT="pf-4sz-16"
EXPERIMENT="pf-16sz-16"

# EXPERIMENT="pf-l1hit-8sz-16"
EXPERIMENT="pf-l1hit-1sz-16"
# EXPERIMENT="pf-l1hit-2sz-16"
# EXPERIMENT="pf-l1hit-4sz-16"
# EXPERIMENT="pf-l1hit-16sz-16"

# 20M
EXPERIMENT="pf-8pb-8sz-4"
EXPERIMENT="pf-8pb-8sz-8"
EXPERIMENT="pf-8pb-8sz-12"
EXPERIMENT="pf-8pb-8sz-16"
EXPERIMENT="pf-8pb-8sz-20"
EXPERIMENT="pf-8pb-8sz-24"

EXPERIMENT="pf-16pb-8sz-4"
# EXPERIMENT="pf-16pb-8sz-8"
# EXPERIMENT="pf-16pb-8sz-12"
# EXPERIMENT="pf-16pb-8sz-16"
# EXPERIMENT="pf-16pb-8sz-20"
# EXPERIMENT="pf-16pb-8sz-24"


EXPERIMENT="pf-16pb-1sz-16"
EXPERIMENT="pf-16pb-2sz-16"
EXPERIMENT="pf-16pb-4sz-16"
EXPERIMENT="pf-16pb-8sz-16"
EXPERIMENT="pf-16pb-16sz-16"
# EXPERIMENT="pf-16pb-24sz-16"

# EXPERIMENT="pf-8pb-1sz-16"
# EXPERIMENT="pf-8pb-2sz-16"
# EXPERIMENT="pf-8pb-4sz-16"
# EXPERIMENT="pf-8pb-8sz-16"
# EXPERIMENT="pf-8pb-16sz-16"
# EXPERIMENT="pf-8pb-24sz-16"

EXPERIMENT="pf-32pb-1sz-16"
EXPERIMENT="pf-32pb-2sz-16"
EXPERIMENT="pf-32pb-4sz-16"
EXPERIMENT="pf-32pb-8sz-16"
EXPERIMENT="pf-32pb-16sz-16"
EXPERIMENT="pf-32pb-24sz-16"

EXPERIMENT="pf-32pb-8sz-4"
EXPERIMENT="pf-32pb-8sz-8"
EXPERIMENT="pf-32pb-8sz-12"
EXPERIMENT="pf-32pb-8sz-16"
EXPERIMENT="pf-32pb-8sz-20"
EXPERIMENT="pf-32pb-8sz-24"
#20M ^
EXPERIMENT="pf-16pb-8sz-20-200M"
EXPERIMENT="pf-8pb-8sz-20-200M"
EXPERIMENT="pf-8pb-8sz-16-200M"
EXPERIMENT="pf-8pb-8sz-8-200M"
EXPERIMENT="pf-8pb-8sz-4-200M"
EXPERIMENT="pf-8pb-8sz-2-200M"
EXPERIMENT="pf-8pb-8sz-1-200M"

EXPERIMENT="pf-16pb-8sz-20-200M"
EXPERIMENT="pf-16pb-8sz-16-200M"
EXPERIMENT="pf-16pb-8sz-8-200M"
EXPERIMENT="pf-16pb-8sz-4-200M"
EXPERIMENT="pf-16pb-8sz-2-200M"
EXPERIMENT="pf-16pb-8sz-1-200M"

# EXPERIMENT="pf-16pb-8sz-20-200M"
# EXPERIMENT="pf-16pb-24sz-20-200M"
# EXPERIMENT="pf-16pb-16sz-20-200M"
# EXPERIMENT="pf-16pb-4sz-20-200M"
# EXPERIMENT="pf-16pb-2sz-20-200M"
# EXPERIMENT="pf-16pb-1sz-20-200M"


# EXPERIMENT="pf-8pb-8sz-20-200M"
EXPERIMENT="pf-8pb-24sz-20-200M"
# EXPERIMENT="pf-8pb-16sz-20-200M"
# EXPERIMENT="pf-8pb-4sz-20-200M"
# EXPERIMENT="pf-8pb-2sz-20-200M"
# EXPERIMENT="pf-8pb-1sz-20-200M"
EXPERIMENT="pf-8sz-1"
# EXPERIMENT="pf-8sz-2"
# EXPERIMENT="pf-8sz-4"
# EXPERIMENT="pf-8sz-8"
# EXPERIMENT="pf-8sz-12"
# EXPERIMENT="pf-8sz-16"
# EXPERIMENT="pf-8sz-20"

EXPERIMENT="64-8sz-1"
EXPERIMENT="64-8sz-2"
EXPERIMENT="64-8sz-4"
EXPERIMENT="64-8sz-6"
EXPERIMENT="64-8sz-8"
EXPERIMENT="64-8sz-10"
EXPERIMENT="64-8sz-12"
EXPERIMENT="64-8sz-14"
EXPERIMENT="64-8sz-16"
EXPERIMENT="64-8sz-18"
EXPERIMENT="64-8sz-20"
EXPERIMENT="64-8sz-22"

EXPERIMENT="64-10sz-14"
EXPERIMENT="64-5sz-14"
EXPERIMENT="64-4sz-14"
EXPERIMENT="64-3sz-14"
EXPERIMENT="64-2sz-14"
EXPERIMENT="64-1sz-14"

# EXPERIMENT="8sz-1"
# EXPERIMENT="8sz-2"
# EXPERIMENT="8sz-4"
# EXPERIMENT="8sz-6"
# EXPERIMENT="8sz-8"
# EXPERIMENT="8sz-10"
# EXPERIMENT="8sz-12"
# EXPERIMENT="8sz-14"
# EXPERIMENT="8sz-16"
# EXPERIMENT="8sz-18"
# EXPERIMENT="8sz-20"
# EXPERIMENT="8sz-22"
# EXPERIMENT="8sz-18"
# EXPERIMENT="32-10sz-14"
# EXPERIMENT="32-5sz-14"
# EXPERIMENT="32-4sz-14"
# EXPERIMENT="32-3sz-14"
# EXPERIMENT="32-2sz-14"
# EXPERIMENT="32-1sz-14"
EXPERIMENT="Ferret-fix"
EXPERIMENT="baseline-3level"
# EXPERIMENT="baseline-3level-3cL2"
EXPERIMENT="baseline-2level-6kL2"


# EXPERIMENT="16-8sz-1"
# EXPERIMENT="16-8sz-2"
# EXPERIMENT="16-8sz-4"
# EXPERIMENT="16-8sz-6"
# EXPERIMENT="16-8sz-8"
# EXPERIMENT="16-8sz-10"
# EXPERIMENT="16-8sz-12"
# EXPERIMENT="16-8sz-14"
# EXPERIMENT="16-8sz-16"
# EXPERIMENT="16-8sz-18"
# EXPERIMENT="16-8sz-20"
# EXPERIMENT="16-8sz-22"

# EXPERIMENT="16-10sz-8"
# EXPERIMENT="16-5sz-8"
# EXPERIMENT="16-4sz-8"
# EXPERIMENT="16-3sz-8"
# EXPERIMENT="16-2sz-8"
# EXPERIMENT="16-1sz-8"

# EXPERIMENT="8-8sz-1"
# EXPERIMENT="8-8sz-2"
# EXPERIMENT="8-8sz-4"
# EXPERIMENT="8-8sz-6"
# EXPERIMENT="8-8sz-8"
# EXPERIMENT="8-8sz-10"
# EXPERIMENT="8-8sz-12"
# EXPERIMENT="8-8sz-14"
# EXPERIMENT="8-8sz-16"
# EXPERIMENT="8-8sz-18"
# EXPERIMENT="8-8sz-20"
# EXPERIMENT="8-8sz-22"

# EXPERIMENT="8-10sz-8"
# EXPERIMENT="8-5sz-8"
# EXPERIMENT="8-4sz-8"
# EXPERIMENT="8-3sz-8"
# EXPERIMENT="8-2sz-8"
# EXPERIMENT="8-1sz-8"


# EXPERIMENT="pf-8sz-24"
# EXPERIMENT="pf-8sz-28"
# EXPERIMENT="pf-8sz-32"

# EXPERIMENT="pf-1sz-20"
# EXPERIMENT="pf-2sz-20"
# EXPERIMENT="pf-4sz-20"
# EXPERIMENT="pf-8sz-20"
# EXPERIMENT="pf-16sz-20"
# EXPERIMENT="pf-24sz-20"

# EXPERIMENT="baseline-144L1"
# EXPERIMENT="baseline-160L1"
# EXPERIMENT="baseline-192L1"
# EXPERIMENT="baseline-256L1"

# --- Suite Configurations ---

# SPEC 2017
SPEC_BMS=()
SPEC_BMS+=("500.perlbench_r.checkspam")
SPEC_BMS+=("502.gcc_r.gcc-pp.opts-O3_-finline-limit_36000")
SPEC_BMS+=("505.mcf_r.inp")
SPEC_BMS+=("523.xalancbmk_r.xalanc")
SPEC_BMS+=("525.x264_r.x264")
SPEC_BMS+=("531.deepsjeng_r.ref")
SPEC_BMS+=("541.leela_r.ref")
SPEC_BMS+=("557.xz_r.input")

SPEC_CONFIG="./gem5-configs/spec-simpoint-run.py"
SPEC_SIMPOINT_BASE="/share/david/spec/arm64/simpoints_200M_v2/"
SPEC_CHECKPOINT_BASE="/share/david/spec/arm64/checkpoints_200M_v2/"

# SVR
SVR_BMS=()
SVR_BMS+=("nodeapp")
SVR_BMS+=("mediawiki")
SVR_BMS+=("proto")
SVR_BMS+=("dacapo-lusearch")
# SVR_BMS+=("swissmap")
SVR_BMS+=("tcmalloc")
SVR_BMS+=("benchbase-voter")
SVR_BMS+=("stl")
SVR_BMS+=("dacapo-h2")
SVR_BMS+=("dacapo-h2o")
# SVR_BMS+=("dacapo-kafka")
SVR_BMS+=("dacapo-luindex")
SVR_BMS+=("dacapo-spring")
SVR_BMS+=("dacapo-tomcat")
SVR_BMS+=("renaissance-http")
SVR_BMS+=("benchbase-twitter")
SVR_BMS+=("benchbase-tatp")
# SVR_BMS+=("benchbase-resourcestresser")
SVR_BMS+=("benchbase-epinions")
SVR_BMS+=("benchbase-ycsb")
SVR_BMS+=("benchbase-seats")
SVR_BMS+=("benchbase-sibench")
SVR_BMS+=("benchbase-noop")
SVR_BMS+=("benchbase-smallbank")

# SVR_BMS+=("benchbase-epinions")

SVR_CONFIG="./gem5-configs/svr-simpoint-run.py"
SVR_SIMPOINT_BASE="/share/david/svr/arm64/v2/simpoints_200M/"
SVR_CHECKPOINT_BASE="/share/david/svr/arm64/v2/checkpoints_200M/"
SVR_KERNEL="/share/david/svr/arm64/v2/kernel"
SVR_DISK_IMAGE="/share/david/svr/arm64/v2/disk.img"

# --- Selection ---

# Set to 1 to enable, 0 to disable
RUN_SPEC=1
RUN_SVR=1

# -----------------

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

RESULTS_DIR="./results/$EXPERIMENT"

if ! pgrep -x "pueued" > /dev/null; then
    pueued -d
fi

PGROUP="$ARCH-$EXPERIMENT"
pueue group add -p 100 "$PGROUP" || true
sudo chown $(id -u) /dev/kvm

# Execution Loop
for suite in "spec" "svr"; do
    if [ "$suite" == "spec" ] && [ $RUN_SPEC -eq 0 ]; then continue; fi
    if [ "$suite" == "svr" ] && [ $RUN_SVR -eq 0 ]; then continue; fi

    if [ "$suite" == "spec" ]; then
        BMS=("${SPEC_BMS[@]}")
        CONFIG=$SPEC_CONFIG
        SIMPOINT_BASE=$SPEC_SIMPOINT_BASE
        CHECKPOINT_BASE=$SPEC_CHECKPOINT_BASE
        EXTRA_FLAGS=""
    else
        BMS=("${SVR_BMS[@]}")
        CONFIG=$SVR_CONFIG
        SIMPOINT_BASE=$SVR_SIMPOINT_BASE
        CHECKPOINT_BASE=$SVR_CHECKPOINT_BASE
        EXTRA_FLAGS="--kernel $SVR_KERNEL --disk $SVR_DISK_IMAGE --isa=Arm"
    fi

    echo "Starting suite: $suite"

    for bm in "${BMS[@]}"; do
        WEIGHT_FILE="${SIMPOINT_BASE}${bm}/results.weights"
        SIMPTS_FILE="${SIMPOINT_BASE}${bm}/results.simpts"

        if [ -f "$WEIGHT_FILE" ] && [ -f "$SIMPTS_FILE" ]; then
            max_phase=$(join -1 2 -2 2 <(sort -k2,2 "$SIMPTS_FILE") <(sort -k2,2 "$WEIGHT_FILE") | sort -k3,3nr | head -n 1 | awk '{print $2}')
            sid=$(awk '{print $1}' "$SIMPTS_FILE" | sort -n | grep -nx "$max_phase" | cut -d: -f1)
            sid=$((sid - 1))
        else
            echo "Warning: Weight file $WEIGHT_FILE or $SIMPTS_FILE not found for $bm. Skipping."
            continue
        fi

        RESDIR=${RESULTS_DIR}/$bm/sid$sid
        if [ -d "$RESDIR" ]; then
            echo "Skipping $bm (SID: $sid) - Result directory already exists."
            continue
        fi
        mkdir -p $RESDIR

        echo "Enqueuing $suite:$bm (SID: $sid)"

        if [ "$bm" == "502.gcc_r.gcc-pp.opts-O3_-finline-limit_36000" ]; then
            SUDO="sudo"
        else
            SUDO=""
        fi

        $SUDO nohup $GEM5 --outdir=$RESDIR \
            ${CONFIG} \
            --workload $bm \
            --sid $sid \
            --fdp --l1NumEntries $L1NUMENTRIES --l2NumEntries $L2NUMENTRIES --l3NumEntries $L3NUMENTRIES --l1Associativity $L1ASSOC --l2Associativity $L2ASSOC --numFTQEntries $NUMFTQENTRIES \
            --l2Latency $L2LATENCY --l3Latency $L3LATENCY --TAGELatency $TAGELATENCY --factor $FACTOR --width $WIDTH --maxTakenPredPerCycle $MAXTAKENPREDPERCYCLE \
            --pBufferSize $PBUFFER_SIZE $PPOLICY \
            --checkpoint-dir $CHECKPOINT_BASE \
            --simpoint-dir $SIMPOINT_BASE \
            $EXTRA_FLAGS \
            > $RESDIR/gem5.log 2>&1 &
    done
done

echo "All jobs submitted."
