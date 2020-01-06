import sys
import os.path
from statistics import median_grouped
from scipy import stats
import numpy as np
import json

sys.path.insert(1, "/home/abramov/ASB-Project")
from scripts.HELPERS.paths import results_path, cl_dict_path, tf_dict_path, parameters_path
from scripts.HELPERS.helpers import callers_names, unpack, pack, check_if_in_expected_args, expected_args, states


def logit_combine_p_values(pvalues):
    if 0 in pvalues:
        return 0
    pvalues = np.array([p for p in pvalues if 1 > p > 0])
    if len(pvalues) == 0:
        return 1
    elif len(pvalues) == 1:
        return pvalues[0]

    statistic = -np.sum(np.log(pvalues)) + np.sum(np.log1p(-pvalues))
    k = len(pvalues)
    nu = np.int_(5 * k + 4)
    approx_factor = np.sqrt(np.int_(3) * nu / (np.int_(k) * np.square(np.pi) * (nu - np.int_(2))))
    pval = stats.distributions.t.sf(statistic * approx_factor, nu)
    return pval


def annotate_snp_with_tables(dictionary, ps_ref, ps_alt, bool_ar):  # return part of the dictionary with fdr from table
    keys = list(dictionary.keys())
    for index in range(len(ps_ref)):
        key = keys[index]
        if bool_ar[index]:
            dictionary[key]['logitp_ref'] = ps_ref[index]
            dictionary[key]['logitp_alt'] = ps_alt[index]
        else:
            del dictionary[key]


def get_name(path):  # path format */ALIGNS000000_table_p.txt
    return path.split("/")[-1].split("_")[0]



def invert(dictionary):
    inverted_dictionary = {}
    for key in dictionary:
        for value in dictionary[key]:
            inverted_dictionary[value] = key
    return inverted_dictionary


def get_another_agr(path):
    return invert(cell_lines_dict).get(path, "None")


if __name__ == '__main__':
    keys = ["CTCF_HUMAN"]

    with open(tf_dict_path, "r") as read_file:
        tf_dict = json.loads(read_file.readline())
    with open(cl_dict_path, "r") as read_file:
        cell_lines_dict = json.loads(read_file.readline())
        inv_cl_dict = invert(cell_lines_dict)
    keys = tf_dict.keys()
    with open(parameters_path + 'Union_SNP_table.tsv', 'w') as out:
        out.write(pack(['#chr', 'pos', 'ID', 'ref', 'alt', 'ref_read_counts', 'alt_read_counts', 'repeat',
                        'BAD', 'ALIGN_NAME', 'Cell_line']))
        for key_name in keys:
            tables = list(map(lambda x: x.replace('table_p', 'table_BADs'), tf_dict[key_name]))

            common_snps = []
            for table in tables:
                if os.path.isfile(table):
                    table_name = get_name(table)
                    with open(table, 'r') as file:
                        for line in file:
                            if line[0] == "#":
                                continue
                            chr, pos, ID, ref, alt, ref_c, alt_c, repeat, _, _, _, _, ploidy, = line.strip().split("\t")[:13]
                            if ploidy == "0":
                                continue
                            common_snps.append([chr, pos, ID, ref, alt, ref_c, alt_c, repeat, ploidy, table_name,
                                                inv_cl_dict[table.replace('table_BADs', 'table_p')]])

            print('Writing {}'.format(key_name))


            common_snps = sorted(common_snps, key=lambda chr_pos: chr_pos[1])
            common_snps = sorted(common_snps, key=lambda chr_pos: chr_pos[0])
            BADs = set()
            for snp in common_snps:
                BADs.add(snp[-3])
                out.write(pack(snp))
        print(BADs)