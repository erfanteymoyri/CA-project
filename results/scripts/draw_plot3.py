import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('./output_for_other_predictor/xalan_tests/output.csv')

plt.figure(figsize=(8, 5))
plt.bar(df['PREDICTOR'], df['ACCURACY'], width=0.4, color='skyblue', edgecolor='black')

plt.xlabel('PREDICTOR')
plt.ylabel('ACCURACY')
plt.title('Accuracy Comparison predictor(xalan)')
plt.ylim(df['ACCURACY'].min() - 1, df['ACCURACY'].max() + 1)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()

# ذخیره به عنوان فایل تصویری
plt.savefig('./output_for_other_predictor/xalan_tests/plot_output.png', dpi=300)

# اگر نمایش لازم نیست:
plt.show()
plt.close()
