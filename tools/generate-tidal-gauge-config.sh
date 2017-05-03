#
# Generate backend tidal gauges config from front end tidal gauges config
#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>
#

TAB="`printf \"\t\"`"

cat << EOF
#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# This file was automatically generated from tidalGauges.txt
#

tidalGauge = {
EOF

read # skip the first line
while IFS=$TAB read lat lon name id region; do
	cat << EOF
    "$id": {
        'name': "$name",
        'lat': $lat,
        'lon': $lon,
	'region': "$region",
    },
EOF
done

cat << EOF
}
EOF
