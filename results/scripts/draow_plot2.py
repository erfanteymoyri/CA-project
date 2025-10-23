import pandas as pd
import matplotlib.pyplot as plt

csv_path = './TABLE_SIZE/output.csv'  

df = pd.read_csv(csv_path)

df['x_label'] = df['ACTIVE_PATTERN'].astype(str) + '_' + df['MAX_TABLE_SIZE_LOG'].astype(str) + '_' + df['MIN_TABLE_SIZE_LOG'].astype(str)

trace_names = df['Trace'].unique()

plt.figure(figsize=(12, 6))

for trace in trace_names:
    sub_df = df[df['Trace'] == trace]
    plt.plot(sub_df['x_label'], sub_df['Accuracy'], marker='o', label=f"Trace: {trace}")

plt.xlabel('ACTIVE_PATTERN + MAX_TABLE_SIZE_LOG + MIN_TABLE_SIZE_LOG')
plt.ylabel('Accuracy')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
