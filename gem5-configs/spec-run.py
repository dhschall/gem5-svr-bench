# Copyright (c) 2024 The Regents of the University of California
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Usage
-----

gem5 -re --outdir=simpoint[sid]-run simpoint-run.py --sid=[sid]

"""

import argparse
from pathlib import Path

from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.isas import ISA
from gem5.utils.simpoint import SimPoint
from gem5.simulate.simulator import Simulator
from gem5.resources.resource import BinaryResource, SimpointDirectoryResource
from gem5.utils.requires import requires
import m5

from m5.objects import (
    Cache,
    SimpleBTB,
    LTAGE,
    TAGE_SC_L_64KB,
    TAGE_SC_L_TAGE_64KB,
    ITTAGE,
    MultiPrefetcher,
    TaggedPrefetcher,
    L2XBar,
)

from gem5.simulate.exit_event import ExitEvent
from gem5.simulate.simulator import Simulator
from gem5.utils.requires import requires
from gem5.components.boards.abstract_board import AbstractBoard
from gem5.components.cachehierarchies.classic.caches.l1icache import L1ICache
from gem5.components.cachehierarchies.classic.caches.mmu_cache import MMUCache
from gem5.components.cachehierarchies.classic.caches.l1dcache import L1DCache
from gem5.components.cachehierarchies.classic.caches.l2cache import L2Cache
from gem5.components.cachehierarchies.classic.private_l1_cache_hierarchy import PrivateL1CacheHierarchy
from gem5.components.cachehierarchies.classic.private_l1_private_l2_cache_hierarchy import PrivateL1PrivateL2CacheHierarchy
from gem5.components.memory import DualChannelDDR4_2400
from m5.objects.FuncUnit import *
from m5.objects.FuncUnitConfig import *
from m5.objects.FUPool import *


from util.arguments_spec import *
from util.specbms import wlcfg

requires(isa_required=isa_choices[args.isa])

width = args.width
factor = args.factor


processor = SimpleProcessor(
   cpu_type=cpu_types[args.cpu_type],
    isa=isa_choices[args.isa],
    num_cores=1,
)

cpu = processor.cores[-1].core

#This function rounds the number to the closet power of 2
def RTCPO2(n):
    if n < 1:
        return 1

    lower = 1 << (n.bit_length() - 1)
    upper = lower << 1

    return lower if (n - lower) < (upper - n) else upper  


class BTB(SimpleBTB):
    numEntries = RTCPO2(32 * 1024 * factor)
    tagBits = 32
   # associativity = 8


class BPLTage(LTAGE):
    instShiftAmt = 0
    btb = BTB()
    #indirectBranchPred=ITTAGE()
    requiresBTBHit = True

class TAGE_Inf_N(TAGE_SC_L_TAGE_64KB):
    logTagTableSize = 20
    shortTagsSize = 20
    longTagsSize = 20 
class BPTageSCL(TAGE_SC_L_64KB):
    instShiftAmt = 0
    btb = BTB()
    indirectBranchPred = ITTAGE()
    """ indirectBranchPred.itage.tagTableTagWidths = [
        0,
        20,
        20,
        20,
        20,
        20,
        20,
        20,
        20,
        20,
        20,
        20,
        20,
        20,
        20,
        20,
    ]
    indirectBranchPred.itage.logTagTableSizes = [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20]
    tage = TAGE_Inf_N() """
    requiresBTBHit = True
    updateBTBAtSquash = True

# -------------- Backend Configutation --------- #
#-----------------------------------------------
class S_IntALU(IntALU):
    count = 12 * factor

class S_IntMultDiv(IntMultDiv):
    count = 6 * factor

class S_FP_ALU(FP_ALU):
    count = 6 * factor

class S_FP_MultDiv(FP_MultDiv):
    count = 6 * factor

class S_SIMD_Unit(SIMD_Unit):
    count = 6 * factor

class S_Matrix_Unit(Matrix_Unit):
    count = 1 * factor

class S_PredALU(PredALU):
    count = 1 * factor

class S_ReadPort(ReadPort):
    count = 4 * factor

class S_WritePort(WritePort):
    count = 4 * factor

class S_RdWrPort(RdWrPort):
    count = 8 * factor

class S_IprPort(IprPort):
    count = 1 * factor

class S_FUPool(FUPool):
    FUList = [
        S_IntALU(),
        S_IntMultDiv(),
        S_FP_ALU(),
        S_FP_MultDiv(),
        S_ReadPort(),
        S_SIMD_Unit(),
        S_Matrix_Unit(),
        S_PredALU(),
        S_WritePort(),
        S_RdWrPort(),
        S_IprPort(),
    ]
#-----------------------------------------------
#-----------------------------------------------#

def scale_registers(cpu_, factor):

    cpu_.numPhysIntRegs = ceil(500 * factor)
    cpu_.numPhysFloatRegs = ceil(400 * factor)
    cpu_.numPhysVecRegs = ceil(256 * factor)
    cpu_.numPhysVecPredRegs = ceil(32 * factor)
    cpu_.numPhysMatRegs = ceil(2 * factor)
    cpu_.numPhysCCRegs = 5*cpu_.numPhysIntRegs
    return

def set_width(cpu_, width):
    cpu_.fetchWidth = width
    cpu_.decodeWidth = width
    cpu_.renameWidth = width
    cpu_.issueWidth = width
    cpu_.wbWidth = width
    cpu_.commitWidth = width
    cpu_.squashWidth = width
    cpu_.dispatchWidth = width

# Configure the branch predictor
cpu.branchPred = BPTageSCL()

if args.fdp:
    # We need to configure the decoupled front-end with some specific parameters.
    # First the fetch buffer and fetch target size. We want double the size of
    # the fetch buffer to be able to run ahead of fetch
    cpu.decoupledFrontEnd = True
    cpu.fetchBufferSize = 64
    cpu.fetchQueueSize = 128 * factor
    cpu.fetchTargetWidth = 64
    cpu.minInstSize = 1 if args.isa == "X86" else 4

    # Set size if relevant buffers
    cpu.numFTQEntries = 50 * factor
    cpu.numROBEntries = 576 * factor
    cpu.numIQEntries = 300 * 2 * factor
    cpu.LQEntries = 200 * factor
    cpu.SQEntries = 200 * factor
    cpu.LFSTSize = RTCPO2(1024 * factor)
    cpu.SSITSize = "{}".format(RTCPO2(1024 * factor))

    # number of set number of prefetches issued by fetch stage
    cpu.maxPrefetchesPerCycle= 2* args.ppc
    cpu.maxOutstandingTranslations=8 * args.ppc
    cpu.maxOutstandingPrefetches=8 * args.ppc

    # Custom functional unit configuration
    cpu.fuPool = S_FUPool()

    # Return address stack size
    cpu.branchPred.ras.numEntries=128

    # Scaling the number of registers used for renaming
    scale_registers(cpu, factor)

    cpu.numPredPerCycle = args.ppc

    #Setting the width of the different stages  
    set_width (cpu, width)

    #tune mmu 
    cpu.mmu.l2_shared.size = RTCPO2(3840 * factor)
    cpu.mmu.l2_shared.assoc = 8
    cpu.mmu.itb.size = RTCPO2(256 * factor)
    cpu.mmu.dtb.size = RTCPO2(256 * factor)
    cpu.mmu.stage2_itb.size = RTCPO2(256 * factor)
    cpu.mmu.stage2_dtb.size = RTCPO2(256 * factor)
   


##############################################################
# Cache Hierarchy
##############################################################

class L1ICacheGiant(Cache):
    size = "32MiB"
    assoc = 8
    tag_latency = 1
    data_latency = 1
    response_latency = 1
    mshrs = 32
    tgts_per_mshr = 20
    writeback_clean = True


class L1DCacheGiant(Cache):
    size = "32MiB"
    assoc = 8
    tag_latency = 1
    data_latency = 1
    response_latency = 1
    mshrs = 32
    tgts_per_mshr = 20
    writeback_clean = True


class CacheHierarchyGiant(PrivateL1CacheHierarchy):
    def __init__(self):
        super().__init__(l1d_size="", l1i_size="")

    def incorporate_cache(self, board: AbstractBoard) -> None:
        board.connect_system_port(self.membus.cpu_side_ports)

        for _, port in board.get_mem_ports():
            self.membus.mem_side_ports = port

        self.l1icaches = [
            L1ICacheGiant()
            for i in range(board.get_processor().get_num_cores())
        ]

        self.l1dcaches = [
            L1DCacheGiant()
            for i in range(board.get_processor().get_num_cores())
        ]
        # ITLB Page walk caches
        self.iptw_caches = [
            MMUCache(size="8MiB")
            for _ in range(board.get_processor().get_num_cores())
        ]
        # DTLB Page walk caches
        self.dptw_caches = [
            MMUCache(size="8MiB")
            for _ in range(board.get_processor().get_num_cores())
        ]

        if board.has_coherent_io():
            self._setup_io_cache(board)

        for i, cpu in enumerate(board.get_processor().get_cores()):
            cpu.connect_icache(self.l1icaches[i].cpu_side)
            cpu.connect_dcache(self.l1dcaches[i].cpu_side)

            self.l1icaches[i].mem_side = self.membus.cpu_side_ports
            self.l1dcaches[i].mem_side = self.membus.cpu_side_ports

            self.iptw_caches[i].mem_side = self.membus.cpu_side_ports
            self.dptw_caches[i].mem_side = self.membus.cpu_side_ports

            cpu.connect_walker_ports(
                self.iptw_caches[i].cpu_side, self.dptw_caches[i].cpu_side
            )

            if board.get_processor().get_isa() == ISA.X86:
                int_req_port = self.membus.mem_side_ports
                int_resp_port = self.membus.cpu_side_ports
                cpu.connect_interrupt(int_req_port, int_resp_port)
            else:
                cpu.connect_interrupt()


#cache_hierarchy = CacheHierarchyGiant()

# Memory: Dual Channel DDR4 2400 DRAM device.
memory = DualChannelDDR4_2400(size="3GiB")


# 2. Instruction prefetcher ---------------------------------------------
# The decoupled front-end is only the first part.
# Now we also need the instruction prefetcher which listens to the
# insertions into the fetch target queue (FTQ) to issue prefetches.


class CacheHierarchy(PrivateL1PrivateL2CacheHierarchy):
    def __init__(self, l1i_size, l1d_size, l2_size):
        super().__init__(l1i_size, l1d_size, l2_size)

    def incorporate_cache(self, board: AbstractBoard) -> None:
        board.connect_system_port(self.membus.cpu_side_ports)

        for _, port in board.get_memory().get_mem_ports():
            self.membus.mem_side_ports = port

        self.l1icaches = [
            L1ICache(size=self._l1i_size, mshrs = 32)
            for i in range(board.get_processor().get_num_cores())
        ]
        cpu1 = board.get_processor().cores[-1].core

        self.l1icaches[-1].prefetcher = MultiPrefetcher()
        #if args.fdp:
        #    self.l1icaches[-1].prefetcher.prefetchers.append(
        #        FetchDirectedPrefetcher(use_virtual_addresses=True, cpu=cpu1)
        #   )
        self.l1icaches[-1].prefetcher.prefetchers.append(
                TaggedPrefetcher(use_virtual_addresses=True)
            )

        for pf in self.l1icaches[-1].prefetcher.prefetchers:
            pf.registerMMU(cpu1.mmu)

        self.l1dcaches = [
            L1DCache(size=self._l1d_size, mshrs = 32)
            for i in range(board.get_processor().get_num_cores())
        ]
        self.l2buses = [
            L2XBar() for i in range(board.get_processor().get_num_cores())
        ]
        self.l2caches = [
            L2Cache(size=self._l2_size)
            for i in range(board.get_processor().get_num_cores())
        ]
        self.mmucaches = [
            MMUCache(size="{}KiB".format(RTCPO2(16*factor)))
           # MMUCache(size="128KiB")
            for _ in range(board.get_processor().get_num_cores())
        ]

        self.mmubuses = [
            L2XBar(width=64) for i in range(board.get_processor().get_num_cores())
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
    l1i_size="{}KiB".format(RTCPO2(64*factor)), l1d_size="{}KiB".format(RTCPO2(64*factor)), l2_size="{}MB".format(RTCPO2(2*factor))
)

#cache_hierarchy = CacheHierarchy("1024KiB", "1024KiB", "8192KiB")



# Here we setup the board.
if args.isa == "Arm":
    #  The ArmBoard allows for Full-System ARM simulations.
    from gem5.components.boards.arm_board import ArmBoard
    from m5.objects import (
        ArmDefaultRelease,
        VExpress_GEM5_V1,
    )

    board = ArmBoard(
        clk_freq="3GHz",
        processor=processor,
        memory=memory,
        cache_hierarchy=cache_hierarchy,
        # The ArmBoard requires a `release` to be specified. This adds all the
        # extensions or features to the system. We are setting this to Armv8
        # (ArmDefaultRelease) in this example config script.
        release = ArmDefaultRelease.for_kvm(),
        # The platform sets up the memory ranges of all the on-chip and
        # off-chip devices present on the ARM system. ARM KVM only works with
        # VExpress_GEM5_V1 on the ArmBoard at the moment.
        platform = VExpress_GEM5_V1(),
    )

elif args.isa == "X86":
    # The X86Board allows for Full-System X86 simulations.
    from gem5.components.boards.x86_board import X86Board
    board = X86Board(
        clk_freq="3GHz",
        processor=processor,
        memory=memory,
        cache_hierarchy=cache_hierarchy,
    )
else:
    raise ValueError("ISA not supported")


simpoint_info = SimpointDirectoryResource(
    local_path=Path(f"{args.simpoint_dir}/{args.workload}"),
    simpoint_file="results.simpts",
    weight_file="results.weights",
    simpoint_interval=200_000_000,
    warmup_interval=100_000_000
)

board.set_se_simpoint_workload(
    binary=BinaryResource(wlcfg[args.workload]["cmd"]),
    arguments=wlcfg[args.workload]["args"],
    simpoint=simpoint_info,
    checkpoint=Path(f"{args.checkpoint_dir}/{args.workload}/cpt.SimPoint{args.sid}")
)

def max_inst():
    warmed_up = False
    while True:
        if warmed_up:
            print("end of SimPoint interval")
            yield True
        else:
            print("end of warmup, starting to simulate SimPoint")
            warmed_up = True
            # Schedule a MAX_INSTS exit event during the simulation
            simulator.schedule_max_insts(
                board.get_simpoint().get_simpoint_interval()
            )
            m5.stats.dump()
            m5.stats.reset()
            yield False

simulator = Simulator(
    board=board,
    on_exit_event={ExitEvent.MAX_INSTS: max_inst()},
)

warmup_interval = board.get_simpoint().get_warmup_list()[args.sid]
if warmup_interval == 0:
    warmup_interval = 1

print(f"Starting simulating SimPoint {args.sid} with weight {board.get_simpoint().get_weight_list()[args.sid]}")
print(f"Starting warmup interval {warmup_interval}")
simulator.schedule_max_insts(warmup_interval)
simulator.run()

print("Simulation Done")
print(f"Ran SimPoint {args.sid} with weight {board.get_simpoint().get_weight_list()[args.sid]}")
