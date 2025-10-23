import pandas as pd
import random
import os
import subprocess

CONFIG_JSON = "champsim_config.json"
CONFIG_HEADER = r"./branch/tage/tage_config.h"
OUTPUT_ROOT = r"outputs"
TRACE_FILE = r"xalancbmk_748B.trace.xz"

file_paths = [
    'D:\\term 4\\computer articture\\project\\NUMBER_OF_TABLE\\output.csv',
    'D:\\term 4\\computer articture\\project\\GEOMETRIC\\output.csv',
    'D:\\term 4\\computer articture\\project\\TABLE_SIZE\\output.csv',
    'D:\\term 4\\computer articture\\project\\TAG_SIZE\\output.csv',
]

list_dic = [{}, {}, {}, {}]

trace_value = '53B'  

params = {}

number_of_test = 30 

def write_config_header(params):
    content = f"""#ifndef TAGE_CONFIG_H
#define TAGE_CONFIG_H

class tage_config {{
public:
    static constexpr std::size_t NUMBER_OF_TABLES = {params['NUMBER_OF_TABLES']};
    static constexpr uint16_t LEAST_HISTORY_LENGTH = {params['LEAST_HISTORY_LENGTH']};
    static constexpr double COMMON_RATIO = {params['COMMON_RATIO']};

    static constexpr uint8_t TAG_SIZE_MAX = {params['TAG_SIZE_MAX']};
    static constexpr uint8_t TAG_SIZE_MIN = {params['TAG_SIZE_MIN']};

    static constexpr uint8_t MAX_TABLE_SIZE_LOG = {params['MAX_TABLE_SIZE_LOG']};
    static constexpr uint8_t MIN_TABLE_SIZE_LOG = {params['MIN_TABLE_SIZE_LOG']};

    enum class TableSizePattern {{
        CONSTANT,
        ASCENDING,
        DESCENDING,
        HILL_SHAPED
    }};

    static constexpr TableSizePattern ACTIVE_PATTERN = TableSizePattern::{params['ACTIVE_PATTERN']};
}};

#endif
"""
    with open(CONFIG_HEADER, "w") as f:
        f.write(content)


def run_command(cmd, cwd="."):
    print(f"Running: {' '.join(cmd)} in {cwd}")
    proc = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout = proc.stdout.decode()
    stderr = proc.stderr.decode()
    if proc.returncode != 0:
        print(f"Error running {' '.join(cmd)}:\n{stderr}")
        return False, stdout, stderr
    return True, stdout, stderr

def run_test(params, test_id):
    print(f"\n=== Running test {test_id} with params: {params} ===")
    write_config_header(params)

    success, out, err = run_command(["./config.sh", CONFIG_JSON])
    if not success:
        return False, out, err

    success, out, err = run_command(["make"])
    if not success:
        return False, out, err

    champsim_bin = "bin/champsim"
    cmd = [
        champsim_bin,
        "--warmup-instructions", "10000000",
        "--simulation-instructions", "40000000",
        TRACE_FILE
    ]
    success, out, err = run_command(cmd)
    if not success:
        return False, out, err

    output_folder = os.path.join(OUTPUT_ROOT, f"test_{test_id}")
    os.makedirs(output_folder, exist_ok=True)

    with open(os.path.join(output_folder, "output.log"), "w") as f:
        f.write(out)
    with open(os.path.join(output_folder, "error.log"), "w") as f:
        f.write(err)
    with open(os.path.join(output_folder, "params.txt"), "w") as f:
        for k,v in params.items():
            f.write(f"{k} = {v}\n")

    return True, out, err





for i in range(4):
    df = pd.read_csv(file_paths[i])
    
    if i == 0:
        for _, row in df.iterrows():
         if row['Trace'] == trace_value:
            key = (row['NUMBER_OF_TABLES'],) 
            probability = row['probability']
            list_dic[i][key] = probability
            
    elif i == 1:
        for _, row in df.iterrows():
         if row['Trace'] == trace_value:
            key = (row['COMMON_RATIO'], row['LEAST_HISTORY_LENGTH'])
            probability = row['probability']
            list_dic[i][key] = probability
            
    elif i == 2:
        for _, row in df.iterrows():
         if row['Trace'] == trace_value:
            key = (row['ACTIVE_PATTERN'], row['MAX_TABLE_SIZE_LOG'], row['MIN_TABLE_SIZE_LOG'])
            probability = row['probability']
            list_dic[i][key] = probability
            
    else:
        for _, row in df.iterrows():
         if row['Trace'] == trace_value:
            key = (row['TAG_SIZE_MAX'], row['TAG_SIZE_MIN'])  
            probability = row['probability']
            list_dic[i][key] = probability


item_NUMBER_OF_TABLE  = list(list_dic[0].keys())
wight_NUMBER_OF_TABLE = list(list_dic[0].values())
params["NUMBER_OF_TABLES"] = random.choices(item_NUMBER_OF_TABLE, weights=wight_NUMBER_OF_TABLE, k=1)[0][0]



item_GEOMETRIC = list(list_dic[1].keys())
wight_GEOMETRIC = list(list_dic[1].values())
params["COMMON_RATIO"],params["LEAST_HISTORY_LENGTH"]  = random.choices(item_GEOMETRIC, weights=wight_GEOMETRIC, k=1)[0]

item_TABLE_SIZE = list(list_dic[2].keys())
wight_TABLE_SIZE = list(list_dic[2].values())
params["ACTIVE_PATTERN"],params["MAX_TABLE_SIZE_LOG"] , params["MIN_TABLE_SIZE_LOG"]  = random.choices(item_TABLE_SIZE, weights=wight_TABLE_SIZE, k=1)[0]


item_TAG_SIZE = list(list_dic[3].keys())
wight_TAG_SIZE = list(list_dic[3].values())
params["TAG_SIZE_MAX"],params["TAG_SIZE_MIN"]   = random.choices(item_TAG_SIZE, weights=wight_TAG_SIZE, k=1)[0]

print(params)


# for i in range(number_of_test) : 
#     success, _, _ = run_test(params, i)
#     if not success:
#         print(f"Test {i} failed.")