#!/bin/bash

SET="IT_PHAST_TRACE"
DATA_POINTS=2

./scripts/run_all.sh -w 36 -f 3 -p 1 -s "$SET" -d ${DATA_POINTS}
./scripts/run_all.sh -w 36 -f 3 -p 2 -s "$SET" -d ${DATA_POINTS}
./scripts/run_all.sh -w 36 -f 3 -p 4 -s "$SET" -d ${DATA_POINTS}

