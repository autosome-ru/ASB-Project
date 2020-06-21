import os
import sys
import pandas as pd

dirname = sys.argv[1]
ids_set = set()
for filename in os.listdir(dirname):
    print(filename)
    df = pd.read_table(os.path.join(dirname, filename))
    df = df[(df['fdrp_bh_ref'] <= 0.05) | (df['fdrp_bh_alt'] <= 0.05)]
    ids_set |= set(df['ID'])

print(len(ids_set))