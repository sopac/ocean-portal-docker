echo Updating Pacific Ocean Portal...
chmod 777 -R /opt/data

echo UPDATING: reynolds
/opt/ocean-portal/usr/local/bin/update-data reynolds
echo \n\n
chmod 777 -R /opt/data

echo UPDATING: ersst
/opt/ocean-portal/usr/local/bin/update-data ersst
echo \n\n
chmod 777 -R /opt/data

echo UPDATING: sealevel
/opt/ocean-portal/usr/local/bin/update-data sealevel
echo \n\n
chmod 777 -R /opt/data

echo UPDATING: decile
/opt/ocean-portal/usr/local/bin/update-data decile
echo \n\n
chmod 777 -R /opt/data

echo UPDATING: ww3
/opt/ocean-portal/usr/local/bin/update-data ww3
echo \n\n
chmod 777 -R /opt/data

echo UPDATING: chloro daily
/opt/ocean-portal/usr/local/bin/update-data chloro daily
echo \n\n
chmod 777 -R /opt/data

echo UPDATING: chloro monthly
/opt/ocean-portal/usr/local/bin/update-data chloro monthly
echo \n\n
chmod 777 -R /opt/data

echo UPDATING: poamasla
/opt/ocean-portal/usr/local/bin/update-data poamasla
echo \n\n
chmod 777 -R /opt/data

echo UPDATING: poamassta
/opt/ocean-portal/usr/local/bin/update-data poamassta
echo \n\n
chmod 777 -R /opt/data

echo UPDATING: coral
/opt/ocean-portal/usr/local/bin/update-data coral
echo \n\n
chmod 777 -R /opt/data

echo UPDATING: coral_ol
/opt/ocean-portal/usr/local/bin/update-data coral_ol
echo \n\n
chmod 777 -R /opt/data

echo UPDATING: currents
/opt/ocean-portal/usr/local/bin/update-data current
echo \n\n
chmod 777 -R /opt/data

echo UPDATING: mur
/opt/ocean-portal/usr/local/bin/update-data mur
echo \n\n
chmod 777 -R /opt/data

echo UPDATING: msla
/opt/ocean-portal/usr/local/bin/update-data msla
echo \n\n
chmod 777 -R /opt/data

echo FINISHED.
