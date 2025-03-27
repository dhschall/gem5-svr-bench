import argparse
import os
import glob
import re
import matplotlib.pyplot as plt
import pandas as pd

def main():
    parser = argparse.ArgumentParser(prog='Plotter')
    parser.add_argument('-e', '--experiments', nargs="+", help='Experiments to process')
    parser.add_argument('-b', '--benchmarks', nargs="+", help='Benchmarks to process')
    args = parser.parse_args()

    if not args.experiments or not args.benchmarks:
        print("Please provide at least one experiment and one benchmark to process.")
        return

    # Find all folders in the collected directory.
    experiments = glob.glob('collected/*')
    
    benchmarks_data: list[pd.DataFrame] = []
    for experiment in experiments:
        experiment_name = os.path.basename(experiment)
        if experiment_name not in args.experiments:
            continue
        print(f"Selecting Experiment '{experiment}'")

        benchmarks = glob.glob(f'{experiment}/*.csv')
        
        for benchmark in benchmarks:
            benchmark_name = os.path.basename(benchmark).replace('.csv', '')
            if benchmark_name not in args.benchmarks:
                continue
            data = pd.read_csv(benchmark)
            
            print(f"\nData for Experiment {experiment_name} Benchmark {benchmark_name}:")
            print(data)
            print("----------------\n")
            data = data.assign(experiment=experiment_name, benchmark=benchmark_name)
            benchmarks_data.append(data)
    
    result = pd.concat(benchmarks_data)
    
    result.to_csv('results.csv', index=False)

if __name__ == '__main__':
    main()
