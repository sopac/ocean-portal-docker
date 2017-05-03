#!/usr/bin/env sh

export PYTHONPATH=${PYTHONPATH}:/srv/map-portal/usr/lib/python2.6/site-packages/:/srv/map-portal/usr/lib64/python2.6/site-packages
export PATH=${PATH}:/srv/gsmith/usr/bin/
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/srv/gsmith/usr/lib/

	python << EOF

# calculate monthly averages
from ocean.processing.Calculate_MultiMonth_Averages import Calculate_MultiMonth_Averages
from ocean.processing.Calculate_Monthly_Averages import Calculate_Monthly_Averages
Calculate_Monthly_Averages().process("BRAN_u")
Calculate_MultiMonth_Averages().process("BRAN_u")
Calculate_Monthly_Averages().process("BRAN_v")
Calculate_MultiMonth_Averages().process("BRAN_v")
Calculate_Monthly_Averages().process("BRAN_eta")
Calculate_MultiMonth_Averages().process("BRAN_eta")
Calculate_Monthly_Averages().process("BRAN_temp")
Calculate_MultiMonth_Averages().process("BRAN_temp")
Calculate_Monthly_Averages().process("BRAN_salt")
Calculate_MultiMonth_Averages().process("BRAN_salt")

EOF
