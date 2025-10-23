import os
import re
import csv

# Root directory containing all test_i folders
root_dir = r'./output_with_change_random_param/perl135B_tests/random_tests'
# Output CSV file
output_csv = './output_with_change_random_param/perl135B_tests/output.csv'

# Prepare list to hold all results
all_results = []

# Loop through test_0 to test_29
for i in range(30):
    print(os.getcwd())
    test_dir = os.path.join(root_dir, f'test_{i}')
    params_path = os.path.join(test_dir, 'params.txt')
    output_log_path = os.path.join(test_dir, 'output.log')
    if not os.path.isfile(params_path) or not os.path.isfile(output_log_path):
        print(f"Skipping {test_dir}, missing files.")
        continue

    # Parse params.txt
    params = {}
    with open(params_path, 'r') as f:
        for line in f:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                params[key.strip()] = value.strip()
    
    # Parse output.log to find accuracy line
    accuracy = None
    with open(output_log_path, 'r') as f:
        for line in f:
            match = re.search(r'Branch Prediction Accuracy:\s*([\d.]+)%', line)
            if match:
                accuracy = float(match.group(1))
                break
    
    if accuracy is None:
        print(f"Accuracy not found in {output_log_path}")
        continue

    # Add accuracy to params dict
    params['Accuracy'] = accuracy
    # Also add test index
    params['Test_ID'] = f'test_{i}'
    all_results.append(params)

# Determine CSV column names (sorted for consistency, Accuracy and Test_ID last)
all_keys = sorted(k for k in all_results[0].keys() if k not in ['Accuracy', 'Test_ID'])
fieldnames = all_keys + ['Accuracy', 'Test_ID']

# Write to CSV
with open(output_csv, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in all_results:
        writer.writerow(row)

print(f"Results written to {output_csv}")
