#!/usr/bin/env python
"""
Title: uncompress_synched_data.py
Author: Nicholas Summons, n.summons@bom.gov.au
CreationDate: 2012-12-11

Description: Script for uncompressing newly synched daily data files.
             Files are only uncompressed if the files do not already exist
             in the output directory or are out of date.
"""
import os
import sys
import subprocess
import datetime
import dateutil.relativedelta

from ocean.config import get_server_config

class uncompress_synched_data():

    def __init__(self):
        # Settings for each dataseto

        sys_config = get_server_config()

        self.config = \
            {'reynolds':{
                'start_year': 1981,
                'start_month': 9,
                'start_day': 1,
                'input_dir': os.path.join(sys_config.dataDir['reynolds'], 'daily-new/%(year)04d/AVHRR/'),
                'input_filename': 'avhrr-only-v2.%(year)04d%(month)02d%(day)02d.nc.gz',
                'input_filename_preliminary': 'avhrr-only-v2.%(year)04d%(month)02d%(day)02d_preliminary.nc.gz',
                'output_filename': 'avhrr-only-v2.%(year)04d%(month)02d%(day)02d.nc',
                'output_filename_preliminary': 'avhrr-only-v2.%(year)04d%(month)02d%(day)02d_preliminary.nc',
                'output_dir': os.path.join(sys_config.dataDir['reynolds'], 'daily-new-uncompressed/')
                }
            }

    def process(self, dataset):
        settings = self.config[dataset]
        print >> sys.stderr, 'Uncompressing %s data files......' % dataset
        start_date = datetime.date(settings['start_year'], 
                                   settings['start_month'], 
                                   settings['start_day'])
        end_date = datetime.date.today()

        # Get all dates within date range
        delta = 0
        valid_dates = []
        while 1:
            new_date = start_date + dateutil.relativedelta.relativedelta(days=delta)
            if new_date <= end_date:
                valid_dates.append(new_date)
            else:
                break
            delta += 1

        last_date_processed = None
        stats_newfile = 0
        stats_updating = 0
        stats_most_recent = 0
        
        if len(valid_dates) == 0:
            print >> sys.stderr, 'No valid dates for processing.'
            return
        
        # Loop through all valid dates and unzip file
        for date_k in valid_dates:
            settings['year'] = date_k.year
            settings['month'] = date_k.month
            settings['day'] = date_k.day
            
            input_dir = settings['input_dir'] % settings
            input_filename = settings['input_filename'] % settings
            input_filename_preliminary = settings['input_filename_preliminary'] % settings
            input_file = os.path.join(input_dir, input_filename)
            input_file_preliminary = os.path.join(input_dir, input_filename_preliminary)
            
            output_dir = settings['output_dir'] % settings
            output_filename = settings['output_filename'] % settings
            output_filename_preliminary = settings['output_filename_preliminary'] % settings
            output_file = os.path.join(output_dir, output_filename)
            output_file_preliminary = os.path.join(output_dir, output_filename_preliminary)
            
            input_file_exists = os.path.exists(input_file)
            output_file_exists = os.path.exists(output_file)
                        
            if not input_file_exists:
                # If input file does not exist => test whether preliminary files exist instead
                input_file = input_file_preliminary
                input_filename = input_filename_preliminary
                output_file = output_file_preliminary
                output_filename = output_filename_preliminary
                input_file_exists = os.path.exists(input_file)
                output_file_exists = os.path.exists(output_file)
            
            if input_file_exists:
                if output_file_exists:
                    input_file_datestamp = os.path.getmtime(input_file)
                    output_file_datestamp = os.path.getmtime(output_file)
                    if input_file_datestamp > output_file_datestamp:
                        # print >> sys.stderr, 'Overwriting data file with new version: ' + output_filename
                        uncompress_file = True
                        stats_updating += 1
                    else:
                        uncompress_file = False
                        stats_most_recent += 1
                        last_date_processed = date_k
                        continue
                else:
                    # print >> sys.stderr, 'Adding new data file: ' + output_filename
                    uncompress_file = True
                    stats_newfile += 1
            else:
                uncompress_file = False
                if last_date_processed is None:
                    print >> sys.stderr, 'Missing input file: ' + input_filename
                else:
                    print >> sys.stderr, 'New files added: ' + str(stats_newfile)
                    print >> sys.stderr, 'Files updated: ' + str(stats_updating)
                    print >> sys.stderr, 'Files already up-to-date: ' + str(stats_most_recent)
                    print >> sys.stderr, 'Final date processed: ' + str(last_date_processed)
                return

            last_date_processed = date_k
            
            if uncompress_file:
                temp_file = os.path.join(output_dir, input_filename)               
                
                # Copy to output directory and uncompress
                cmd1 = 'cp %s %s' % (input_file, output_dir)               
                cmd2 = 'gunzip -f %s' % (temp_file)
                subprocess.call(cmd1, shell=True)
                subprocess.call(cmd2, shell=True)
