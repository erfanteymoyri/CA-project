import os
import subprocess

# مسیرهای پروژه و فایل‌ها (لطفا خودتان تنظیم کنید)
CHAMPSIM_ROOT = "/path/to/champsim"
CONFIG_JSON = "chamsim_configuration.json"
CONFIG_HEADER = os.path.join(CHAMPSIM_ROOT, "src", "branch_predictor", "tage_config.h")
OUTPUT_ROOT = "/path/to/output"
TRACE_FILE = "/path/to/traces/600.perlbench_s-210B.champsimtrace.xz"

# پارامترها برای تست
number_of_tables_list = [8, 10, 12, 14]
least_history_lengths = [1.5, 1.6, 1.7]
common_ratios = [4, 5]
tag_size_max_list = [10, 12]
tag_size_min_list = [6, 8]
active_patterns = ["CONSTANT", "ASCENDING", "DESCENDING", "HILL_SHAPED"]
max_table_size_logs = [11, 12]
min_table_size_logs = [9, 10]

def write_config_header(params):
    content = f"""#ifndef BRANCH_TAGE_CONFIG_H
#define BRANCH_TAGE_CONFIG_H

static constexpr std::size_t NUMBER_OF_TABLES = {params['NUMBER_OF_TABLES']};
static constexpr double LEAST_HISTORY_LENGTH = {params['LEAST_HISTORY_LENGTH']};
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

constexpr TableSizePattern ACTIVE_PATTERN = TableSizePattern::{params['ACTIVE_PATTERN']};

#endif
"""
    with open(CONFIG_HEADER, "w") as f:
        f.write(content)

def run_command(cmd, cwd=None):
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

    success, out, err = run_command(["./config.sh", CONFIG_JSON], cwd=CHAMPSIM_ROOT)
    if not success:
        return False, out, err

    success, out, err = run_command(["make", "clean"], cwd=CHAMPSIM_ROOT)
    if not success:
        return False, out, err

    success, out, err = run_command(["make"], cwd=CHAMPSIM_ROOT)
    if not success:
        return False, out, err

    champsim_bin = os.path.join(CHAMPSIM_ROOT, "bin", "champsim")
    cmd = [
        champsim_bin,
        "--warmup-instructions", "200000000",
        "--simulation-instructions", "500000000",
        TRACE_FILE
    ]
    success, out, err = run_command(cmd, cwd=CHAMPSIM_ROOT)
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

def main():
    test_id = 0
    # مقدار ثابت اولیه
    fixed_params = {
        "NUMBER_OF_TABLES": 12,
        "LEAST_HISTORY_LENGTH": 1.5,
        "COMMON_RATIO": 4,
        "TAG_SIZE_MAX": 10,
        "TAG_SIZE_MIN": 6,
        "MAX_TABLE_SIZE_LOG": 11,
        "MIN_TABLE_SIZE_LOG": 9,
        "ACTIVE_PATTERN": "CONSTANT",
    }

    # 1. تغییر NUMBER_OF_TABLES
    for val in number_of_tables_list:
        params = fixed_params.copy()
        params["NUMBER_OF_TABLES"] = val
        success, _, _ = run_test(params, test_id)
        if not success:
            print(f"Test {test_id} failed.")
        test_id += 1

    # 2. تغییر LEAST_HISTORY_LENGTH و COMMON_RATIO با هم (6 حالت)
    for lh in least_history_lengths:
        for cr in common_ratios:
            params = fixed_params.copy()
            params["LEAST_HISTORY_LENGTH"] = lh
            params["COMMON_RATIO"] = cr
            success, _, _ = run_test(params, test_id)
            if not success:
                print(f"Test {test_id} failed.")
            test_id += 1

    # 3. تغییر TAG_SIZE_MAX و TAG_SIZE_MIN (4 حالت)
    for max_tag in tag_size_max_list:
        for min_tag in tag_size_min_list:
            params = fixed_params.copy()
            params["TAG_SIZE_MAX"] = max_tag
            params["TAG_SIZE_MIN"] = min_tag
            success, _, _ = run_test(params, test_id)
            if not success:
                print(f"Test {test_id} failed.")
            test_id += 1

    # 4. تغییر ACTIVE_PATTERN و MAX_TABLE_SIZE_LOG و MIN_TABLE_SIZE_LOG (16 حالت)
    for pattern in active_patterns:
        for max_log in max_table_size_logs:
            for min_log in min_table_size_logs:
                params = fixed_params.copy()
                params["ACTIVE_PATTERN"] = pattern
                params["MAX_TABLE_SIZE_LOG"] = max_log
                params["MIN_TABLE_SIZE_LOG"] = min_log
                success, _, _ = run_test(params, test_id)
                if not success:
                    print(f"Test {test_id} failed.")
                test_id += 1

if __name__ == "__main__":
    main()
