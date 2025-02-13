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
# Install dependencies

"""
This script further shows an example of booting an x86 based full system Ubuntu
disk image. The script boots a full system Ubuntu image and starts the function container.
The function is invoked using a test client.

The workflow has two steps
1. Use the "setup" mode to boot the full system from scratch using the KVM core. The
   script will perform functional warming and then take a checkpoint of the system.
2. Use the "eval" mode to start from the previously taken checkpoint and perform
   the actual measurements using a detailed core model.

Usage
-----

```
scons build/<ALL|X86>/gem5.opt -j<NUM_CPUS>
./build/<ALL|X86>/gem5.opt x86-simple.py
    --mode <setup/eval> --function <function-name>
    --kernel <path-to-vmlinux> --disk <path-to-disk-image>
    --atomic-warming <num-inv-to-warm> --num-invocations <num-inv-to-simulate>
```

"""
import m5

from gem5.components.boards.x86_board import X86Board
from gem5.components.memory import DualChannelDDR4_2400
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.isas import ISA
from gem5.resources.resource import KernelResource,DiskImageResource
from gem5.simulate.exit_event import ExitEvent
from gem5.simulate.simulator import Simulator
from gem5.utils.requires import requires

# This runs a check to ensure the gem5 binary is compiled for X86.
requires(isa_required=ISA.X86)

from gem5.components.cachehierarchies.classic.private_l1_private_l2_cache_hierarchy import (
    PrivateL1PrivateL2CacheHierarchy,
)

from pathlib import Path

from util.workloads import *
from util.arguments import *



checkpoint_dir = "wkdir/checkpoints"

if args.mode == "setup":
    Path("{}/{}".format(checkpoint_dir, args.workload)).mkdir(parents=True, exist_ok=True)




# Memory: Dual Channel DDR4 2400 DRAM device.
memory = DualChannelDDR4_2400(size="3GiB")


# Here we setup the parameters of the l1 and l2 caches.
cache_hierarchy = PrivateL1PrivateL2CacheHierarchy(
    l1d_size="32kB", l1i_size="32kB", l2_size="512kB"
)



# Here we setup the processor. For booting we take the KVM core and
# for the evaluation we can take ATOMIC, TIMING or O3

processor = SimpleProcessor(
    cpu_type=CPUTypes.KVM if args.mode=="setup" else cpu_types[args.cpu_type],
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




def workitems(start) -> bool:
    cnt = 1
    while True:
        if start:
            print("Begin Invocation ", cnt)
        else:
            print("End Invocation ", cnt)
            if args.mode == "eval":
                m5.stats.dump()
                m5.stats.reset()

            cnt += 1

        if args.mode == "eval" and cnt >= args.num_invocations:
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
                m5.checkpoint("{}/{}".format(checkpoint_dir, args.workload))
                m5.stats.dump()
                m5.stats.reset()

        yield False



delta = 100_000_000

def maxInsts() -> bool:
    sim_instr = 0
    max_instr = 1_000_000_000_000

    while True:
        m5.stats.dump()
        m5.stats.reset()
        sim_instr += delta
        print("Simulated Instructions: ", sim_instr)
        simulator.schedule_max_insts(delta)
        if sim_instr >= max_instr:
            yield True
        yield False




# Here we set a full system workload.
board.set_kernel_disk_workload(
    kernel=KernelResource(args.kernel),
    disk_image=DiskImageResource(args.disk),
    readfile_contents=wlcfg[args.workload]["runscript"](wlcfg[args.workload], 1),
    kernel_args=['earlyprintk=ttyS0', 'console=ttyS0', 'lpj=7999923',
                 'root=/dev/sda2',
                #  'isolcpus=1',
                 'cloud-init=disabled',
                 'mitigations=off',
                ],
    checkpoint=Path("{}/{}".format(checkpoint_dir, args.workload)) if args.mode=="eval" else None,
)

class MySimulator(Simulator):
    def get_last_exit_event_code(self):
        return self._last_exit_event.getCode()


# We define the system with the aforementioned system defined.
simulator = MySimulator(
    board=board,
    on_exit_event={
        # ExitEvent.EXIT: (func() for func in [processor.switch]),
        # ExitEvent.WORKBEGIN: workitems(True),
        # ExitEvent.WORKEND: workitems(False),
        ExitEvent.EXIT: executeExit(),
        ExitEvent.FAIL: executeFail(),
        ExitEvent.MAX_INSTS: maxInsts(),
        },
)

if args.mode == "eval":
    simulator.schedule_max_insts(delta)

# Once the system successfully boots, it encounters an
# `m5_exit instruction encountered`. We stop the simulation then. When the
# simulation has ended you may inspect `m5out/board.terminal` to see
# the stdout.
simulator.run()
