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

"""
This file contains utility functions for configuring simulations in using multiple branch prediction.
"""
from gem5.isas import ISA
from m5.objects import (
    Cache,
    SimpleBTB,
    TAGE_SC_L_64KB,
    TAGE_SC_L_TAGE_64KB,
    ITTAGE,
    MultiPrefetcher,
    TaggedPrefetcher,
    L2XBar,
)
from gem5.components.boards.abstract_board import AbstractBoard
from gem5.components.cachehierarchies.classic.caches.l1icache import L1ICache
from gem5.components.cachehierarchies.classic.caches.mmu_cache import MMUCache
from gem5.components.cachehierarchies.classic.caches.l1dcache import L1DCache
from gem5.components.cachehierarchies.classic.caches.l2cache import L2Cache
from gem5.components.cachehierarchies.classic.private_l1_cache_hierarchy import PrivateL1CacheHierarchy
from gem5.components.cachehierarchies.classic.private_l1_private_l2_cache_hierarchy import PrivateL1PrivateL2CacheHierarchy
from m5.objects.FuncUnit import *
from m5.objects.FuncUnitConfig import *
from m5.objects.FUPool import *

from math import ceil

#############################################################
######################### Functions #########################
############################################################


#This function rounds the number to the closet power of 2
def RTCPO2(n):
    if n < 1:
        return 1
    lower = 1 << (n.bit_length() - 1)
    upper = lower << 1
    return lower if (n - lower) < (upper - n) else upper   

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

# Configure the CPU with the specified arguments
def configure_cpu(cpu, args):
    if args.fdp:
        #Enable the decoupled front-end
        cpu.decoupledFrontEnd = True
        #set branch predictor
        cpu.branchPred = BPTageSCL(args.inf_tage)
        cpu.branchPred.btb = BTB(args.factor)
        #configure frontend
        cpu.fetchBufferSize = 64
        cpu.fetchQueueSize = 128 * args.factor
        cpu.fetchTargetWidth = 64
        cpu.minInstSize = 1 if args.isa == "X86" else 4

         # Set size of relevant buffers
        cpu.numFTQEntries = 50 * args.factor
        cpu.numROBEntries = 576 * args.factor
        cpu.numIQEntries = 300 * 2 * args.factor
        cpu.LQEntries = 200 * args.factor
        cpu.SQEntries = 200 * args.factor

        # configure multiple branch prediction
        if args.ppc > 0:
            cpu.maxPrefetchesPerCycle= 2* args.ppc
            cpu.maxOutstandingTranslations=8 * args.ppc
            cpu.maxOutstandingPrefetches=8 * args.ppc
            cpu.numPredPerCycle = args.ppc

        # Custom functional unit configuration
        cpu.fuPool = S_FUPool(args.factor)

        # Return address stack size
        cpu.branchPred.ras.numEntries=128

        # Scaling the number of registers used for renaming
        scale_registers(cpu, args.factor)


        #Setting the width of the different stages  
        set_width (cpu, args.width)

        if args.big_squash:
            cpu.squashWidth = cpu.numROBEntries

        #tuning phast
        if args.inf_phast:
            cpu.phast_num_rows = 256
            cpu.phast_associativity = 8
            cpu.phast_tag_bits = 16
            cpu.phast_max_counter = 100
            cpu.LSQDepCheckShift = 2

        #tune mmu 
        cpu.mmu.l2_shared.size = RTCPO2(3840 * args.factor)
        cpu.mmu.l2_shared.assoc = 8
        cpu.mmu.itb.size = RTCPO2(256 * args.factor)
        cpu.mmu.dtb.size = RTCPO2(256 * args.factor)
        cpu.mmu.stage2_itb.size = RTCPO2(256 * args.factor)
        cpu.mmu.stage2_dtb.size = RTCPO2(256 * args.factor)

    else:
        exit("This script is meant to be used with FDP enabled for mutiple branch prediction. Please use the --fdp flag.")
    
   
