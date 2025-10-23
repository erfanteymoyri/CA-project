import pandas as pd
import matplotlib.pyplot as plt

csv_path = './NUMBER_OF_TABLE/output.csv'  

df = pd.read_csv(csv_path)


trace_names = df['Trace'].unique()

plt.figure(figsize=(12, 6))

for trace in trace_names:
    sub_df = df[df['Trace'] == trace]
    plt.plot(sub_df['NUMBER_OF_TABLES'], sub_df['Accuracy'], marker='o', label=f"Trace: {trace}")

plt.xlabel('NUMBER_OF_TABLES')
plt.ylabel('Accuracy')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
