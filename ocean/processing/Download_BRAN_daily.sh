#!/bin/bash
array=(v u eta salt temp)
first_year=1993
last_year=2012
first_month=01
last_month=12
for var in "${array[@]}"
do
  echo ${var}
  for i in $(seq -w "$first_year" "$last_year")
  do
    if [ $i -ne $first_year ]
    then
      printf -v first_month '%02d' 01
    fi
    for j in $(seq -w "$first_month" "$last_month")
    do
      if [ $i -eq "$first_year" ] && [ $j -eq "$first_month" ]
      then
        echo "Download first file...ocean_${var}_${i}_${j}.nc"
        curl -O http://dapds00.nci.org.au/thredds/fileServer/gb6/BRAN/BRAN3p5/OFAM/ocean_${var}_${i}_${j}.nc
      else
        if [ $j -eq 01 ]
        then
          prev_month=12
          let prev_year=$i-1
        else
          printf -v prev_month '%02d' $((10#$j-1))
          prev_year=$i
        fi
        echo "Download next file...ocean_${var}_${i}_${j}.nc"
        curl -O http://dapds00.nci.org.au/thredds/fileServer/gb6/BRAN/BRAN3p5/OFAM/ocean_${var}_${i}_${j}.nc &
        for k in {01..31}
        do
          printf -v time_num '%02d' $((10#$k-1))
          echo "Extract each day of month...ocean_${var}_${prev_year}_${prev_month}_${k}.nc from ocean_${var}_${prev_year}_${prev_month}.nc"
          if [ ${var} == "eta" ]
          then
            #/home/sguo/temp/ncolib/bin/ncks -4 -O -v eta_t -d Time,${time_num} ocean_${var}_${prev_year}_${prev_month}.nc /data/blue_link/data/BRAN3p5/daily/${var}_compressed/ocean_${var}_${prev_year}_${prev_month}_${k}.nc4
            ncks -4 -O -v eta_t -d Time,${time_num} ocean_${var}_${prev_year}_${prev_month}.nc /data/blue_link/data/BRAN3p5/daily/${var}_compressed/ocean_${var}_${prev_year}_${prev_month}_${k}.nc4
          else
            #/home/sguo/temp/ncolib/bin/ncks -4 -O -v ${var} -d st_ocean,0,29 -d Time,${time_num} ocean_${var}_${prev_year}_${prev_month}.nc /data/blue_link/data/BRAN3p5/daily/${var}_compressed/ocean_${var}_${prev_year}_${prev_month}_${k}.nc4
            ncks -4 -O -v ${var} -d st_ocean,0,29 -d Time,${time_num} ocean_${var}_${prev_year}_${prev_month}.nc /data/blue_link/data/BRAN3p5/daily/${var}_compressed/ocean_${var}_${prev_year}_${prev_month}_${k}.nc4
          fi
        done
        rm ./ocean_${var}_${prev_year}_${prev_month}.nc
        wait
      fi
    done
  done
  for k in {01..31}
  do
    printf -v time_num '%02d' $((10#$k-1))
    echo "Extract each day of month...ocean_${var}_${i}_${j}_${k}.nc from ocean_${var}_${i}_${j}.nc"
    if [ ${var} == "eta" ]
    then
      #/home/sguo/temp/ncolib/bin/ncks -4 -O -v eta_t -d Time,${time_num} ocean_${var}_${i}_${j}.nc /data/blue_link/data/BRAN3p5/daily/${var}_compressed/ocean_${var}_${i}_${j}_${k}.nc4
      ncks -4 -O -v eta_t -d Time,${time_num} ocean_${var}_${i}_${j}.nc /data/blue_link/data/BRAN3p5/daily/${var}_compressed/ocean_${var}_${i}_${j}_${k}.nc4
    else
      #/home/sguo/temp/ncolib/bin/ncks -4 -O -v ${var} -d st_ocean,0,29 -d Time,${time_num} ocean_${var}_${i}_${j}.nc /data/blue_link/data/BRAN3p5/daily/${var}_compressed/ocean_${var}_${i}_${j}_${k}.nc4
      ncks -4 -O -v ${var} -d st_ocean,0,29 -d Time,${time_num} ocean_${var}_${i}_${j}.nc /data/blue_link/data/BRAN3p5/daily/${var}_compressed/ocean_${var}_${i}_${j}_${k}.nc4
    fi
  done
  rm ./ocean_${var}_${i}_${j}.nc
done
