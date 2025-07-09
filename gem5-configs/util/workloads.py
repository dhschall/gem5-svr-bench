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

### Own Benchmarks ###################################################################


def writeDockerRunScript(cfg, cpu=1):
    urlfile = cfg["urlfile"]
    dcfile = cfg["dcfile"]
    container = cfg["container"]
    test_ip = "0.0.0.0"
    conc = 2
    # home = "root"
    home = "home/gem5"
    n_invocations=cfg["invocations"]
    n_warming=cfg["warming"]
    return f"""
#!/bin/bash

## Define the image name of your function.

# We use the 'm5 exit' magic instruction to indicate the
# python script where in workflow the system currently is.

## Spin up Container
echo "Start the container..."
sudo docker compose -f /{home}/{dcfile} up -d

echo "Pin {container} container to core {cpu}"
sudo docker update {container} --cpuset-cpus {cpu}
sleep 30


# # The client will perform some functional warming
# and then send a fail code before invoking the
# function again for the actual measurement.
sudo GOGC=1000 /{home}/http-client -f /{home}/{urlfile} -url {test_ip} -c {conc} -n {n_invocations} -w {n_warming} -m5ops -v

## Stop container
# sudo docker compose -f /{home}/{dcfile} down


## exit the simulations
m5 exit ## Test done

"""


wlcfg |= {
    "nodeapp": {
        "runscript": writeDockerRunScript,
        "urlfile": "nodeapp.urls.tmpl",
        "dcfile": "dc-nodeapp.yaml",
        "container": "nodeapp",
        "invocations": 200,
        "warming": 5000,
    },
    "nodeapp-nginx": {
        "runscript": writeDockerRunScript,
        "urlfile": "nodeapp.urls.tmpl",
        "dcfile": "dc-nodeapp.yaml",
        "container": "nginx",
        "invocations": 200,
        "warming": 5000,
    },
    "mediawiki": {
        "runscript": writeDockerRunScript,
        "urlfile": "mediawiki.urls.tmpl",
        "dcfile": "dc-mediawiki.yaml",
        "container": "wiki",
        "invocations": 200,
        "warming": 5000,
    },
    "mediawiki-nginx": {
        "runscript": writeDockerRunScript,
        "urlfile": "mediawiki.urls.tmpl",
        "dcfile": "dc-mediawiki.yaml",
        "container": "nginx",
        "invocations": 200,
        "warming": 5000,
    },
}




### LLBP_Bench ###################################################################


def writeLLBPRunScript(cfg, cpu=1):
    workload = cfg["cmd"]
    options = cfg["options"]
    return f"""
#!/bin/bash

## Define the image name of your function.

sleep 3

taskset -c {cpu} {workload} {options}

sleep 1

## exit the simulations
m5 exit ## Test done
"""


LLBP_BENCH_BUILD_BASE="/home/gem5/llbp_benchmark"

wlcfg |= {
    "llbp": {
        "runscript": writeLLBPRunScript,
        "cmd": f"{LLBP_BENCH_BUILD_BASE}/output/binary_search",
        "options": "--bench",
    },
}



### Fleetbench ###################################################################

def writeFleetbenchRunScript(cfg, cpu=1):
    workload = cfg["cmd"]
    options = cfg["options"]
    return f"""
#!/bin/bash

## Define the image name of your function.

sleep 3

taskset -c {cpu} {workload} {options} &
PID=$!

sleep 1
m5 fail 4 ## take checkpoint

wait $PID

sleep 5

## exit the simulations
m5 exit ## Test done

"""



FLEETBENCH_BUILD_BASE="/home/gem5/fleetbench/bazel-bin/fleetbench"

