import os
import sys
import numpy as np
import re

stats = {
    r".+cores1.+\.commitStats0\.numInsts .+ (\d+) .+" : "insts",
    r".+\.branchPred\.btb\.mispredict::total .+ (\d+) .+" : "BTB_mispredict",
    r".+\.branchPred\.mispredicted_0::total .+ (\d+) .+" : "BPU_mispredict",
    r".+\.branchPred\.mispredicted_0::DirectCond .+ (\d+) .+" : "BPU_cond_mispredict",
    r".+\.branchPred\.btb\.mispredict::DirectCond .+ (\d+) .+" : "BTB_cond_mispredict",
}
#     "board.processor.cores1.core.commitStats0.numInsts " : "insts",
#     "board.processor.cores1.core.branchPred.BTB.mispredict::total " : "BTB_mispredict",
#     "board.processor.cores1.core.branchPred.mispredicted_0::total " : "BPU_mispredict",
#     "board.processor.cores1.core.branchPred.mispredicted_0::DirectCond " : "BPU_cond_mispredict",
#     "board.processor.cores1.core.branchPred.BTB.mispredict::DirectCond " : "BTB_cond_mispredict",
# }

data = {kk : [] for kk in stats.values()}
if len(sys.argv) != 2:
    print("Usage: ./parse.py <output_file>")
    exit(1)
fn = sys.argv[1]



with open(fn) as f:
    for line in f:
        for key in stats:
            m = re.match(key, line)
            if m:
                # print(m)
                data[stats[key]].append(m.group(1))
                break

print(data)
# Convert data to numpy arrays with dtype=float
inst = np.array(data["insts"], dtype=float)
btb_m = np.array(data["BTB_mispredict"], dtype=float)
bpu_m = np.array(data["BPU_mispredict"], dtype=float)
bpu_cond_m = np.array(data["BPU_cond_mispredict"], dtype=float)
btb_cond_m = np.array(data["BTB_cond_mispredict"], dtype=float)

_min = min(len(inst), len(btb_m), len(bpu_m), len(bpu_cond_m), len(btb_cond_m))



print("BTB MPKI: ", (btb_m[:_min] / inst[:_min]) * 1000)
print("BPU MPKI: ", (bpu_m[:_min] / inst[:_min]) * 1000)
print("BP MPKI: ", ((bpu_cond_m[:_min] - btb_cond_m[:_min]) / inst[:_min]) * 1000)