import json
import sys
from scipy.stats import binom_test, binom


sys.path.insert(1, "/home/abramov/ASB-Project")
from scripts.HELPERS.paths import ploidy_dict_path, create_ploidy_path_function
from scripts.HELPERS.helpers import callers_names, unpack, pack, Intersection


corrected = {1: 1, 1.5: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 6}


def count_p(x, n, p, alternative, cut_off=2):
    if x <= cut_off or x >= n - cut_off:
        raise ValueError('Read-counts {} must be greater than cut off value {}'.format(x, cut_off))
    tail = binom_test(cut_off, n, p, alternative='less') + binom_test(n - cut_off, n, p, alternative='greater')

    pv = (binom_test(x, n, p, alternative) + binom_test(x, n, 1 - p, alternative)) / 2
    pv_corrected = 0.5 + (pv - 0.5) / (1 - tail)
    pv_balanced = pv_corrected - binom(n, p).pmf(x) / 2

    return pv, pv_corrected, pv_balanced


def make_reverse_dict(dictionary):
    new_dict = {}
    for key in dictionary:
        paths = dictionary[key]
        for path in paths:
            if path.split("/")[-3] != "CTRL":
                new_dict[path] = key
    return new_dict


if __name__ == '__main__':
    full_path = sys.argv[1]

    key = full_path + ".vcf.gz"
    table_annotated = full_path + "_table_annotated.txt"
    output = full_path + "_table_p.txt"

    with open(ploidy_dict_path, "r") as read_file:
        d = json.loads(read_file.readline())
        rev_d = make_reverse_dict(d)

    ploidy = create_ploidy_path_function(rev_d[key])

    print('Now doing {} \n with ploidy file {}'.format(table_annotated, rev_d[key]))

    with open(ploidy, 'r') as ploidy_file, open(output, 'w') as out, open(table_annotated, 'r') as table_file:
        out.write(pack(['#chr', 'pos', 'ID', 'ref', 'alt', 'ref_read_counts', 'alt_read_counts',
                        'repeat_type'] + callers_names + ['BAD', 'Q1', 'left_qual', 'right_qual', 'SNP_count',
                                                          'sum_cover',
                                                          'p_value_ref', 'p_value_alt',
                                                          'p_value_ref_corrected', 'p_value_alt_corrected',
                                                          'p_value_ref_balanced', 'p_value_alt_balanced',
                                                          ]))

        for chr, pos, ID, ref, alt, ref_c, alt_c, repeat_type, in_callers, \
            in_intersection, ploidy, dip_qual, lq, rq, seg_c, sum_cov in \
                Intersection(table_file, ploidy_file, write_segment_args=True, write_intersect=True,
                             unpack_snp_function=lambda x: unpack(x, use_in='Pcounter')):
            if in_intersection:
                #  p_value counting
                p = 1 / (float(ploidy) + 1)
                p = corrected.get(p, p)  # up-correct ploidy
                n = ref_c + alt_c

                p_ref, p_ref_cor, p_ref_bal = count_p(ref_c, n, p, 'greater')
                p_alt, p_alt_cor, p_alt_bal = count_p(ref_c, n, p, 'less')
            else:
                ploidy = 0

                p_ref, p_ref_cor, p_ref_bal = '.', '.', '.'
                p_alt, p_alt_cor, p_alt_bal = '.', '.', '.'

            out.write(pack([chr, pos, ID, ref, alt, ref_c, alt_c, repeat_type] +
                           [in_callers[name] for name in callers_names] +
                           [ploidy, dip_qual, lq, rq, seg_c, sum_cov,
                            p_ref, p_alt,
                            p_ref_cor, p_alt_cor,
                            p_ref_bal, p_alt_bal,
                            ]))
