#!/usr/bin/env python
"""
Title: Calculate_Monthly_Averages.py
Author: Grant Smith
CreationDate: 2016-01-05

Description:
    Calculates monthly averages from daily NetCDF data files.
"""
import os
import sys
import subprocess
import copy
import pdb
import calendar
import datetime
import dateutil.relativedelta

from ocean.config import get_server_config

class Calculate_Weekly_Averages():

    def __init__(self):

        sys_config = get_server_config()

        reynolds_end_date = self.get_date_for_last_complete_week()
	nrt_sea_level_end_date = self.get_date_for_last_complete_week()

        # Settings for each dataset
        self.config = \
            {'reynolds':{
                'product_str': 'reynolds_sst',
                'start_year': 1981,
                'start_month': 9,
		'start_day': 1,
                'end_year': reynolds_end_date.year,
                'end_month': reynolds_end_date.month,
		'end_day': reynolds_end_date.day,
                'input_dir': os.path.join(sys_config.dataDir['reynolds'], 'daily-new-uncompressed/'),
                'input_filename': 'avhrr-only-v2.%(year)04d%(month)02d%(day)02d.nc',
                'output_dir': os.path.join(sys_config.dataDir['reynolds'], 'averages/weekly/'),
                'output_filename': '%(product_str)s_avhrr-only-v2_%(year)04d%(month)02d_week_%(week)02d.nc',
                'input_filename_preliminary': 'avhrr-only-v2.%(year)04d%(month)02d%(day)02d_preliminary.nc',
                'output_filename_preliminary': '%(product_str)s_avhrr-only-v2_%(year)04d%(month)02d_week_%(week)02d_preliminary.nc',
                'use_old_version_of_ncea': False},
             'msla':{
                'product_str': 'nrt_sea_level',
                'start_year': 2015,
                'start_month': 8,
                'end_year': nrt_sea_level_end_date.year,
                'end_month': nrt_sea_level_end_date.month,
                'input_dir': os.path.join(sys_config.dataDir['msla'],'grids/daily'),
                'input_filename': 'nrt_global_allsat_msla_h_%(year)04d%(month)02d%(day)02d_%(year)04d%(month)02d%(day)02d.nc',
                'output_dir': os.path.join(sys_config.dataDir['msla'], 'grids/weekly/'),
                'output_filename': '%(product_str)s_%(year)04d%(month)02d.nc',
                'input_filename_preliminary': '',
                'output_filename_preliminary': '',
                'processing_settings':'-v sla'},
            }

    def process(self, dataset):
        """
        Calculate weekly averages for the dataset specified by the input argument.
        """
        settings = self.config[dataset]
        start_year = settings['start_year']
        start_month = settings['start_month']
	start_day = settings['start_day']
        end_year = settings['end_year']
        end_month = settings['end_month']
	end_day =settings['end_day']
	print end_day, end_month

	start_date=datetime.datetime(start_year,start_month,start_day)
	end_date=datetime.datetime(end_year,end_month,end_day)
	idx = (start_date.weekday())
	if idx == 0:
		first_date_to_use = start_date
	else:
		first_date_to_use = start_date+dateutil.relativedelta.relativedelta(days=7-idx)
	num_of_days=end_date-first_date_to_use

	num_of_weeks=(num_of_days.days/7)+1
	

        # Loop through months in date range
        for week in range(1, num_of_weeks+1):
                self._calc_weekly_average(settings, first_date_to_use,week)

    def get_date_for_last_complete_week(self):
        last_date_to_use = datetime.date.today() + dateutil.relativedelta.relativedelta(days=-2)
	idx = (last_date_to_use.weekday())
	last_date_to_use = last_date_to_use + dateutil.relativedelta.relativedelta(days=-idx-1)
        year = last_date_to_use.year
        month = last_date_to_use.month
	day = last_date_to_use.day
        end_date = datetime.datetime(year, month, day)
	print end_date
        return end_date

    def _calc_weekly_average(self, settings, first_date,week):
        input_files = []
        input_files_timestamps = []

        preliminary_data_used = False
        settings['year'] =(first_date+dateutil.relativedelta.relativedelta(days=(week-1)*7)).year
        settings['month'] = (first_date+dateutil.relativedelta.relativedelta(days=(week-1)*7)).month
	settings['week'] = week
	
        # Create list of input files and check if the files exist
        for day in range(0, 7):
            settings['day'] = (first_date+dateutil.relativedelta.relativedelta(days=((week-1)*7)+day)).day
            input_dir = settings['input_dir'] % settings
            input_filename = settings['input_filename'] % settings
            input_filename_preliminary = settings['input_filename_preliminary'] % settings
            output_dir = settings['output_dir'] % settings
            output_filename = settings['output_filename'] % settings
            output_filename_preliminary = settings['output_filename_preliminary'] % settings

            input_file_fullpath = os.path.join(input_dir, input_filename)
            if input_filename_preliminary == '':
                input_file_preliminary_fullpath = ''
            else:
                input_file_preliminary_fullpath = os.path.join(input_dir, input_filename_preliminary)
            output_file_fullpath = os.path.join(output_dir, output_filename)
            output_file_preliminary_fullpath = os.path.join(output_dir, output_filename_preliminary)
             
            # Raise error if input file not found
            if not os.path.exists(input_file_fullpath):
                # Use preliminary file if exists instead
                if os.path.exists(input_file_preliminary_fullpath):
                    input_file_fullpath = input_file_preliminary_fullpath
                    preliminary_data_used = True
                else:
                    print >> sys.stderr, 'Missing input file: ' + input_file_fullpath
                    raise Exception('Missing input file: ' + input_file_fullpath)
                    break

            input_files.append(input_file_fullpath)
            input_files_timestamps.append(os.path.getmtime(input_file_fullpath))

        if preliminary_data_used:
            output_filename = output_filename_preliminary
            output_file_fullpath = output_file_preliminary_fullpath
        
        if os.path.exists(output_file_fullpath):
            output_file_timestamp = os.path.getmtime(output_file_fullpath)
            if output_file_timestamp > max(input_files_timestamps):
                # If output file already exists and is newer than input files => do nothing
                return
        else:
            # Create output directory if doesn't exist
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

        ncea_path = '/srv/map-portal/usr/bin/ncea'
        if settings.has_key('use_old_version_of_ncea'):
            if settings['use_old_version_of_ncea']:
                ncea_path = '/srv/map-portal/usr/bin/ncea'

        if 'processing_settings' in settings:
            ncea_settings = settings['processing_settings'] + ' '
        else:
            ncea_settings = ''
        cmd = ncea_path + ' -O ' + ncea_settings + ' '.join(input_files) + ' ' + output_file_fullpath
        proc = subprocess.call(cmd, shell=True)
