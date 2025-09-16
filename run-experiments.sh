#!/bin/bash
# -i set inf_tage, -b set big squash, -g set giant cache -m set inf_phast -q set fbInFTQ
# -w set the width, -f set the factor, -p set predictions per cycle
# -s set the set name, -d set number of data points, -h for help

SET="Experiment_set"
DATA_POINTS=1
FLAGS=""

FRONTEND_BASELINE=""
ENHANCED_FRONTEND="-q"
BACKEND_BASELINE="-q"
ONE_CYCLE_SQUASH="-q -b"
OCS_INF_TAGE="-q -b -i"
OCS_IT_INF_PHAST="-q -b -i -m"
OCS_IT_IP_GIANT_CACHE="-q -b -i -m -g"

# Bigger inst window uses width 64, factor 8 and OCS_IT_IP_GIANT_CACHE


FLAGS="$FRONTEND_BASELINE"



#./scripts/run_all.sh -w 12 -f 1 -p 1 -s "$SET" -d ${DATA_POINTS} $FLAGS
#./scripts/run_all.sh -w 12 -f 1 -p 2 -s "$SET" -d ${DATA_POINTS} $FLAGS
#./scripts/run_all.sh -w 12 -f 1 -p 4 -s "$SET" -d ${DATA_POINTS} $FLAGS
#./scripts/run_all.sh -w 12 -f 1 -p 6 -s "$SET" -d ${DATA_POINTS} $FLAGS

./scripts/run_all.sh -w 36 -f 3 -p 1 -s "$SET" -d ${DATA_POINTS} $FLAGS
./scripts/run_all.sh -w 36 -f 3 -p 2 -s "$SET" -d ${DATA_POINTS} $FLAGS
./scripts/run_all.sh -w 36 -f 3 -p 4 -s "$SET" -d ${DATA_POINTS} $FLAGS
./scripts/run_all.sh -w 36 -f 3 -p 6 -s "$SET" -d ${DATA_POINTS} $FLAGS


#./scripts/spec_run_simpoints.sh -w 12 -f 1 -p 1 -s "$SET" $FLAGS
#./scripts/spec_run_simpoints.sh -w 12 -f 1 -p 2 -s "$SET" $FLAGS
#./scripts/spec_run_simpoints.sh -w 12 -f 1 -p 4 -s "$SET" $FLAGS
#./scripts/spec_run_simpoints.sh -w 12 -f 1 -p 6 -s "$SET" $FLAGS

./scripts/spec_run_simpoints.sh -w 36 -f 3 -p 1 -s "$SET" $FLAGS
./scripts/spec_run_simpoints.sh -w 36 -f 3 -p 2 -s "$SET" $FLAGS
./scripts/spec_run_simpoints.sh -w 36 -f 3 -p 4 -s "$SET" $FLAGS
./scripts/spec_run_simpoints.sh -w 36 -f 3 -p 6 -s "$SET" $FLAGS