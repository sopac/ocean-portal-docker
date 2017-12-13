#!/bin/bash

# Run initial data loading
# This should match cron jobs...
echo 'Running all update-data jobs... This will take a while !'
echo "update-data reynolds"
/ocean-portal/src/update-data reynolds >> /opt/data/logs_reynolds_initial.txt 2>&1
echo "update-data ersst"
/ocean-portal/src/update-data ersst >> /opt/data/logs_ersst_initial.txt 2>&1
echo "update-data sealevel"
/ocean-portal/src/update-data sealevel >> /opt/data/logs_sealevel_initial.txt 2>&1
echo "update-data ww3"
/ocean-portal/src/update-data ww3 >> /opt/data/logs_ww3_initial.txt 2>&1
echo "update-data chloro daily"
/ocean-portal/src/update-data chloro daily >> /opt/data/logs_chloro-daily_initial.txt 2>&1
echo "update-data chloro monthly"
/ocean-portal/src/update-data chloro monthly >> /opt/data/logs_chloro-monthly_initial.txt 2>&1
echo "update-data poamasla"
/ocean-portal/src/update-data poamasla >> /opt/data/logs_poamasla_initial.txt 2>&1
echo "update-data poamassta"
/ocean-portal/src/update-data poamassta >> /opt/data/logs_poamassta_initial.txt 2>&1
echo "update-data coral"
/ocean-portal/src/update-data coral >> /opt/data/logs_coral_initial.txt 2>&1
echo "update-data coral_ol"
/ocean-portal/src/update-data coral_ol >> /opt/data/logs_coral_ol_initial.txt 2>&1
echo "update-data currents"
/ocean-portal/src/update-data currents >> /opt/data/logs_currents_initial.txt 2>&1
echo "update-data mur"
/ocean-portal/src/update-data mur >> /opt/data/logs_mur_initial.txt 2>&1
echo "update-data msla"
/ocean-portal/src/update-data msla >> /opt/data/logs_msla_initial.txt 2>&1

# Start cron
cron

# Start apache in foreground
apachectl -D FOREGROUND