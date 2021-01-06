# -*- coding: utf-8 -*-
"""
Created on Mon Jan  4 15:55:38 2021

@author: John Meluso
"""

import data_manager as dm
import get_params as gp
import numpy as np
import os
import pickle
import sys


def os_setup():
    """Configures the function for the current operating system."""

    if sys.platform.startswith('linux'):

        try:
            outputdir = str(sys.argv[1])
            execnum = int(sys.argv[2])
            run_list = np.arange(100)
        except IndexError:
            sys.exit("Usage: %s outputdir" % sys.argv[0] )

    else:

        outputdir = '../data/test'
        execnum = 2
        run_list = [999999]

    return outputdir, execnum, run_list



def change_filenames(outputdir, execnum, run_list):
    """Renames file case numbers to match their respective indeces."""

    # Get parameters for specified execution
    params = gp.get_params(execnum)

    # Cycle through parameters and runs for this execution number
    for casenum in np.arange(len(params)):
        for runnum in run_list:

            # Build name for specific test
            case_str = f'case{casenum:06}'
            run_str = f'run{runnum:06}'
            file_prefix = outputdir + '/' + case_str + '_' + run_str

            # Check if the file exists
            try:

                # Get file contents
                summary, history = dm.load_data(file_prefix)

                # Get case number from summary
                summary_case = int(summary[0])
                summary_str = f'case{summary_case:06}'

                # Check if case string matches case number
                if not(summary_str == case_str):
                    new_prefix = outputdir + '/' + summary_str + '_' + run_str
                    os.rename(file_prefix + '_summary.csv',
                              new_prefix + '_summary.csv')
                    os.rename(file_prefix + '_history.csv',
                              new_prefix + '_history.csv')
            except IOError:
                print('No ' + file_prefix)


def run_change_filenames():
    outputdir, execnum, run_list = os_setup()
    change_filenames(outputdir, execnum, run_list)


def get_incompletes(outputdir, execnum, run_list):
    """Identifies runs that didn't save data for the specified execution,
    directory, and list of runs."""

    # Get parameters for specified execution
    params = gp.get_params(execnum)

    # Create empty list for parameter combos that didn't run
    leftovers = []
    counts = np.zeros((len(params),2))
    index_case = 0
    index_count = 1
    case_num = -1

    # Cycle through parameters and runs for this execution number
    for case in params:

        case_num += 1

        # Get case for testing
        casenum = case['ind']
        counts[case_num,index_case] = casenum

        for runnum in run_list:

            # Add run number to case info
            case['run'] = runnum

            # Build name for specific test
            case_str = f'case{casenum:06}'
            run_str = f'run{runnum:06}'
            file_prefix = outputdir + '/' + case_str + '_' + run_str

            # Check if the file exists
            try:
                summary, history = dm.load_data(file_prefix)
                counts[case_num,index_count] += 1
            except IOError:
                leftovers.append(case.copy())

    return leftovers, counts


def run_get_incompletes():
    outputdir, execnum, run_list = os_setup()
    leftovers, counts = get_incompletes(outputdir, execnum, run_list)
    pickle.dump(leftovers, open(f'leftovers_exec{execnum:03}.pickle',"wb"))
    np.save(f'counts_exec{execnum:03}.npy',counts)


def load_incompletes(execnum):
    """Loads the incompletes from file."""

    if sys.platform.startswith('linux'):
        save_dir = ''
    else:
        save_dir = '../data/leftovers/'

    return pickle.load(open(save_dir + f'leftovers_exec{execnum:03}.pickle',
                            "rb"))


if __name__ == '__main__':
    run_get_incompletes()



