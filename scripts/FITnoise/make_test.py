import sys
import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from scipy import stats as st

filename = os.path.expanduser('~/CTCF_HUMAN_SNP_table.tsv'.format(BAD))
stats = pd.read_table(filename)