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

from gem5.components.processors.cpu_types import CPUTypes
from gem5.isas import ISA

from .workloads import *
import argparse


parser = argparse.ArgumentParser(
    description="gem5 configuration script to run a full system simulation"
)

parser.add_argument(
    "--kernel",
    type=str,
    default="wkdir4/kernel",
    help="The kernel image to boot the system.",
)

parser.add_argument(
    "--disk",
    type=str,
    default="wkdir4/disk.img",
    help="The disk image to boot the system.",
)

parser.add_argument(
    "-w","--workload",
    action="store",
    type=str,
    default="nodeapp",
    choices=wlcfg.keys(),
    help="""Specify a workload that should run in the simulator.""",
)

parser.add_argument(
    "--mode",
    type=str,
    default="setup",
    choices=["setup", "eval",],
    help="""Setup mode: Will boot linux using the kvm core, perform functional
            warming and then take a snapshot.
            Evaluation mode: Will start from a previously taken checkpoint and
            run the actual measurements using the specified core.""",
)

cpu_types = {
    "atomic": CPUTypes.ATOMIC,
    "timing": CPUTypes.TIMING,
    "o3": CPUTypes.O3,
}

parser.add_argument(
    "--cpu-type",
    type=str,
    default="atomic",
    help="The CPU model to use.",
    choices=cpu_types.keys(),
)

parser.add_argument(
    "--fdp",
    action="store_true",
    default=False,
    help="Enable FDP",
)

parser.add_argument(
    "--inf_tage",
    action="store_true",
    default=False,
    help="Enable Infinite TAGE branch predictor",
)

parser.add_argument(
    "--inf_phast",
    action="store_true",
    default=False,
    help="Enable Infinite PHAST memory dependency predictor",
)

parser.add_argument(
    "--big_squash",
    action="store_true",
    default=False,
    help="Set the the squash width equal to ROB size",
)

parser.add_argument(
    "--giant_cache",
    action="store_true",
    default=False,
    help="Set the cache hierarchy to giant cache mode",
)

isa_choices = {
    "X86": ISA.X86,
    "Arm": ISA.ARM,
    "RiscV": ISA.RISCV,
}

parser.add_argument(
    "--isa",
    type=str,
    default="X86",
    help="The ISA to simulate.",
    choices=isa_choices.keys(),
)

parser.add_argument(
    "--width",
    type=int,
    default=12,
    help="The width of the pipeline to simulate."
)


parser.add_argument(
    "--factor",
    type=int,
    default=1,
    help="The factor to scale the pipeline capacity."
)

parser.add_argument(
    "--ppc",
    type=int,
    default=0, 
    help="The number of prediction per cycle to simulate."
)

parser.add_argument(
    "--data_point",
    type=int,
    default=10,
    help="The number of data points to simulate"
)

parser.add_argument(
    "--fbInFTQ",
    action="store_true",
    default=False,
    help="Enable the Fetch target queue to store the fetch block information in the FTQ"
)

args = parser.parse_args()


def isa_to_arch(isa: str) -> str:
    match isa:
        case "X86": return "amd64"
        case "Arm": return "arm64"
        case "RiscV": return "riscv"
        case _: raise ValueError(f"Unsupported ISA: {isa}")