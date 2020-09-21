import sys
import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt, ticker
import seaborn as sns

sys.path.insert(1, "/home/abramov/ASB-Project")
from scripts.HELPERS.helpers import states

sns.set(font_scale=1.4, style="ticks", font="lato")
sns.set_palette((
'#56B4E9',
'#0072B2',
'#009E73',
'#E69F00',
'#F0E442',
'#D55E00',
'#999999',
'#505050',
'#CC79A7'))
# sns.set_palette('Set1', desat=0.9, n_colors=9)
# '#e41a1c',
# '#377eb8',
# '#4daf4a',
# '#984ea3',
# '#ff7f00',
# '#999999',
# '#a65628',
# '#f781bf',
# '#ffff33'))

# sns.set(font_scale=1.4, style="ticks", font="lato", palette=(
# "#f15854", "#faa43a", "#e5d00d", "#60bd68", "#5da5da", "#f17cb0", "#975597", "#b2912f", "#aaaaaa", "#4d4d4d"))
# sns.set(palette=('#fcfbfd', '#efedf5', '#dadaeb', '#bcbddc', '#9e9ac8', '#807dba', '#6a51a3', '#54278f', '#3f007d'))
# sns.set(palette=(
# "#f15854", "#faa43a", "#e5d00d", "#60bd68", "#5da5da", "#f17cb0", "#975597", "#b2912f", "#aaaaaa", "#4d4d4d"))
sns.set_style({"xtick.direction": "in", "ytick.direction": "in"})
plt.rcParams['font.weight'] = "medium"
plt.rcParams['axes.labelweight'] = 'medium'
plt.rcParams['figure.titleweight'] = 'medium'
plt.rcParams['axes.titleweight'] = 'medium'
plt.rcParams['figure.figsize'] = 6, 5
plt.rcParams["legend.framealpha"] = 1
plt.rcParams['axes.xmargin'] = 0
plt.rcParams['axes.ymargin'] = 0
plt.rcParams["legend.framealpha"] = 0.4

t = {}
min_tr = {}
max_tr = {}
for BAD in states:
    t[BAD] = pd.read_table(os.path.expanduser('~/DataForFigures/counts_deltaqm_{:.2f}.tsv'.format(BAD)))
    t[BAD].replace(1.3333333333333337, 4 / 3, inplace=True)
    min_tr[BAD] = t[BAD]['threshold'].min()
    max_tr[BAD] = t[BAD]['threshold'].max()
# for x in t['COSMIC'].unique():
#     print(x, t[t['COSMIC'] == x]['counts'].sum())

# x = [x for x in range(101)] + [x for x in range(110, 201, 10)]

TP = {}
FP = {}
Precision = {}  # TP / (TP + FP)
Recall = {}  # TPR = TP / P
FPR = {}  # FP / N
for BAD in states:
    TP[BAD] = {}
    FP[BAD] = {}
    Precision[BAD] = {}
    Recall[BAD] = {}
    FPR[BAD] = {}

# All = {}
# Global_precision = {}

for BAD in states:
    t[BAD] = t[BAD][t[BAD]['BAD'].isin(states) & t[BAD]['COSMIC'].isin(states)]
l = len(states)

P = {}
N = {}
for BAD in states:
    P[BAD] = t[BAD][(t[BAD]['COSMIC'] == BAD) & (t[BAD]['threshold'] == min_tr[BAD])]['counts'].sum()
    N[BAD] = t[BAD][(t[BAD]['COSMIC'] != BAD) & (t[BAD]['threshold'] == min_tr[BAD])]['counts'].sum()
ALL = sum(P[BAD] for BAD in states)

x = {}
s = {}

for BAD in states:
    x[BAD] = sorted(list(t[BAD]['threshold'].unique()))
    for tr in x[BAD]:
        s[BAD] = t[BAD][t[BAD]['threshold'] == tr].copy()
        # print(tr, BAD)
        TP[BAD][tr] = s[BAD][(s[BAD]['COSMIC'] == BAD) & (s[BAD]['BAD'] == BAD)]['counts'].sum()
        FP[BAD][tr] = s[BAD][(s[BAD]['COSMIC'] != BAD) & (s[BAD]['BAD'] == BAD)]['counts'].sum()
        Precision[BAD][tr] = TP[BAD][tr] / (TP[BAD][tr] + FP[BAD][tr])
        Recall[BAD][tr] = TP[BAD][tr] / P[BAD]
        FPR[BAD][tr] = FP[BAD][tr] / N[BAD]
    # All[tr] = s['counts'].sum()
    # Global_precision[tr] = s[s['BAD'] == s['COSMIC']]['counts'].sum() / All[tr]

