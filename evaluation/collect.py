import argparse
import os
import glob
import subprocess

import pandas as pd

SIMPOINT_BASE = "/share/david/spec/arm64/simpoints_200M/"

def parse_stats_file(file_path) -> dict[str, list[str]]:
    with open(file_path, 'r') as f:
        lines: list[str] = f.readlines()
    
    blocks: list[list[str]] = []
    block: list[str] = []
    in_block = False
    for line in lines:
        if '---------- Begin Simulation Statistics' in line:
            block = []
            in_block = True
        elif '---------- End Simulation Statistics' in line:
            in_block = False
            blocks.append(block)
        elif in_block:
            block.append(line)
    
    # First pass: collect all unique keys
    all_keys = set()
    for block in blocks:
        for line in block:
            chunks = line.split()
            if len(chunks) < 2:
                continue
            key = chunks[0]
            if '\0' in key:
                continue
            all_keys.add(key)
    
    # Second pass: collect values for each key per block
    datapoints: dict[str, list[str]] = {key: [] for key in all_keys}
    for block in blocks:
        block_dict = {}
        for line in block:
            chunks = line.split()
            if len(chunks) < 2:
                continue
            key = chunks[0]
            if '\0' in key:
                continue
            value = chunks[1]
            block_dict[key] = value
        for key in all_keys:
            datapoints[key].append(block_dict.get(key, ''))
    return datapoints
 
def parse_simpoint_files(filepath_simpt, filepath_weight, benchmark_name = None) -> None:
    with open(filepath_simpt, 'r') as f:
        simpoint_lines = f.readlines()
    with open(filepath_weight, 'r') as f:
        weight_lines = f.readlines()

    simpts = []
    weights = []
    for idx, line in enumerate(simpoint_lines): 
        simpt_chunks = line.split()
        weight_chunks = weight_lines[idx].split()
        simpts.append(simpt_chunks[0])
        weights.append(weight_chunks[0])

    if benchmark_name:
        print(f"Benchmark: {benchmark_name}")
        print(f"Simpts: {simpts}")
        print(f"Weights: {weights}")

    # get idx of smallest simpoint in simpts
    sid_weights = []
    for i in range(len(simpts)):
        min_idx = simpts.index(min(simpts, key=float))
        sid_weights.append(weights[min_idx])
        # remove the smallest simpoint from simpts and weights
        simpts.pop(min_idx)
        weights.pop(min_idx)

    return sid_weights




def main():
    our_arch = str.replace(subprocess.check_output(['dpkg', '--print-architecture']).decode("utf-8"), '\n', '') 
    
    parser = argparse.ArgumentParser(prog='Collector')
    parser.add_argument('--arch', type=str, default=our_arch, help='Architecture name')
    parser.add_argument('--set', type=str, default='', help='name of the experiment set')
    parser.add_argument('experiments', nargs="+", help='Name of experiments')
    parser.add_argument('--spec', action="store_true", default=False)
    parser.add_argument('--debug', action="store_true", default=False)

    args = parser.parse_args()

    map_spec = None

    if args.spec:
        print("Collecting SimPoints files...")
        map_spec = {}
        simpts =  glob.glob(f'{SIMPOINT_BASE}/*/results.simpts')
        weights = glob.glob(f'{SIMPOINT_BASE}/*/results.weights')
        for simpt in simpts:
            benchmark_name = os.path.basename(os.path.dirname(simpt))
            # get the weight file of the same benchmark with exact name
            weight_file = next((w for w in weights if os.path.basename(os.path.dirname(w)) == benchmark_name), None)
            if not weight_file:
                print(f"No weight file found for {benchmark_name}")
                continue
            sid_weights = parse_simpoint_files(simpt, weight_file)
            map_spec[benchmark_name] = sid_weights
        if args.debug:
            print("SimPoints mapping:")
            for k, v in map_spec.items():
                print(f"Benchmark: {k}")
                for i, sid in enumerate(v):
                    print(f"  sid {i}: {sid}")
            return
        

    result: pd.DataFrame = pd.DataFrame()

    for experiment in args.experiments:
        if args.spec:
            benchmarks = glob.glob(f'../results/{args.arch}/{args.set}/{experiment}/*/*/stats.txt')
        else:    
            benchmarks = glob.glob(f'../results/{args.arch}/{args.set}/{experiment}/*/stats.txt')

        for benchmark in benchmarks:
            # The benchmark name is assumed to be the immediate subdirectory name.
            if args.spec:
                benchmark_name = os.path.basename(os.path.dirname(os.path.dirname(benchmark)))
                sid_number =  os.path.basename(os.path.dirname(benchmark)).replace('sid', '')
                if sid_number.isdigit():
                    sid_number = int(sid_number)
                else:
                    print(f"Invalid sid number in path: {benchmark}")
                    continue
                if benchmark_name in map_spec:
                    sid_weights = map_spec[benchmark_name]
                    data = parse_stats_file(benchmark)
                else:
                    print(f"No simpoint weights found for {benchmark_name}, skipping...")
                    continue
            else:
                benchmark_name = os.path.basename(os.path.dirname(benchmark))
                data = parse_stats_file(benchmark)

            if not data:
                print(f"No data found in {benchmark}")
                continue
            
            experiment_name = f"{args.arch}_{experiment}"

            df = pd.DataFrame({k:pd.Series(v) for k,v in data.items()})

            print(f"\nData for Experiment {experiment_name} Benchmark {benchmark_name}:\n {df}\n")
            df = df.assign(experiment=experiment_name, benchmark=benchmark_name)
            if args.spec:
                df['sid_number'] = sid_number
                df['sid_weight'] = sid_weights[sid_number]
            result = pd.concat([result, df], ignore_index=True)
    

    # group by experiment and benchmark, and aggregate the data scaled by sid_weight is spec is True
    # example of aggregation: sum of all values in the group multiplied by sid_weight
    #  ipc   sid_weight
    #  1.2   0.5
    #  1.4   0.5
    # result 
    # ipc
    # 1.3 
    if args.spec:
        #save before aggregation
        result.to_csv(f'{args.set}_raw_results.csv' if args.set != '' else f'raw_results.csv', index=False)

        def weighted_sum(group):
            agg_columns = [k for k in group.columns if k not in ['experiment', 'benchmark', 'sid_weight', 'sid_number']]
            out = {}
            for col in agg_columns:
                # Multiply each value by its corresponding sid_weight, then sum
                out[col] = (group[col].astype(float) * group['sid_weight'].astype(float)).sum()
            out['experiment'] = group['experiment'].iloc[0]
            out['benchmark'] = group['benchmark'].iloc[0]
            return pd.Series(out)

        result = result.groupby(['experiment', 'benchmark']).apply(weighted_sum).reset_index(drop=True)
        # remove sid_weight column
        result = result.drop(columns=['sid_weight', 'sid_number'], errors='ignore')            

    # Save the result to a CSV file
    result.to_csv(f'{args.set}_results.csv' if args.set != '' else f'results.csv', index=False)



if __name__ == '__main__':
    main()