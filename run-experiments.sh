#!/bin/bash

SET=""

./scripts/run_all.sh -w 12 -f 1 -p 1 -s "$SET"
./scripts/run_all.sh -w 12 -f 1 -p 2 -s "$SET"
./scripts/run_all.sh -w 12 -f 1 -p 4 -s "$SET"
./scripts/run_all.sh -w 24 -f 2 -p 1 -s "$SET"
./scripts/run_all.sh -w 24 -f 2 -p 2 -s "$SET"
./scripts/run_all.sh -w 24 -f 2 -p 4 -s "$SET"
./scripts/run_all.sh -w 36 -f 3 -p 1 -s "$SET"
./scripts/run_all.sh -w 36 -f 3 -p 2 -s "$SET"
./scripts/run_all.sh -w 36 -f 3 -p 4 -s "$SET"
./scripts/run_all.sh -w 48 -f 3 -p 1 -s "$SET"
./scripts/run_all.sh -w 48 -f 3 -p 2 -s "$SET"
./scripts/run_all.sh -w 48 -f 3 -p 4 -s "$SET"
