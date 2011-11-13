'''
Created: Nov 13 2011

@author: Stephen Lewchuk
@email: stephen.lewchuk@gmail.com

This file is the unified command line refference for the backup program.

'''

import argparse
import os
import __init__ as init

def existing_folder(value):
    if not os.path.isdir(value):
        raise argparse.ArgumentTypeError("%r is not an existing directory" % value)
    return os.path.abspath(value)

def existing_backup(value):
    if not os.path.exists(os.path.join(value, 'backup.db')):
        raise argparse.ArgumentTypeError("%r has no existing backup instance" % value)
    return os.path.abspath(value)

def no_existing_backup(value):
    if os.path.exists(os.path.join(value, 'backup.db')):
        raise argparse.ArgumentTypeError("%r has an existing backup instance" % value)
    return os.path.abspath(value)

def init_backup(args):
    import backup_action
    params = vars(args)
    del params['func']
    backup_action.initiate_backup(**params)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Interface for the backup program.")
    parser.add_argument('--version', action='version', version=init.__version__)
    subparsers = parser.add_subparsers(description='backup actions')

    init_parser = subparsers.add_parser('init', help="initialize a backup", description="creates the settings for a new database which can be used with the other commands.  No backup will be made just the folder and sqlite db.")
    init_parser.add_argument('source', help="folder to backup", type=existing_folder)
    init_parser.add_argument('dest', metavar='destination', help="location store backup", type=no_existing_backup)
    init_parser.add_argument('--exclude', help="a relative path to exlude from the backup", type=str, action="append")
    init_parser.set_defaults(func=init_backup)

    args = parser.parse_args()
    args.func(args)
