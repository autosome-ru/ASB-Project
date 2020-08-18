#!/bin/bash
source scripts/HELPERS/soft_configs.cfg
source scripts/HELPERS/paths_for_components.py

PEAKannotationScriptsPath=${scripts_path}/PEAKannotation/

GETNAME(){
	local var=$1
	local varpath=${var%/*}
	[ "$varpath" != "$var" ] && local vartmp="${var:${#varpath}}"
		echo "${vartmp%.*}"
}


withmacs=false
withsissrs=false
withcpics=false
withgem=false

while [ "$(echo "$1" | cut -c1)" = "-" ]
do
  case "$1" in

	  -Out) OUT=$2
		  shift 2;;

	  -macs) withmacs=true
		  macs=$2
		  shift 2;;

	  -sissrs) withsissrs=true
		  sissrs=$2
		  shift 2;;

	  -cpics) withcpics=true
		  cpics=$2
		  shift 2;;

	  -gem) withgem=true
		  gem=$2
		  shift 2;;

	  -VCF) VCF=$2
		  shift 2;;

	  *)
		  echo "There is no option $1"
		  break;;

  esac
done

if [ $withgem != false ]; then
	adastra check_pos_peaks --peak "$gem" --out "${OUT}_gem.bed" --type 'gem'
	# shellcheck disable=SC2154
	if ! bedtools sort -i "${OUT}_gem.bed" > "${OUT}_gem.bed.sorted"
	then
		echo "Failed to sort gem peaks"
		exit 1
	fi
	rm "${OUT}_gem.bed"
fi

if [ $withmacs != false ]; then
	adastra check_pos_peaks --peak "$macs" --out "${OUT}_macs.bed" --type 'macs'

	if ! bedtools sort -i "${OUT}_macs.bed" > "${OUT}_macs.bed.sorted"
	then
		echo "Failed to sort macs peaks"
		exit 1
	fi
  rm "${OUT}_macs.bed"
fi

if [ $withsissrs != false ]; then
	adastra check_pos_peaks --peak "$sissrs" --out "${OUT}_sissrs.bed" --type 'sissrs'

	if ! bedtools sort -i "${OUT}_sissrs.bed" > "${OUT}_sissrs.bed.sorted"
	then
		echo "Failed to sort sissrs peaks"
		exit 1
	fi
  rm "${OUT}_sissrs.bed"
fi

if [ $withcpics != false ]; then
	adastra check_pos_peaks --peak "$cpics" --out "${OUT}_cpics.bed" --type 'cpics'

	if ! bedtools sort -i "${OUT}_cpics.bed" > "${OUT}_cpics.bed.sorted"
	then
		echo "Failed to sort cpics peaks"
		exit 1
	fi
  rm "${OUT}_cpics.bed"
fi

adastra annotate_peaks --vcf "$VCF" --out "${OUT}_table_annotated.txt"


if [ "$withgem" != false ]; then
	rm "${OUT}_gem.bed.sorted"
fi

if [ "$withcpics" != false ]; then
	rm "${OUT}_cpics.bed.sorted"
fi

if [ "$withmacs" != false ]; then
  rm "${OUT}_macs.bed.sorted"
fi

if [ "$withsissrs" != false ]; then
  rm "${OUT}_sissrs.bed.sorted"
fi
