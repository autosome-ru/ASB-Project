import sys
import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

stats = pd.read_table(os.path.expanduser('~/pvalue_bias_statistics_BAD=1.0.tsv'))
print(stats)

fig, ax = plt.subplots(figsize=(10, 8))
x = np.array(range(1, 18))

palts = stats[stats['alt_p'] != 1.0]
sns.barplot(x=x, y=[palts[palts['alt_p'] <= 1/10**k]['counts'].sum() for k in x], label='alt', ax=ax, color='C1')

prefs = stats[stats['ref_p'] != 1.0]
sns.barplot(x=x, y=[prefs[prefs['ref_p'] <= 1/10**k]['counts'].sum() for k in x], label='ref', ax=ax, color='C0')




plt.grid(True)
plt.legend()
plt.title('ref-alt p_value on BAD=1')
plt.xlabel('x: -log10 p_value >= x')
plt.ylabel('snp count')
plt.savefig(os.path.expanduser('~/fixed_alt/p_dist.png'))
plt.show()