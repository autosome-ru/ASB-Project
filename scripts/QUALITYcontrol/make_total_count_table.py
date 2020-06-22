import pandas as pd
import os
import sys
import numpy as np

sys.path.insert(1, "/home/abramov/ASB-Project")
from scripts.HELPERS.helpers import states
from scripts.HELPERS.paths_for_components import parameters_path

df = pd.read_table(os.path.expanduser(os.path.join(parameters_path, 'unionSNPs.tsv')))
print('iread')
df.columns = ['chr', 'pos', 'cov', 'BAD', 'COSMIC'] + ['Q{:.2f}'.format(state) for state in states]
df = df[['BAD', 'COSMIC']]
df_counts = df.groupby(['BAD', 'COSMIC']).size().reset_index(name='counts')
df_counts = df_counts.groupby(['BAD', 'COSMIC'], as_index=False)['counts'].sum()
df_counts.to_csv(os.path.expanduser('~/PARAMETERS/counts/counts.tsv'), index=False, sep='\t')