#Configure the cache hierarchy based on the arguments
def configure_cache(args):
    return CacheHierarchyGiant() if args.giant_cache else CacheHierarchy(
    l1i_size="{}KiB".format(RTCPO2(64*args.factor)), l1d_size="{}KiB".format(RTCPO2(64*args.factor)), l2_size="{}MB".format(RTCPO2(2*args.factor), factor=args.factor)
    ) 


#############################################################
########### Classes for the different components ###########
############################################################

                             
class BTB(SimpleBTB):
    def __init__(self, factor):
        super().__init__()
        self.numEntries = RTCPO2(32 * 1024 * factor)
    tagBits = 32
    associativity = 8

class TAGE_Inf_N(TAGE_SC_L_TAGE_64KB):
    logTagTableSize = 20
    shortTagsSize = 20
    longTagsSize = 20 

class BPTageSCL(TAGE_SC_L_64KB):
    def __init__(self, inf_tage :bool = False):
        super().__init__()
        if inf_tage:
            self.indirectBranchPred.itage.tagTableTagWidths = [
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
            self.indirectBranchPred.itage.logTagTableSizes = [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20]
            self.tage = TAGE_Inf_N()       

    instShiftAmt = 0
    indirectBranchPred = ITTAGE()
    requiresBTBHit = True
    updateBTBAtSquash = True

# -------------- Backend Configutation --------- #
#-----------------------------------------------
class S_IntALU(IntALU):
    def __init__(self, factor):
        super().__init__()
        self.count = 12 * factor

class S_IntMultDiv(IntMultDiv):
    def __init__(self, factor):
        super().__init__()
        self.count = 6 * factor

class S_FP_ALU(FP_ALU):
    def __init__(self, factor):
        super().__init__()
        self.count = 6 * factor

class S_FP_MultDiv(FP_MultDiv):
    def __init__(self, factor):
        super().__init__()
        self.count = 6 * factor

class S_SIMD_Unit(SIMD_Unit):
    def __init__(self, factor):
        super().__init__()
        self.count = 6 * factor

class S_Matrix_Unit(Matrix_Unit):
    def __init__(self, factor):
        super().__init__()
        self.count = 1 * factor

class S_PredALU(PredALU):
    def __init__(self, factor):
        super().__init__()
        self.count = 1 * factor

class S_ReadPort(ReadPort):
    def __init__(self, factor):
        super().__init__()
        self.count = 4 * factor

class S_WritePort(WritePort):
    def __init__(self, factor):
        super().__init__()
        self.count = 4 * factor

class S_RdWrPort(RdWrPort):
    def __init__(self, factor):
        super().__init__()
        self.count = 8 * factor

class S_IprPort(IprPort):
    def __init__(self, factor):
        super().__init__()
        self.count = 1 * factor

class S_FUPool(FUPool):
    def __init__(self, factor=1):
        super().__init__()
        self.FUList = [
            S_IntALU(factor=factor),
            S_IntMultDiv(factor=factor),
            S_FP_ALU(factor=factor),
            S_FP_MultDiv(factor=factor),
            S_ReadPort(factor=factor),
            S_SIMD_Unit(factor=factor),
            S_Matrix_Unit(factor=factor),
            S_PredALU(factor=factor),
            S_WritePort(factor=factor),
            S_RdWrPort(factor=factor),
            S_IprPort(factor=factor),
        ]
#-----------------------------------------------
#-----------------------------------------------#


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



# 2. Instruction prefetcher ---------------------------------------------
#Cache hierarchy with prefetchers

class CacheHierarchy(PrivateL1PrivateL2CacheHierarchy):
    def __init__(self, l1i_size, l1d_size, l2_size, factor=1):
        super().__init__(l1i_size, l1d_size, l2_size)
        #self.scaling_factor = factor
        self._factor = factor

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
            MMUCache(size="{}KiB".format(RTCPO2(16*self._factor)))
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




