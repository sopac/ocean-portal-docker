#!/usr/bin/env python
"""
Title: Calculate_MultiMonth_Averages.py
Author: Nicholas Summons, n.summons@bom.gov.au
CreationDate: 2012-10-25

Description: 
    Calculates multi-month averages from monthly NetCDF data files where the
    averages are weighted by the number of days in each month.
    
    Note: This script is dependent on the NCO utilities package (http://nco.sourceforge.net/).
    This dependency will be removed in the near future.
"""
import os
import sys
import subprocess
import copy
import pdb
import calendar
import tempfile
import datetime
import dateutil.relativedelta

from ocean.config import get_server_config


class Calculate_MultiMonth_Averages():

    def __init__(self):
       
        sys_config = get_server_config()

        reynolds_end_date = self.get_date_for_last_complete_month()

        self.config = \
            {'ersst':{
                'product_str': 'ersst_v3b',
                'start_year': 1854,
                'start_month': 1,
                'end_year': reynolds_end_date.year,
                'end_month': reynolds_end_date.month,
                'input_dir': os.path.join(sys_config.dataDir['ersst'], 'monthly_processed/'),
                'input_filename': 'ersst.%(year)04d%(month)02d.nc',
                'output_dir': os.path.join(sys_config.dataDir['ersst'], 'averages/%(avg_period)dmonthly/'),
                'output_filename': '%(product_str)s_%(avg_period)dmthavg_%(date_str1)s_%(date_str2)s.nc',
                'avg_periods': [3, 6, 12]},
             'reynolds':{
                'product_str': 'reynolds_sst',
                'start_year': 1981,
                'start_month': 9,
                'end_year': reynolds_end_date.year,
                'end_month': reynolds_end_date.month,
                'input_dir': os.path.join(sys_config.dataDir['reynolds'], 'averages/monthly/'),
                'input_filename': '%(product_str)s_avhrr-only-v2_%(year)04d%(month)02d.nc',
                'input_filename_preliminary': '%(product_str)s_avhrr-only-v2_%(year)04d%(month)02d_preliminary.nc',
                'output_dir': os.path.join(sys_config.dataDir['reynolds'], 'averages/%(avg_period)dmonthly/'),
                'output_filename': '%(product_str)s_avhrr-only-v2_%(avg_period)dmthavg_%(date_str1)s_%(date_str2)s.nc',
                'output_filename_preliminary': '%(product_str)s_avhrr-only-v2_%(avg_period)dmthavg_%(date_str1)s_%(date_str2)s_preliminary.nc',
                'avg_periods': [3, 6, 12]},
             'BRAN_eta':{
                'product_str': 'bran3.5',
                'start_year': 1993,
                'start_month': 1,
                'end_year': 2012,
                'end_month': 7,
                'input_dir': '/data/blue_link/data/BRAN3p5/monthly/eta/',
                'input_filename': 'eta_%(year)04d_%(month)02d.nc4',
                'output_dir': '/data/blue_link/data/BRAN3p5/averages/%(avg_period)dmonthly/eta/',
                'output_filename': '%(product_str)s_%(avg_period)dmthavg_%(date_str1)s_%(date_str2)s.nc4',
                'avg_periods': [3, 6, 12]},
             'BRAN_temp':{
                'product_str': 'bran3.5',
                'start_year': 1993,
                'start_month': 1,
                'end_year': 2012,
                'end_month': 7,
                'input_dir': '/data/blue_link/data/BRAN3p5/monthly/temp/',
                'input_filename': 'temp_%(year)04d_%(month)02d.nc4',
                'output_dir': '/data/blue_link/data/BRAN3p5/averages/%(avg_period)dmonthly/temp/',
                'output_filename': '%(product_str)s_%(avg_period)dmthavg_%(date_str1)s_%(date_str2)s.nc4',
                'avg_periods': [3, 6, 12]},
             'BRAN_salt':{
                'product_str': 'bran3.5',
                'start_year': 1993,
                'start_month': 1,
                'end_year': 2012,
                'end_month': 7,
                'input_dir': '/data/blue_link/data/BRAN3p5/monthly/salt/',
                'input_filename': 'salt_%(year)04d_%(month)02d.nc4',
                'output_dir': '/data/blue_link/data/BRAN3p5/averages/%(avg_period)dmonthly/salt/',
                'output_filename': '%(product_str)s_%(avg_period)dmthavg_%(date_str1)s_%(date_str2)s.nc4',
                'avg_periods': [3, 6, 12]},
             'BRAN_u':{
                'product_str': 'bran3.5',
                'start_year': 1993,
                'start_month': 1,
                'end_year': 2012,
                'end_month': 7,
                'input_dir': '/data/blue_link/data/BRAN3p5/monthly/u/',
                'input_filename': 'u_%(year)04d_%(month)02d.nc4',
                'output_dir': '/data/blue_link/data/BRAN3p5/averages/%(avg_period)dmonthly/u/',
                'output_filename': '%(product_str)s_%(avg_period)dmthavg_%(date_str1)s_%(date_str2)s.nc4',
                'avg_periods': [3, 6, 12]},
             'BRAN_v':{
                'product_str': 'bran3.5',
                'start_year': 1993,
                'start_month': 1,
                'end_year': 2012,
                'end_month': 7,
                'input_dir': '/data/blue_link/data/BRAN3p5/monthly/v/',
                'input_filename': 'v_%(year)04d_%(month)02d.nc4',
                'output_dir': '/data/blue_link/data/BRAN3p5/averages/%(avg_period)dmonthly/v/',
                'output_filename': '%(product_str)s_%(avg_period)dmthavg_%(date_str1)s_%(date_str2)s.nc4',
                'avg_periods': [3, 6, 12]}
            }

    def process(self, dataset):
        """
        Calculate multi-month averages for the dataset specified by the input argument.
        """

        self.ncea_path = '/srv/map-portal/usr/bin/ncea'
        self.ncflint_path = '/srv/map-portal/usr/bin/ncflint'

        # Settings for each dataset
        settings = self.config[dataset]
        start_year = settings['start_year']
        start_month = settings['start_month']
        end_year = settings['end_year']
        end_month = settings['end_month']

        # Loop through months in date range
        k = 0
        for year in range(start_year, end_year + 1):
            for month in range(1, 12 + 1):
                if (year == start_year) and (month < start_month):
                    continue
                if (year == end_year) and (month > end_month):
                    break

                k += 1
                for avg_period in settings['avg_periods']:
                    if k >= avg_period:
                        self._calc_multimonth_average(settings, year, month, avg_period)

    def get_date_for_last_complete_month(self):
        last_date_to_use = datetime.date.today() + dateutil.relativedelta.relativedelta(days=-5)
        year = last_date_to_use.year
        month = last_date_to_use.month - 1
        if month == 0:
            month = 12
            year -= 1
        end_date = datetime.datetime(year, month, 1)
        return end_date

    def _calc_multimonth_average(self, settings, end_date_year, end_date_month, N):
        """
        Calculate average over N consecutive months that end on the date specified by
        end_date_year and end_date_month.
        """

        # Get months for averaging as (year, month) tuples
        datelist = self._get_months_for_averaging(end_date_year, end_date_month, N)

        input_files = []
        input_files_timestamps = []
        scale_factors = []
        settings['date_str1'] = '%04d%02d' % datelist[0]
        settings['date_str2'] = '%04d%02d' % datelist[-1]
        settings['avg_period'] = N
        preliminary_data_used = False
        if 'input_filename_preliminary' not in settings:
            settings['input_filename_preliminary'] = ''
        if 'output_filename_preliminary' not in settings:
            settings['output_filename_preliminary'] = ''

        # Create list of input files and check if the files exist
        for year, month in datelist:
            settings['year'] = year
            settings['month'] = month
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
            days_in_month = calendar.monthrange(year, month)[1]
            # Weight averages by days in each month
            # Note: division by 30.0 (~average length of a month) helps minimise floating point errors
            scale_factors.append(days_in_month / 30.0)

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

        # Create temporary directory for processing files
        temp_dir = tempfile.mkdtemp(dir=output_dir)

        # The following steps perform a weighted average of the monthly files
        # (weighted by the number of days in each month).

        # Scale input files by number of days in month
        scaled_files = []
        for k in range(len(input_files)):
            input_file_fullpath = input_files[k]
            input_filename = os.path.split(input_file_fullpath)[1]
            scale_factor = scale_factors[k]
            scaled_filename = os.path.splitext(input_filename)[0] + '_scaled.nc'
            scaled_files.append(self._scale_netcdf_file(input_file_fullpath, scale_factor, temp_dir, scaled_filename))

        # Average scaled files
        scaled_avg_filename = os.path.join(temp_dir, 'tmp_scaledavg.nc')
        cmd = self.ncea_path + ' -O ' + ' '.join(scaled_files) + ' ' + scaled_avg_filename
        proc = subprocess.call(cmd, shell=True)

        # Scale result by N / days in period
        scale_factor = N / sum(scale_factors)
        self._scale_netcdf_file(scaled_avg_filename, scale_factor, output_dir, output_filename)

        # Remove temporary files
        os.remove(scaled_avg_filename)
        for filename in scaled_files:
            os.remove(filename)

        # Delete temporary directory
        os.rmdir(temp_dir)

    def _scale_netcdf_file(self, input_file_fullpath, scale_factor, output_dir, output_filename):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        output_file_fullpath = os.path.join(output_dir, output_filename)

        cmd = self.ncflint_path + ' -O -w ' + str(scale_factor) + ',0' + ' ' + input_file_fullpath + ' ' + input_file_fullpath + ' ' + output_file_fullpath
        proc = subprocess.call(cmd, shell=True)
        return output_file_fullpath

    def _get_months_for_averaging(self, end_date_year, end_date_month, n_months):
        """
        Get list of consecutive months of length n_months that end on the
        date specified by end_date_year and end_date_month.
            Output argument is a list of tuples in format:
                    [(year1, month1), (year2, month2), ...]
        """
        year_counter = end_date_year
        month_counter = end_date_month
        datelist = []

        for k in range(n_months):
            datelist.append((year_counter, month_counter))
            month_counter = month_counter - 1
            if month_counter == 0:
                month_counter = 12
                year_counter = year_counter - 1

        # Reverse list so dates are in chronological order
        datelist = datelist[::-1]
        return datelist
