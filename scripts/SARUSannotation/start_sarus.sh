#!/bin/bash

source scripts/HELPERS/Config.cfg
source scripts/HELPERS/paths_for_components.py

GETNAME(){
	local var=$1
	local varpath=${var%/*}
	[ "$varpath" != "$var" ] && local vartmp="${var:${#varpath}}"
		echo "${vartmp%_*_*}"
}

tf_name=$1

# shellcheck disable=SC2154
echo $pwms_path"/$tf_name"/
if [ -d "${pwms_path}/$tf_name"/ ]; then

  motif_len=$(wc -l "${pwms_path}/$tf_name/"*)
#  motif_len=$((${motive_len%" "*}))

  if ! adastra extract_sarus_data --tf-name "$tf_name" --motif-len "${motif_len}"
  then
        echo "Failed to extract adjacent nucleotides"
        exit 0
  fi
  sarus_dir_base_path="${results_path}/Sarus/${tf_name}"
  if [ -s "${sarus_dir_base_path}.fasta" ]; then
    echo "Make sarus"
    # shellcheck disable=SC2154

    if ! $Java -cp "${parameters_path}/sarus.jar" ru.autosome.SARUS "${sarus_dir_base_path}.fasta" \
                            "${pwms_path}/${tf_name}/"* \
                            -10000000 \
                            --pvalues-file "${thresholds_path}/${tf_name}"* \
                            --threshold-mode score \
                            --output-scoring-mode logpvalue \
                            > "${sarus_dir_base_path}.sarus"
    then
          echo "Failed sarus"
          exit 0
    fi

  else
    echo "NO ASB found for ${tf_name}"
  fi
  if [ -f "${sarus_dir_base_path}.fasta" ]; then
    rm "${sarus_dir_base_path}.fasta"
  fi
else
  echo "No PWMs_path found for $tf_name"
fi

if ! adastra annotate_table_with_sarus --tf-name "$tf_name" --motif-len "${motif_len}"
then
  echo "Failed to add fc to the table"
  exit 0
fi

if [ -f "${sarus_dir_base_path}.sarus" ]; then
  rm "${sarus_dir_base_path}.sarus"
fi
