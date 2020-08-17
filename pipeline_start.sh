#!/bin/bash

njobs=$1
flag=$2
start_script_path="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

previous_pwd=$PWD
cd $start_script_path

python3 "construct_parameters_python.py"

source "scripts/HELPERS/paths_for_components.py"

case "$2" in
  --create_reference) stage_index=1
    ;;
  --snp_call) stage_index=2
    ;;
  --peak_call) stage_index=3
    ;;
  --bad_call) stage_index=4
    ;;
  --nb_fit) stage_index=5
    ;;
  --p_value_count) stage_index=6
    ;;
  --aggregate_p_values) stage_index=7
    ;;
  *)
    echo "There is no option $1"
    stage_index=0
    ;;
esac

if [ "$stage_index" -le 1 ]; then

  bash "create_reference.sh" -RefFolder "$reference_path" -RefGenome "$genome_path"
  python3 "PARAMETERS/make_badmaps_dict.py"
  python3 "SNPcalling/"sort_columns.py
  python3 "PARAMETERS/create_initial_dirs.py"
  python3 "PARAMETERS/make_aggregation_dict.py" TF
  python3 "PARAMETERS/make_aggregation_dict.py" CL
fi

if [ "$stage_index" -le 2 ]; then
  bash snp_calling.sh "$njobs"
fi

if [ "$stage_index" -le 3 ]; then
  bash annotation.sh "$njobs"
fi

if [ "$stage_index" -le 4 ]; then
  bash bad_map_est.sh "$njobs" --merge
  bash BAD_annotation.sh "$njobs"
fi

if [ "$stage_index" -le 5 ]; then
  python3 FITnoise/collect_ref_bias_statistics.py
  python3 FITnoise/fit_negative_binom_with_weights.py
fi

if [ "$stage_index" -le 6 ]; then
  bash p_value_count.sh "$njobs"
fi

if [ "$stage_index" -le 7 ]; then
  bash aggregation.sh "$njobs" --forTF
  bash aggregation.sh "$njobs" --forCL
fi

cd $previous_pwd