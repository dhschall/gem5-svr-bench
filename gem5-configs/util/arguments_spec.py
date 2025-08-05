from gem5.components.processors.cpu_types import CPUTypes
from gem5.isas import ISA

import argparse
from specbms import wlcfg



parser = argparse.ArgumentParser(
    description="gem5 configuration script to run a SPEC 2017 simulations"
)

parser.add_argument("--sid", type=int, required=True)
parser.add_argument("--checkpoint-dir", type=str, default="simpoint-checkpoint",)
parser.add_argument("--simpoint-dir", type=str, default="./",)
parser.add_argument("cmd", nargs=argparse.REMAINDER)
parser.add_argument(
    "--workload",
    type=str,
    required=True,
    choices=list(wlcfg.keys()),
    help="The workload to run",
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
    default=1, 
    help="The number of prediction per cycle to simulate."
)

parser.add_argument(
    "--data_point",
    type=int,
    default=10,
    help="The number of data points to simulate"
)


args = parser.parse_args()