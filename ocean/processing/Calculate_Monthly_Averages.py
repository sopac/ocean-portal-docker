#!/usr/bin/env python
"""
Title: Calculate_Monthly_Averages.py
Author: Nicholas Summons, Grant Smith
CreationDate: 2012-11-05

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

class Calculate_Monthly_Averages():

    def __init__(self):

        sys_config = get_server_config()

        reynolds_end_date = self.get_date_for_last_complete_month()
        nrt_sea_level_end_date = self.get_date_for_last_complete_month()

        # Settings for each dataset
        self.config = \
            {'reynolds':{
                'product_str': 'reynolds_sst',
                'start_year': 1981,
                'start_month': 9,
                'end_year': reynolds_end_date.year,
                'end_month': reynolds_end_date.month,
                'input_dir': os.path.join(sys_config.dataDir['reynolds'], 'daily-new-uncompressed/'),
                'input_filename': 'avhrr-only-v2.%(year)04d%(month)02d%(day)02d.nc',
                'output_dir': os.path.join(sys_config.dataDir['reynolds'], 'averages/monthly/'),
                'output_filename': '%(product_str)s_avhrr-only-v2_%(year)04d%(month)02d.nc',
                'input_filename_preliminary': 'avhrr-only-v2.%(year)04d%(month)02d%(day)02d_preliminary.nc',
                'output_filename_preliminary': '%(product_str)s_avhrr-only-v2_%(year)04d%(month)02d_preliminary.nc',
                'use_old_version_of_ncea': True},
             'msla':{
                'product_str': 'nrt_sea_level',
                'start_year': 2015,
                'start_month': 8,
                'end_year': nrt_sea_level_end_date.year,
                'end_month': nrt_sea_level_end_date.month,
                'input_dir': os.path.join(sys_config.dataDir['msla'],'grids/daily'),
                'input_filename': 'nrt_global_allsat_msla_h_%(year)04d%(month)02d%(day)02d_%(year)04d%(month)02d%(day)02d.nc',
                'output_dir': os.path.join(sys_config.dataDir['msla'], 'grids/monthly/'),
                'output_filename': '%(product_str)s_%(year)04d%(month)02d.nc',
                'input_filename_preliminary': '',
                'output_filename_preliminary': '',
                'processing_settings':'-v sla'},
             'BRAN_eta':{
                'product_str': 'bran3.5_',
                'start_year': 1993,
                'start_month': 1,
                'end_year': 2012,
                'end_month': 07,  # Note patch in function _calc_monthly_average to handle missing BRAN files for 31 Dec 2006
                'input_dir': '/data/blue_link/data/BRAN3p5/daily/eta_compressed/',
                'input_filename': 'ocean_eta_%(year)04d_%(month)02d_%(day)02d.nc4',
                'output_dir': '/data/blue_link/data/BRAN3p5/monthly/eta/',
                'output_filename': 'eta_%(year)04d_%(month)02d.nc4',
                'input_filename_preliminary': '',
                'output_filename_preliminary': '',
                'processing_settings':'-v eta_t'},
             'BRAN_u':{
                'product_str': 'bran3.5_',
                'start_year': 1993,
                'start_month': 1,
                'end_year': 2012,
                'end_month': 07,
                'input_dir': '/data/blue_link/data/BRAN3p5/daily/u_compressed/',
                'input_filename': 'ocean_u_%(year)04d_%(month)02d_%(day)02d.nc4',
                'output_dir': '/data/blue_link/data/BRAN3p5/monthly/u/',
                'output_filename': 'u_%(year)04d_%(month)02d.nc4',
                'input_filename_preliminary': '',
                'output_filename_preliminary': '',
                'processing_settings':'-v u'},
             'BRAN_v':{
                'product_str': 'bran3.5_',
                'start_year': 1993,
                'start_month': 1,
                'end_year': 2012,
                'end_month': 07,
                'input_dir': '/data/blue_link/data/BRAN3p5/daily/v_compressed/',
                'input_filename': 'ocean_v_%(year)04d_%(month)02d_%(day)02d.nc4',
                'output_dir': '/data/blue_link/data/BRAN3p5/monthly/v/',
                'output_filename': 'v_%(year)04d_%(month)02d.nc4',
                'input_filename_preliminary': '',
                'output_filename_preliminary': '',
                'processing_settings':'-v v'},
             'BRAN_temp':{
                'product_str': 'bran3.5_',
                'start_year': 1993,
                'start_month': 1,
                'end_year': 2012,
                'end_month': 07,
                'input_dir': '/data/blue_link/data/BRAN3p5/daily/temp_compressed/',
                'input_filename': 'ocean_temp_%(year)04d_%(month)02d_%(day)02d.nc4',
                'output_dir': '/data/blue_link/data/BRAN3p5/monthly/temp/',
                'output_filename': 'temp_%(year)04d_%(month)02d.nc4',
                'input_filename_preliminary': '',
                'output_filename_preliminary': '',
                'processing_settings':'-v temp'},
             'BRAN_salt':{
                'product_str': 'bran3.5_',
                'start_year': 1993,
                'start_month': 1,
                'end_year': 2012,
                'end_month': 07,
                'input_dir': '/data/blue_link/data/BRAN3p5/daily/salt_compressed/',
                'input_filename': 'ocean_salt_%(year)04d_%(month)02d_%(day)02d.nc4',
                'output_dir': '/data/blue_link/data/BRAN3p5/monthly/salt/',
                'output_filename': 'salt_%(year)04d_%(month)02d.nc4',
                'input_filename_preliminary': '',
                'output_filename_preliminary': '',
                'processing_settings':'-v salt'}
            }

    def process(self, dataset):
        """
        Calculate monthly averages for the dataset specified by the input argument.
        """
        settings = self.config[dataset]
        start_year = settings['start_year']
        start_month = settings['start_month']
        end_year = settings['end_year']
        end_month = settings['end_month']
	print end_month

        # Loop through months in date range
        for year in range(start_year, end_year + 1):
            for month in range(1, 12 + 1):
                if (year == start_year) and (month < start_month):
                    continue
                if (year == end_year) and (month > end_month):
                    break
                self._calc_monthly_average(settings, year, month)

    def get_date_for_last_complete_month(self):
        last_date_to_use = datetime.date.today() + dateutil.relativedelta.relativedelta(days=-2)
        year = last_date_to_use.year
        month = last_date_to_use.month - 1
        if month == 0:
            month = 12
            year -= 1
        end_date = datetime.datetime(year, month, 1)
        return end_date

    def _calc_monthly_average(self, settings, year, month):
        input_files = []
        input_files_timestamps = []
        days_in_month = calendar.monthrange(year, month)[1]

        # Patch for BRAN which is missing final day of data for 2006
        if (settings['product_str'] == 'bran2.1_') and (year == 2006) and (month == 12):
            days_in_month = 30

        preliminary_data_used = False
        settings['year'] = year
        settings['month'] = month

        # Create list of input files and check if the files exist
	missing_file_count=0
        for day in range(1, days_in_month + 1):
            settings['day'] = day
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
            #if not os.path.exists(input_file_fullpath):
            if os.path.exists(input_file_fullpath):
                 input_files.append(input_file_fullpath)
	         input_files_timestamps.append(os.path.getmtime(input_file_fullpath))
                # Use preliminary file if exists instead
            elif os.path.exists(input_file_preliminary_fullpath):
                 input_file_fullpath = input_file_preliminary_fullpath
                 preliminary_data_used = True
                 input_files.append(input_file_fullpath)
                 input_files_timestamps.append(os.path.getmtime(input_file_fullpath))
            else:
                 print >> sys.stderr, 'Missing input file: ' + input_file_fullpath
                 #raise Exception('Missing input file: ' + input_file_fullpath)
                 missing_file_count=missing_file_count+1
                 if missing_file_count > 5:
                      raise Exception('Too many missing files, more than five')
                      break

            #input_files.append(input_file_fullpath)
            #input_files_timestamps.append(os.path.getmtime(input_file_fullpath))

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
