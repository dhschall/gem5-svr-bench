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

from .workloads import * 
import argparse

cpu_types = {
    "atomic": CPUTypes.ATOMIC,
    "timing": CPUTypes.TIMING,
    "o3": CPUTypes.O3,
}

parser = argparse.ArgumentParser(
    description="gem5 configuration script to run a full system x86 simulation"
)

parser.add_argument(
    "--kernel",
    type=str,
    default="wkdir/kernel",
    help="The kernel image to boot the system.",
)

parser.add_argument(
    "--disk",
    type=str,
    default="wkdir/disk.img",
    help="The disk image to boot the system.",
)

parser.add_argument(
    "-w","--workload",
    action="store",
    type=str,
    choices=wlcfg.keys(),
    default="nodeapp",
    help="""Specify a workload that should run in the simulator.""",
)

parser.add_argument(
    "--atomic-warming",
    type=int,
    default=5000,
    help="""Perform warming of the cache hierarchy using the atomic core.""",
)

parser.add_argument(
    "--num-invocations",
    type=int,
    default=200,
    help="""Number of invocation to be measured.""",
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

parser.add_argument(
    "--cpu-type",
    type=str,
    default="atomic",
    help="The CPU model to use.",
    choices=cpu_types.keys(),
)

parser.add_argument(
    "--disable-fdp",
    action="store_true",
    help="Disable FDP to get evaluate baseline",
)

args = parser.parse_args()

if not args.disable_fdp:
    args.fdp = True
else:
    args.fdp = False