wlcfg |= {

    "proto": {
        "runscript": writeFleetbenchRunScript,
        "cmd" : f"{FLEETBENCH_BUILD_BASE}/proto/proto_benchmark",
        "options" : "--benchmark_min_time=30s",
    },
    "swissmap": {
        "runscript": writeFleetbenchRunScript,
        "cmd" : f"{FLEETBENCH_BUILD_BASE}/swissmap/swissmap_benchmark",
        "options" : "--benchmark_min_time=30s",
    },
    "libc": {
        "runscript": writeFleetbenchRunScript,
        "cmd" : f"{FLEETBENCH_BUILD_BASE}/libc/mem_benchmark",
        "options" : f"--benchmark_min_time=1s --L1_data_size={32*1024} --L2_size={512*1024} --L3_size {512*1024}",
    },
    "tcmalloc": {
        "runscript": writeFleetbenchRunScript,
        "cmd" : f"{FLEETBENCH_BUILD_BASE}/tcmalloc/empirical_driver",
        "options" : "--benchmark_min_time=1s",
    },
    "compression": {
        "runscript": writeFleetbenchRunScript,
        "cmd" : f"{FLEETBENCH_BUILD_BASE}/compression/compression_benchmark",
        "options" : "--benchmark_min_time=1s",
    },
    "hashing": {
        "runscript": writeFleetbenchRunScript,
        "cmd" : f"{FLEETBENCH_BUILD_BASE}/hashing/hashing_benchmark",
        "options" : f"--benchmark_min_time=1s --L1_data_size {32*1024} --L2_size {512*1024} --L3_size {512*1024}",
    },
    "stl": {
        "runscript": writeFleetbenchRunScript,
        "cmd" : f"{FLEETBENCH_BUILD_BASE}/stl/cord_benchmark",
        "options" : "--benchmark_min_time=30s",
    },

}




### Verilator ###################################################################


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



### Java Apps ###################################################################


def writeJavaAppRunScript(cfg, cpu=1):
    # home = "root"
    home = "home/gem5"
    wl = cfg["workload"]
    return f"""
#!/bin/bash

## Define the image name of your function.

# We use the 'm5 exit' magic instruction to indicate the
# python script where in workflow the system currently is.

## 1: BOOTING complete
set -x

sleep 3

CMD="java -jar {cfg["jarfile"]} {wl} {cfg["args"]}" 

taskset --cpu-list {cpu} $CMD > /tmp/{wl}.log 2>&1 &
BMPID=$!


i=0
while true; do
    if grep -q '{cfg["match_string"]}' /tmp/{wl}.log; then
        echo "Found the match string in the log file."
        break
    fi
    sleep 1
    i=$((i+1))
    if [ $i -gt 10 ]; then
        cat /tmp/{wl}.log
        i=0
    fi
done

sleep 1
m5 fail 4 ## take checkpoint

wait $BMPID

m5 writefile /tmp/{wl}.log workload.log

## exit the simulations
m5 exit ## 6: Test done

"""


wlcfg |= {

    "dacapo-cassandra": {
        "runscript": writeJavaAppRunScript,
        "workload": "cassandra",
        "jarfile": "dacapo.jar",
        "args": "-n 5",
        "match_string": "cassandra starting =====",
    },
    "dacapo-h2": {
        "runscript": writeJavaAppRunScript,
        "workload": "h2",
        "jarfile": "dacapo.jar",
        "args": "-n 5",
        "match_string": "h2 starting =====",
    },
    "dacapo-h2o": {
        "runscript": writeJavaAppRunScript,
        "workload": "h2o",
        "jarfile": "dacapo.jar",
        "args": "-n 5",
        "match_string": "h2o starting =====",
    },
    "dacapo-kafka": {
        "runscript": writeJavaAppRunScript,
        "workload": "kafka",
        "jarfile": "dacapo.jar",
        "args": "-n 5",
        "match_string": "kafka starting =====",
    },
    "dacapo-luindex": {
        "runscript": writeJavaAppRunScript,
        "workload": "luindex",
        "jarfile": "dacapo.jar",
        "args": "-n 5",
        "match_string": "luindex starting =====",
    },
    "dacapo-lusearch": {
        "runscript": writeJavaAppRunScript,
        "workload": "lusearch",
        "jarfile": "dacapo.jar",
        "args": "-n 5",
        "match_string": "lusearch starting =====",
    },
    "dacapo-spring": {
        "runscript": writeJavaAppRunScript,
        "workload": "spring",
        "jarfile": "dacapo.jar",
        "args": "-n 5",
        "match_string": "spring starting =====",
    },
    "dacapo-tomcat": {
        "runscript": writeJavaAppRunScript,
        "workload": "tomcat",
        "jarfile": "dacapo.jar",
        "args": "-n 5",
        "match_string": "tomcat starting =====",
    },


    "renaissance-chirper": {
        "runscript": writeJavaAppRunScript,
        "workload": "finagle-chirper",
        "jarfile": "renaissance.jar",
        "args": "-r 10",
        "match_string": "iteration 7 started ======",
    },
    "renaissance-http": {
        "runscript": writeJavaAppRunScript,
        "workload": "finagle-http",
        "jarfile": "renaissance.jar",
        "args": "-r 10",
        "match_string": "iteration 7 started ======",
    },


}