# s[((s['COSMIC'] == BAD) & (s['BAD'] == BAD)) | ((s['COSMIC'] != BAD) & (s['BAD'] != BAD))]['counts'].sum() / All)

# P[tr] R[tr]
for metric, label in (Precision, 'Precision'), (Recall, 'Recall'):
    fig, ax = plt.subplots()
    for BAD in states:
        plt.plot([tr for tr in x[BAD] if 100 >= tr >= -100], [metric[BAD][tr] for tr in x[BAD] if 100 >= tr >= -100],
                 label='{:.2f}'.format(BAD))
    # plt.plot(x, [Global_precision[tr] for tr in x], label='All', color='black')
    # ax.axhline(y=((l - 1) ** 2 + 1) / ((l - 1) ** 2 + 1 + 2 * (l - 1)), color='black', linestyle='--')
    if label == 'Precision':
        ax.axhline(y=1 / l, color='black', linestyle='--')
    ax.axvline(x=0, color='black', linestyle='--')

    ax.legend(loc='lower right')
    ax.grid(True)
    ax.set_ylim(0, 1)
    ax.set_xlabel('SNP qual >= x')
    ax.set_ylabel(label)

    plt.savefig(os.path.expanduser('~/AC_5/AS_Figure_5_{}.png'.format(label)), dpi=300)
    plt.close(fig)

actual_seg_tr = dict(zip(states, [min(x for x in Recall[BAD].keys() if x >= 0) for BAD in states]))

# PR-curve
fig, ax = plt.subplots()
for i, BAD in enumerate(states):
    x_list, y_list = zip(*sorted(zip([Recall[BAD][tr] for tr in x[BAD]], [Precision[BAD][tr] for tr in x[BAD]]),
                                 key=lambda z: z[0]))
    AUC = np.trapz(x=x_list, y=y_list)
    # print('AUPRC for {:.2f}: {:.3f}'.format(BAD, AUC))
    print('Prec. {:.3f}, Rec. {:.3f} for {:.2f}'.format(Precision[BAD][0], Recall[BAD][0], BAD))
    ax.plot(x_list, y_list, label='{:.2f}'.format(BAD))
    ax.scatter([Recall[BAD][actual_seg_tr[BAD]]], [Precision[BAD][actual_seg_tr[BAD]]],
               s=50, zorder=10, alpha=0.7, lw=0)
ax.grid(True)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_xlabel('Recall')
ax.set_ylabel('Precision')
ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])

# Shrink current axis by 20%
box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

# Put a legend to the right of the current axis
legend = ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), title='BAD', frameon=True, fancybox=False,
                   labels=['1', '4/3', '3/2', '2', '5/2', '3', '4', '5', '6'])
legend.get_frame().set_edgecolor('black')

# for i, BAD in enumerate(states):
#     ax.axhline(y=P[BAD] / ALL * 1 / l, color='C'+str(i), linestyle='--', label=None, lw=1)

plt.savefig(os.path.expanduser('~/AC_5/Figure_AS_5_PR.png'), dpi=300)
plt.savefig(os.path.expanduser('~/AC_5/Figure_AS_5_PR.svg'), dpi=300)
plt.close(fig)

# ROC
fig, ax = plt.subplots()
for BAD in states:
    x_list, y_list = zip(*sorted(zip([FPR[BAD][tr] for tr in x[BAD]], [Recall[BAD][tr] for tr in x[BAD]]),
                                 key=lambda z: z[0]))
    AUC = np.trapz(x=x_list, y=y_list)
    print('AUROC for {:.2f}: {:.3f}'.format(BAD, AUC))
    ax.plot(x_list, y_list, label='{:.2f}'.format(BAD))
    ax.scatter([FPR[BAD][actual_seg_tr[BAD]]], [Recall[BAD][actual_seg_tr[BAD]]],
               s=50, zorder=10, alpha=0.7, lw=0)
ax.plot([0, 1], [0, 1], color='black', linestyle='--')
ax.grid(True)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_xlabel('FPR')
ax.set_ylabel('TPR')
ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])

# Shrink current axis by 20%
box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

# Put a legend to the right of the current axis
legend = ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), title='BAD', frameon=True, fancybox=False,
                   labels=['1', '4/3', '3/2', '2', '5/2', '3', '4', '5', '6'])
legend.get_frame().set_edgecolor('black')

plt.savefig(os.path.expanduser('~/AC_5/Figure_AS_5_ROC.png'), dpi=300)
plt.savefig(os.path.expanduser('~/AC_5/Figure_AS_5_ROC.svg'), dpi=300)

# plt.show()
plt.close(fig)