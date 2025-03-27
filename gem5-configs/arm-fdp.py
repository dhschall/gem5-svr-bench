# Copyright (c) 2025 Technical University of Munich
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
This script further shows an example of booting an ARM based full system Ubuntu
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
scons build/<ALL|ARM>/gem5.opt -j<NUM_CPUS>
./build/<ALL|ARM>/gem5.opt arm-fdp.py
    --mode <setup/eval> --function <function-name>
    --kernel <path-to-vmlinux> --disk <path-to-disk-image>
    --atomic-warming <num-inv-to-warm> --num-invocations <num-inv-to-simulate>
```

"""
import m5

from gem5.components.boards.arm_board import ArmBoard
from gem5.components.boards.x86_board import X86Board
from gem5.components.memory import DualChannelDDR4_2400
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.isas import ISA
from gem5.resources.resource import KernelResource,DiskImageResource, obtain_resource
from gem5.simulate.exit_event import ExitEvent
from gem5.simulate.simulator import Simulator
from gem5.utils.requires import requires
from gem5.components.boards.abstract_board import AbstractBoard
from gem5.components.cachehierarchies.classic.caches.l1icache import L1ICache
from gem5.components.cachehierarchies.classic.caches.mmu_cache import MMUCache
from gem5.components.cachehierarchies.classic.caches.l1dcache import L1DCache
from gem5.components.cachehierarchies.classic.caches.l2cache import L2Cache
from gem5.components.cachehierarchies.classic.private_l1_private_l2_cache_hierarchy import (
    PrivateL1PrivateL2CacheHierarchy
)

from pathlib import Path

from util.workloads import *
from util.arguments import *


# This runs a check to ensure the gem5 binary is compiled for ARM.
requires(isa_required=ISA.ARM)

from m5.objects import (
    LTAGE,
    SimpleBTB,
    SimpleIndirectPredictor,
    TAGEBase,
    TaggedPrefetcher,
    FetchDirectedPrefetcher,
    L2XBar,
    ArmDefaultRelease,
    VExpress_GEM5_V1,
)

checkpoint_dir = "wkdir/checkpoints"

if args.mode == "setup":
    Path("{}/{}".format(checkpoint_dir, args.workload)).mkdir(parents=True, exist_ok=True)


# Here we setup the processor. For booting we take the KVM core and
# for the evaluation we can take ATOMIC, TIMING or O3

processor = SimpleProcessor(
    cpu_type=CPUTypes.KVM if args.mode=="setup" else cpu_types[args.cpu_type],
    isa=ISA.ARM,
    num_cores=2,
)
cpu = processor.cores[-1].core




## FDP needs the AssociativeBTB.
class BTB(SimpleBTB):
    numEntries = 8192
    associativity = 4

class IndirectPred(SimpleIndirectPredictor):
    indirectSets = 512 # Cache sets for indirect predictor
    indirectWays = 4 # Ways for indirect predictor
    indirectPathLength = 7 # Previous indirect targets to use for path history
    indirectGHRBits = 16 # Indirect GHR number of bits
    speculativePathLength = 20
    instShiftAmt = 0

class TAGE_64KB_N(TAGEBase):
    # From https://jilp.org/jwac-2/program/cbp3_03_seznec.pdf
    nHistoryTables = 15
    minHist = 8
    maxHist = 2000

    tagTableUBits = 1
    tagTableTagWidths = [0,  8,  8, 11, 11, 11, 11, 11, 13, 13, 13, 13, 13, 13, 14, 14]
    logTagTableSizes = [15, 12, 12, 14, 14, 14, 14, 14, 13, 13, 13, 13, 13, 13, 10, 10]

    numUseAltOnNa=16

    logUResetPeriod=10
    maxNumAlloc=2
    pathHistBits=27
    speculativeHistUpdate=True

    tagTableCounterBits=3
    tagTableUBits=1
    useAltOnNaBits=5

class BPLTage(LTAGE):
    instShiftAmt = 0
    indirectBranchPred = IndirectPred()
    BTB = BTB()
    tage = TAGE_64KB_N(maxHist=2000)
    requiresBTBHit = True



cpu.branchPred = BPLTage()
cpu.branchPred.tage.speculativeHistUpdate=True

cpu.fetchBufferSize = 16
cpu.fetchTargetWidth = 32

if args.fdp:
    # We need to configure the decoupled front-end with some specific parameters.
    # First the fetch buffer and fetch target size. We want double the size of
    # the fetch buffer to be able to run ahead of fetch
    print("!! FDP enabled !!")
    cpu.bacBranchPredictDelay = 1
    cpu.minInstSize = 1
    cpu.decoupledFrontEnd = True


# 2. Instruction prefetcher ---------------------------------------------
# The decoupled front-end is only the first part.
# Now we also need the instruction prefetcher which listens to the
# insertions into the fetch target queue (FTQ) to issue prefetches.

# Create the icache and the prefetcher
icache = L1ICache(size="32kB")

if not args.fdp:
    # If FDP is disabled we use the TaggedPrefetcher (Next-Line Prefetcher)
    icache.prefetcher = TaggedPrefetcher()
else:
    ## Setup the FDP prefetcher
    icache.prefetcher = FetchDirectedPrefetcher(
        use_virtual_addresses=True,
        # The FDP prefetcher needs to know to which CPU to listent to.
        cpu=cpu,
    )

# Register the MMU to allow address translation
icache.prefetcher.registerMMU(processor.cores[0].core.mmu)


class CacheHierarchy(PrivateL1PrivateL2CacheHierarchy):
    def __init__(self, l1i_size, l1d_size, l2_size):
        super().__init__(l1i_size, l1d_size, l2_size)

    def incorporate_cache(self, board: AbstractBoard) -> None:
        board.connect_system_port(self.membus.cpu_side_ports)

        for _, port in board.get_memory().get_mem_ports():
            self.membus.mem_side_ports = port

        self.l1icaches = [
            L1ICache(size=self._l1i_size)
            for i in range(board.get_processor().get_num_cores())
        ]
        cpu1 = board.get_processor().cores[1].core

        self.l1icaches[1].prefetcher = FetchDirectedPrefetcher(use_virtual_addresses=True, cpu=cpu1)

        self.l1icaches[1].prefetcher.registerMMU(cpu1.mmu)

        self.l1dcaches = [
            L1DCache(size=self._l1d_size)
            for _ in range(board.get_processor().get_num_cores())
        ]
        self.l2buses = [
            L2XBar() for _ in range(board.get_processor().get_num_cores())
        ]
        self.l2caches = [
            L2Cache(size=self._l2_size)
            for _ in range(board.get_processor().get_num_cores())
        ]
        self.mmucaches = [
            MMUCache(size="8KiB")
            for _ in range(board.get_processor().get_num_cores())
        ]

        self.mmubuses = [
            L2XBar(width=64) for _ in range(board.get_processor().get_num_cores())
        ]


        if board.has_coherent_io():
            self._setup_io_cache(board)

        for i, cpu in enumerate(board.get_processor().get_cores()):

            cpu.connect_icache(self.l1icaches[i].cpu_side)
            cpu.connect_dcache(self.l1dcaches[i].cpu_side)

            self.l1icaches[i].mem_side = self.l2buses[i].cpu_side_ports
            self.l1dcaches[i].mem_side = self.l2buses[i].cpu_side_ports
            self.mmucaches[i].mem_side = self.l2buses[i].cpu_side_ports

            self.mmubuses[i].mem_side_ports = self.mmucaches[i].cpu_side
            self.l2buses[i].mem_side_ports = self.l2caches[i].cpu_side

            self.membus.cpu_side_ports = self.l2caches[i].mem_side

            cpu.connect_walker_ports(
                self.mmubuses[i].cpu_side_ports, self.mmubuses[i].cpu_side_ports
            )

            if board.get_processor().get_isa() == ISA.X86:
                int_req_port = self.membus.mem_side_ports
                int_resp_port = self.membus.cpu_side_ports
                cpu.connect_interrupt(int_req_port, int_resp_port)
            else:
                cpu.connect_interrupt()


cache_hierarchy = CacheHierarchy(
    l1i_size="32KiB", l1d_size="32KiB", l2_size="1MB"
)

memory = DualChannelDDR4_2400(size="3GB")


# The ArmBoard requires a `release` to be specified. This adds all the
# extensions or features to the system. We are setting this to Armv8
# (ArmDefaultRelease) in this example config script.
release = ArmDefaultRelease.for_kvm()

# The platform sets up the memory ranges of all the on-chip and off-chip
# devices present on the ARM system. ARM KVM only works with VExpress_GEM5_V1
# on the ArmBoard at the moment.
platform = VExpress_GEM5_V1()

# Here we setup the board. The ArmBoard allows for Full-System ARM simulations.
board = ArmBoard(
    clk_freq="3GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
    release=release,
    platform=platform,
)


def executeExit():
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
        yield True



def executeFail():
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


def maxInsts():
    sim_instr = 0
    max_instr = 10_000_000_000

    while True:
        m5.stats.dump() 
        m5.stats.reset()
        sim_instr += delta
        print("Simulated Instructions: ", sim_instr)
        processor.cores[-1]._set_inst_stop_any_thread(delta, True)
        if sim_instr >= max_instr:
            yield True
        yield False



# Here we set a full system workload.
board.set_kernel_disk_workload(
    kernel=KernelResource(args.kernel),
    disk_image=DiskImageResource(args.disk),
    bootloader=obtain_resource("arm64-bootloader"),
    readfile_contents=wlcfg[args.workload]["runscript"](wlcfg[args.workload], 1),
    kernel_args=["console=ttyAMA0",
                 "lpj=19988480", "norandmaps",
                 "root=/dev/vda2", "disk_device=/dev/vda2",
                 'isolcpus=1',
                 'cloud-init=disabled',
                 'mitigations=off',
                ],
    checkpoint=Path("{}/{}".format(checkpoint_dir, args.workload)) if args.mode=="eval" else None,
)

class MySimulator(Simulator):
    def get_last_exit_event_code(self):
        return self._last_exit_event.getCode()


simulator = MySimulator(
    board=board,
    on_exit_event={
        ExitEvent.EXIT: executeExit(),
        ExitEvent.FAIL: executeFail(),
        ExitEvent.MAX_INSTS: maxInsts(),
    },
)



if args.mode == "eval":
    processor.cores[-1]._set_inst_stop_any_thread(delta, False)


# Once the system successfully boots, it encounters an
# `m5_exit instruction encountered`. We stop the simulation then. When the
# simulation has ended you may inspect `m5out/board.terminal` to see
# the stdout.
simulator.run()

print("Simulation finished at tick {} because {}.".format(
    m5.curTick(), simulator.get_last_exit_event_code()
))