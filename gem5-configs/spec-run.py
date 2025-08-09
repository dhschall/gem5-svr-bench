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
from pathlib import Path

from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.utils.simpoint import SimPoint
from gem5.simulate.simulator import Simulator
from gem5.resources.resource import BinaryResource, SimpointDirectoryResource
from gem5.utils.requires import requires
import m5

from gem5.components.boards.simple_board import SimpleBoard
from gem5.simulate.exit_event import ExitEvent
from gem5.simulate.simulator import Simulator
from gem5.utils.requires import requires
from gem5.components.memory import DualChannelDDR4_2400

from util.arguments_spec import *
from util.specbms import wlcfg

from util.simulation_utils import configure_cpu, configure_cache

requires(isa_required=isa_choices[args.isa])

# Memory: Dual Channel DDR4 2400 DRAM device.
memory = DualChannelDDR4_2400(size="3GiB")

processor = SimpleProcessor(
   cpu_type=cpu_types[args.cpu_type],
    isa=isa_choices[args.isa],
    num_cores=1,
)

cpu = processor.cores[-1].core

configure_cpu(cpu, args)

cpu.backComSize = 20
cpu.forwardComSize = 20
   
cache_hierarchy = configure_cache(args)   

board = SimpleBoard(
    clk_freq="3GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)


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
          #  m5.stats.dump()
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
