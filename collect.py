import argparse
import os
import glob
import re

def parse_stats_file(file_path) -> dict[str, list[str]]:
    with open(file_path, 'r') as f:
        lines: list[str] = f.readlines()
    
    datapoints: dict[str, list[str]] = {}
    
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
    
    for block in blocks:
        for line in block:
            chunks = line.split()
            if len(chunks) < 2:
                continue                
            key = chunks[0]
            if key not in datapoints:
                datapoints[key] = []
            value = chunks[1]
            datapoints[key].append(value)
    return datapoints
            


def main():
    # Find all stats.txt files in the expected directory structure.
    stats_files = glob.glob('results/test/*/stats.txt')
    
    parser = argparse.ArgumentParser(prog='Collector')
    parser.add_argument('folder', type=str, help='Output folder')
    args = parser.parse_args()
    
    base_path, _ = os.path.split(os.path.abspath(__file__))
    base_path = os.path.join(base_path, 'collected')
    output_folder = os.path.join(base_path, args.folder)
    os.makedirs(output_folder, exist_ok=True)


    for file in stats_files:
        # The benchmark name is assumed to be the immediate subdirectory name.
        benchmark_name = os.path.basename(os.path.dirname(file))
        data = parse_stats_file(file)
        if data:
            with open(os.path.join(output_folder, f"{benchmark_name}.csv"), 'w') as f:
                header = ','.join(data.keys())
                f.write(f'{header}\n')
                buffer = []
                max_row = max(map(len, data.values())) - 1
                row = 0
                while row < max_row:
                    for col in data.values():
                        val = col[row] if row < len(col) else ""     
                        buffer.append(val)
                    out = ','.join(buffer)        
                    f.write(f'{out}\n')
                    buffer = []
                    row += 1

if __name__ == '__main__':
    main()
