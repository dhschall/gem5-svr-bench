# Copyright (c) 2024 Technical University of Munich
# All rights reserved.
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


wlcfg = {}

from .arguments import *

### Own Benchmarks ###################################################################


def writeRunScript(cfg, cpu=1):
    urlfile = cfg["urlfile"]
    dcfile = cfg["dcfile"]
    container = cfg["container"]
    test_ip = "0.0.0.0"
    conc = 2
    # home = "root"
    home = "home/gem5"
    n_invocations=args.num_invocations
    n_warming=args.atomic_warming
    return f"""
#!/bin/bash

## Define the image name of your function.

# We use the 'm5 exit' magic instruction to indicate the
# python script where in workflow the system currently is.

m5 --addr=0x10010000 exit ## 1: BOOTING complete

## Spin up Container
echo "Start the container..."
sudo docker compose -f /{home}/{dcfile} up -d
sudo docker compose -f /{home}/{dcfile} up -d
m5 --addr=0x10010000 exit ## 2: Started container

echo "Pin {container} container to core {cpu}"
sudo docker update {container} --cpuset-cpus {cpu}
sleep 30

sleep 5
m5 --addr=0x10010000 exit ## 3: Pinned container


# # The client will perform some functional warming
# and then send a fail code before invoking the
# function again for the actual measurement.
sudo GOGC=1000 /{home}/http-client -f /{home}/{urlfile} -url {test_ip} -c {conc} -n {n_invocations} -w {n_warming} -m5ops -v



m5 --addr=0x10010000 exit ## 4: Stop client
# -------------------------------------------


## Stop container
sudo docker compose -f /{home}/{dcfile} down
m5 --addr=0x10010000 exit ## 5: Container stop


## exit the simulations
m5 --addr=0x10010000 exit ## 6: Test done

"""



wlcfg |= {
    "nodeapp": {
        "runscript": writeRunScript,
        "urlfile": "nodeapp.urls.tmpl",
        "dcfile": "dc-nodeapp.yaml",
        "container": "nodeapp",
    },
    "nodeapp-nginx": {
        "runscript": writeRunScript,
        "urlfile": "nodeapp.urls.tmpl",
        "dcfile": "dc-nodeapp.yaml",
        "container": "nginx",
    },
    "mediawiki": {
        "runscript": writeRunScript,
        "urlfile": "mediawiki.urls.tmpl",
        "dcfile": "dc-mediawiki.yaml",
        "container": "wiki",
    },
    "mediawiki-nginx": {
        "runscript": writeRunScript,
        "urlfile": "mediawiki.urls.tmpl",
        "dcfile": "dc-mediawiki.yaml",
        "container": "nginx",
    },
}







### Fleetbench ###################################################################


def writeFleetbenchRunScript(cfg, cpu=1):
    workload = cfg["cmd"]
    options = cfg["options"]
    conc = 2
    # home = "root"
    home = "home/gem5"
    return f"""
#!/bin/bash

## Define the image name of your function.

# We use the 'm5 exit' magic instruction to indicate the
# python script where in workflow the system currently is.

m5 exit ## 1: BOOTING complete

sleep 3

taskset -c {cpu} {workload} {options} &
PID=$!

sleep 1
m5 fail 4 ## take checkpoint


wait $PID


sleep 5

## exit the simulations
m5 exit ## 6: Test done

"""

FLEETBENCH_BUILD_BASE="/home/gem5/fleetbench/build/execroot/com_google_fleetbench/bazel-out/k8-opt/bin/fleetbench"

wlcfg |= {

    "proto": {
        "runscript": writeFleetbenchRunScript,
        "cmd" : f"{FLEETBENCH_BUILD_BASE}/proto/proto_benchmark.runfiles/com_google_fleetbench/fleetbench/proto/proto_benchmark",
        "options" : "--benchmark_min_time=30s",
    },
    "swissmap": {
        "runscript": writeFleetbenchRunScript,
        "cmd" : f"{FLEETBENCH_BUILD_BASE}/swissmap/swissmap_benchmark.runfiles/com_google_fleetbench/fleetbench/swissmap/swissmap_benchmark",
        "options" : "--benchmark_min_time=30s",
    },
    "libc": {
        "runscript": writeFleetbenchRunScript,
        "cmd" : f"{FLEETBENCH_BUILD_BASE}/libc/mem_benchmark.runfiles/com_google_fleetbench/fleetbench/libc/mem_benchmark",
        "options" : f"--benchmark_min_time=1s --L1_data_size={32*1024} --L2_size={512*1024} --L3_size {512*1024}",
    },
    "tcmalloc": {
        "runscript": writeFleetbenchRunScript,
        "cmd" : f"{FLEETBENCH_BUILD_BASE}/tcmalloc/empirical_driver.runfiles/com_google_fleetbench/fleetbench/tcmalloc/empirical_driver",
        "options" : "--benchmark_min_time=1s",
    },
    "compression": {
        "runscript": writeFleetbenchRunScript,
        "cmd" : f"{FLEETBENCH_BUILD_BASE}/compression/compression_benchmark.runfiles/com_google_fleetbench/fleetbench/compression/compression_benchmark",
        "options" : "--benchmark_min_time=1s",
    },
    "hashing": {
        "runscript": writeFleetbenchRunScript,
        "cmd" : f"{FLEETBENCH_BUILD_BASE}/hashing/hashing_benchmark.runfiles/com_google_fleetbench/fleetbench/hashing/hashing_benchmark",
        "options" : f"--benchmark_min_time=1s --L1_data_size {32*1024} --L2_size {512*1024} --L3_size {512*1024}",
    },
    "stl": {
        "runscript": writeFleetbenchRunScript,
        "cmd" : f"{FLEETBENCH_BUILD_BASE}/stl/cord_benchmark.runfiles/com_google_fleetbench/fleetbench/stl/cord_benchmark",
        "options" : "--benchmark_min_time=30s",
    },

}




### Fleetbench ###################################################################


def writeVerilatorRunScript(cfg, cpu=1):
    # home = "root"
    home = "home/gem5"
    return f"""
#!/bin/bash

## Define the image name of your function.

# We use the 'm5 exit' magic instruction to indicate the
# python script where in workflow the system currently is.

m5 exit ## 1: BOOTING complete

sleep 3

taskset -c {cpu} /{home}/Variane_testharness /{home}/dhrystone.riscv &
PID=$!

sleep 25 ## Sleep for at least 20 seconds in which the model loads the
         ## binary before starting the actual simulation
m5 fail 4 ## take checkpoint


wait $PID

## exit the simulations
m5 exit ## 6: Test done

"""


wlcfg |= {

    "verilator": {
        "runscript": writeVerilatorRunScript,
    },
}
