import os
import numpy as np
import pandas as pd
from scripts.HELPERS.paths_for_components import results_path
from scripts.HELPERS.paths import get_tf_sarus_path


def get_concordance(p_val_ref, p_val_alt, motif_fc, motif_pval_ref, motif_pval_alt):
    if not pd.isna(p_val_ref) and not pd.isna(p_val_alt):
        log_pv = np.log10(min(p_val_ref, p_val_alt)) * np.sign(p_val_alt - p_val_ref)
        if abs(log_pv) >= -np.log10(0.05) and motif_fc != 0:
            if max(motif_pval_ref, motif_pval_alt) >= -np.log10(0.0005):
                result = "Weak " if abs(motif_fc) < 2 else ""
                if motif_fc * log_pv > 0:
                    result += 'Concordant'
                elif motif_fc * log_pv < 0:
                    result += 'Discordant'
                return result
            else:
                return "No Hit"
    return None


def make_dict_from_data(tf_fasta_path, motif_length):
    # read sarus file and choose best hit
    dict_of_snps = {}
    if os.path.isfile(tf_fasta_path):
        motif_length = motif_length
        with open(tf_fasta_path, 'r') as sarus:
            allele = None
            current_snp_id = None
            for line in sarus:
                if line[0] == ">":
                    # choose best
                    allele = line[-4:-1]
                    current_snp_id = line[1:-5]
                    assert allele in ("ref", "alt")
                    if allele == "ref":
                        dict_of_snps[current_snp_id] = {"ref": [], "alt": []}
                else:
                    assert allele in ("ref", "alt")
                    line = line.strip('\n').split("\t")
                    dict_of_snps[current_snp_id][allele].append({
                        "p": float(line[0]),
                        "orientation": line[2],
                        "pos": int(line[1]) if line[2] == '-' else motif_length - 1 - int(line[1]),
                    })
    return dict_of_snps


def adjust_with_sarus(df_row, dict_of_snps):
    ID = "{};{}".format(df_row['ID'], df_row['alt'])
    if len(dict_of_snps) == 0:
        df_row['motif_log_pref'] = None
        df_row['motif_log_palt'] = None
        df_row['motif_fc'] = None
        df_row['motif_pos'] = None
        df_row['motif_orient'] = None
        df_row['motif_conc'] = None
    else:
        dict_of_snps[ID]['ref'] = sorted(dict_of_snps[ID]['ref'], key=lambda x: x['pos'])
        dict_of_snps[ID]['ref'] = sorted(dict_of_snps[ID]['ref'], key=lambda x: x['orientation'])
        dict_of_snps[ID]['alt'] = sorted(dict_of_snps[ID]['alt'], key=lambda x: x['pos'])
        dict_of_snps[ID]['alt'] = sorted(dict_of_snps[ID]['alt'], key=lambda x: x['orientation'])
        ref_best = max(enumerate(dict_of_snps[ID]['ref']), key=lambda x: x[1]['p'])
        alt_best = max(enumerate(dict_of_snps[ID]['alt']), key=lambda x: x[1]['p'])
        best_idx, _ = max((ref_best, alt_best), key=lambda x: x[1]['p'])

        if len(dict_of_snps[ID]['ref']) != len(dict_of_snps[ID]['alt']):
            raise AssertionError(ID, dict_of_snps[ID]['ref'], dict_of_snps[ID]['alt'])
        assert dict_of_snps[ID]['ref'][best_idx]['pos'] == dict_of_snps[ID]['alt'][best_idx]['pos']
        df_row['motif_log_pref'] = dict_of_snps[ID]['ref'][best_idx]['p']
        df_row['motif_log_palt'] = dict_of_snps[ID]['alt'][best_idx]['p']
        df_row['motif_fc'] = (df_row['motif_log_palt'] - df_row['motif_log_pref']) / np.log10(2)
        df_row['motif_pos'] = dict_of_snps[ID]['ref'][best_idx]['pos']
        df_row['motif_orient'] = dict_of_snps[ID]['ref'][best_idx]['orientation']
        df_row['motif_conc'] = get_concordance(df_row['fdrp_bh_ref'],
                                               df_row['fdrp_bh_alt'],
                                               df_row['motif_fc'],
                                               df_row['motif_log_pref'],
                                               df_row['motif_log_palt'])
    return df_row


def main(tf_name, motif_length):
    after_sarus_fasta_path = get_tf_sarus_path(tf_name, 'sarus')
    sarus_table_path = get_tf_sarus_path(tf_name)
    dict_of_snps = make_dict_from_data(after_sarus_fasta_path, motif_length)
    tf_df = pd.read_table(os.path.join(results_path, 'TF_P-values', tf_name + '.tsv'))
    tf_df = tf_df.apply(lambda x: adjust_with_sarus(x, dict_of_snps), axis=1)
    tf_df.to_csv(sarus_table_path, header=True, sep='\t', index=False)