import argparse
import os
import glob
import subprocess

from typing import Optional

import polars as pl


def parse_stats_file(file_path) -> Optional[pl.DataFrame]:
    """
    Parse a stats.txt file and return a polars DataFrame.
    """
    num_rows = 0
    all: list[pl.DataFrame] = []
    current: dict[str, str] = {}
    in_block = False

    with open(file_path, 'r') as f:
        for line in f:
            if '---------- Begin Simulation Statistics' in line:
                current = {}
                in_block = True
            elif '---------- End Simulation Statistics' in line:
                in_block = False
                if current:
                    all.append(pl.DataFrame(current))
                    num_rows += 1
            elif in_block:
                parts = line.split()
                if len(parts) < 2:
                    continue
                key = parts[0]
                if '\0' in key or "distribution" in line or "Distribution" in line:
                    continue
                current[key] = parts[1]

    if num_rows == 0:
        return None
    
    return pl.concat(all, how='diagonal')


def main():
    # Determine the system architecture once
    default_arch = subprocess.check_output(['dpkg', '--print-architecture']).decode().strip()

    parser = argparse.ArgumentParser(prog='Collector')
    parser.add_argument('--arch', type=str, default=default_arch, help='Architecture name')
    parser.add_argument('experiments', nargs='+', help='Name of experiments')
    args = parser.parse_args()
    
    stuff: list[pl.DataFrame] = []

    for experiment in args.experiments:
        pattern = os.path.join('..', 'results', args.arch, experiment, '*', 'stats.txt')
        for stats_file in glob.glob(pattern):
            benchmark = os.path.basename(os.path.dirname(stats_file))
            exp_df = parse_stats_file(stats_file)

            if exp_df is None:
                print(f"No data found in {stats_file}")
                continue

            exp_name = f"{args.arch}_{experiment}"

            print(f"\nProcessing Experiment {exp_name} Benchmark {benchmark}\n")

            exp_df = exp_df.with_columns(
                pl.lit(exp_name).alias('experiment'),
                pl.lit(benchmark).alias('benchmark')
            )

            stuff.append(exp_df)
            

    # Write to CSV
    result = pl.concat(stuff, how='diagonal')
    
    result.write_csv('results.csv')


if __name__ == '__main__':
    main()
