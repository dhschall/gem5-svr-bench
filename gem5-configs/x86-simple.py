#
# Copyright (c) 2024 David Schall and EASE lab
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
# Install dependencies

"""
This script further shows an example of booting an x86 based full system Ubuntu
disk image. The script boots a full system Ubuntu image and starts the function container.
The function is invoked using a test client.

The workflow has two steps
1. Use the "setup" mode to boot the full system from scratch using the KVM core. The
   script will perform functional warming and then take a checkpoint of the system.
2. Use the "evaluation" mode to start from the previously taken checkpoint and perform
   the actual measurements using a detailed core model.

Usage
-----

```
scons build/<ALL|X86>/gem5.opt -j<NUM_CPUS>
./build/<ALL|X86>/gem5.opt x86-simple.py
    --mode <setup/evaluation> --function <function-name>
    --kernel <path-to-vmlinux> --disk <path-to-disk-image>
    --atomic-warming <num-inv-to-warm> --num-invocations <num-inv-to-simulate>
```

"""
import m5

from gem5.coherence_protocol import CoherenceProtocol
from gem5.components.boards.x86_board import X86Board
from gem5.components.memory import DualChannelDDR4_2400
from gem5.components.memory.simple import SingleChannelSimpleMemory
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.isas import ISA
from gem5.resources.resource import obtain_resource,KernelResource,DiskImageResource
from gem5.simulate.exit_event import ExitEvent
from gem5.simulate.simulator import Simulator
from gem5.utils.requires import requires

# This runs a check to ensure the gem5 binary is compiled for X86.
requires(isa_required=ISA.X86)

from gem5.components.cachehierarchies.classic.private_l1_private_l2_cache_hierarchy import (
    PrivateL1PrivateL2CacheHierarchy,
)

import os
from pathlib import Path


import argparse
def parse_arguments():
    parser = argparse.ArgumentParser(description=
                        "gem5 config file to run vSwarm benchmarks")
    parser.add_argument("--kernel", type = str, help = "Path to vmlinux")
    parser.add_argument("--disk", type = str,
                  help = "Path to the disk image containing your function image")
    parser.add_argument("-f", "--function", action="store", type=str, default="nodeapp",
                        help="""Specify a function that should run in the simulator.""")
    parser.add_argument("--atomic-warming", type=int, default=100,
                        help="""Perform warming of the cache hierarchy using the atomic core.""")
    parser.add_argument("--num-invocations", type=int, default=40,
                        help="""Number of invocation to be measured.""")
    parser.add_argument("--mode", type=str, default="setup",choices=["setup", "evaluation",],
                        help="""Setup mode: Will boot linux using the kvm core, perform functional
                                warming and then take a snapshot.
                                Evaluation mode: Will start from a previously taken checkpoint
                                do some """)
    parser.add_argument("--checkpoint-dir", type = str, default="checkpoints/",
                        help = "Directory of")
    return parser.parse_args()


args = parse_arguments()

if args.mode == "setup":
    Path("{}/{}".format(args.checkpoint_dir, args.function)).mkdir(parents=True, exist_ok=True)




cfgs = {
    "nodeapp": {
        "urlfile": "nodeapp.urls.tmpl",
        "dcfile": "dc-nodeapp.yaml",
        "container": "nodeapp",
    },
}






# Here we setup the parameters of the l1 and l2 caches.
cache_hierarchy = PrivateL1PrivateL2CacheHierarchy(
    l1d_size="32kB", l1i_size="32kB", l2_size="1MB"
)

# Memory: Dual Channel DDR4 2400 DRAM device.
memory = DualChannelDDR4_2400(size="2GB")

# Here we setup the processor. For booting we take the KVM core and
# for the evaluation we can take ATOMIC, TIMING or O3
# eval_core = CPUTypes.ATOMIC
eval_core = CPUTypes.TIMING
# eval_core = CPUTypes.O3

processor = SimpleProcessor(
    cpu_type=CPUTypes.KVM if args.mode=="setup" else eval_core,
    isa=ISA.X86,
    num_cores=2,
)


# Here we setup the board. The ArmBoard allows for Full-System ARM simulations.
board = X86Board(
    clk_freq="3GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)



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
sudo GOGC=1000 /{home}/http-client -f /{home}/{urlfile} -url {test_ip} -c {conc} -n {n_invocations} -w {n_warming} -m5ops -m5iv 1 -v



m5 --addr=0x10010000 exit ## 4: Stop client
# -------------------------------------------


## Stop container
sudo docker compose -f /{home}/{dcfile} down
m5 --addr=0x10010000 exit ## 5: Container stop


## exit the simulations
m5 --addr=0x10010000 exit ## 6: Test done

"""


def workitems(start) -> bool:
    cnt = 1
    while True:
        if start:
            print("Begin Invocation ", cnt)
            # args.mode == "evaluation" and m5.stats.reset()
        else:
            print("End Invocation ", cnt)
            args.mode == "evaluation" and m5.stats.dump()
            cnt += 1

        if args.mode == "evaluation" and cnt >= args.num_invocations:
            yield True
        yield False


def executeExit() -> bool:

    if args.mode == "setup":

        print("1: BOOTING complete")
        yield False

        print("2: Started container")
        yield False

        print("3: Pinned container")
        yield False

        print("4: Stop client")
        yield False

        print("5: Stop container")
        yield False

        print("6: Stop simulation")
        yield True

    else:
        print("Simulation done")
        m5.stats.dump()
        m5.exit()



def executeFail() -> bool:
    
    while True:
        fc = simulator.get_last_exit_event_code()
        print("Fail code: ", fc)
        if fc == 4:
            if args.mode == "setup":
                m5.checkpoint("{}/{}".format(args.checkpoint_dir, args.function))

        yield False




# Here we set a full system workload.
board.set_kernel_disk_workload(
    kernel=KernelResource(args.kernel),
    disk_image=DiskImageResource(args.disk),
    readfile_contents=writeRunScript(cfgs[args.function], 1),
    kernel_args=['earlyprintk=ttyS0', 'console=ttyS0', 'lpj=7999923',
                 'root=/dev/sda1',
                 'isolcpus=1',
                 'cloud-init=disabled'
                ],
    checkpoint=Path("{}/{}".format(args.checkpoint_dir, args.function)) if args.mode=="evaluation" else None,
)

class MySimulator(Simulator):
    def get_last_exit_event_code(self):
        return self._last_exit_event.getCode()


# We define the system with the aforementioned system defined.
simulator = MySimulator(
    board=board,
    on_exit_event={
        # ExitEvent.EXIT: (func() for func in [processor.switch]),
        ExitEvent.WORKBEGIN: workitems(True),
        ExitEvent.WORKEND: workitems(False),
        ExitEvent.EXIT: executeExit(),
        ExitEvent.FAIL: executeFail(),
        },
)

# Once the system successfully boots, it encounters an
# `m5_exit instruction encountered`. We stop the simulation then. When the
# simulation has ended you may inspect `m5out/board.terminal` to see
# the stdout.
simulator.run()
