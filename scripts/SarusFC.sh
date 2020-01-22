#!/bin/bash

source HELPERS/Config.cfg
source HELPERS/paths_for_components.py

GETNAME(){
	local var=$1
	local varpath=${var%/*}
	[ "$varpath" != "$var" ] && local vartmp="${var:${#varpath}}"
		echo "${vartmp%_*_*}"
}

file=$1
ExpFile=$( GETNAME "$file" )
ExpName=${ExpFile%.*}

# shellcheck disable=SC2154
echo $PWMs_path"$ExpName"/
if [ -d "${PWMs_path}/$ExpName"/ ]; then
  # shellcheck disable=SC2154

  motive_len=$(wc -l "${PWMs_path}/$ExpName/"*)
  motive_len=$((${motive_len%" "*}))

  # shellcheck disable=SC2154
  if ! $python3 "${scripts_path}SARUSannotation/"extract_sarus_data.py "$file" "$FA" \
    "${sarus_path}${ExpName}_ape_data.txt" "${motive_len}"
  then
        echo "Failed to extract adjacent nucleotides"
        exit 0
  fi

  if [ -s "${sarus_path}${ExpName}_ape_data.txt" ]; then
    echo "Make sarus"
    # shellcheck disable=SC2154

    if ! $Java -cp "${parameters_path}sarus-2.0.1.jar" ru.autosome.SARUS "${sarus_path}${ExpName}_ape_data.txt" \
                            "${PWMs_path}/$ExpName/"* \
                            -10000000 \
                            --pvalues-file "${threshold_path}${ExpName}"* \
                            --threshold-mode score \
                            --output-scoring-mode logpvalue \
                            > "${sarus_path}${ExpName}_ape.txt"
    then
          echo "Failed sarus"
          exit 0
    fi




  else
    echo "NO ASB found for ${ExpName}"
  fi
  rm "${sarus_path}${ExpName}_ape_data.txt"
else
  echo "No PWMs_path found for $ExpName"
fi

if ! $python3 "${scripts_path}SARUSannotation/"adjust_table_with_sarus.py "${file}" \
  "${sarus_path}${ExpName}_ape.txt" "${sarus_path}${ExpName}_fc.tsv" "${motive_len}";
then
  echo "Failed to add fc to the table"
  exit 0
fi

if [ -f "${sarus_path}${ExpName}_ape.txt" ]; then
  rm "${sarus_path}${ExpName}_ape.txt"
fi