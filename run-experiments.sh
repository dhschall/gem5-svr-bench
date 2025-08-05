#!/bin/bash

SET="BASELINE"
DATA_POINTS=1

./scripts/run_all.sh -w 12 -f 1 -p 1 -s "$SET" -d ${DATA_POINTS}
./scripts/run_all.sh -w 12 -f 1 -p 2 -s "$SET" -d ${DATA_POINTS}
./scripts/run_all.sh -w 12 -f 1 -p 4 -s "$SET" -d ${DATA_POINTS}
./scripts/run_all.sh -w 12 -f 1 -p 6 -s "$SET" -d ${DATA_POINTS}

./scripts/run_all.sh -w 36 -f 3 -p 1 -s "$SET" -d ${DATA_POINTS}
./scripts/run_all.sh -w 36 -f 3 -p 2 -s "$SET" -d ${DATA_POINTS}
./scripts/run_all.sh -w 36 -f 3 -p 4 -s "$SET" -d ${DATA_POINTS}
./scripts/run_all.sh -w 36 -f 3 -p 6 -s "$SET" -d ${DATA_POINTS}

