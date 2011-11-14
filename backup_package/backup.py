'''
Created: Nov 13 2011

@author: Stephen Lewchuk
@email: stephen.lewchuk@gmail.com

This file is the unified command line refference for the backup program.

'''

import argparse
import os
import __init__ as init

import backup_action
import migrate_action
import restore_action

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

def run_command(args):
    params = vars(args)
    function = params.pop('func')
    function(**params)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Interface for the backup program.")
    parser.add_argument('--version', action='version', version=init.__version__)
    subparsers = parser.add_subparsers(description='backup actions')

    init_parser = subparsers.add_parser('init', help="initialize a backup", description="creates the settings for a new database which can be used with the other commands.  No backup will be made just the folder and sqlite db.")
    init_parser.add_argument('source', help="folder to backup", type=existing_folder)
    init_parser.add_argument('dest', metavar='destination', help="location store backup", type=no_existing_backup)
    init_parser.add_argument('--exclude', help="an absolute path to exlude from the backup", type=str, action="append", default=[])
    init_parser.add_argument('--follow_symbolic', help="instruct backups to follow symbolic links in source directory", action="store_true", default=False)
    init_parser.set_defaults(func=backup_action.initiate_backup)

    migrate_parser = subparsers.add_parser('migrate', help='migrate a backup', description="if possible updates a backup to the version compatible with this script.")
    migrate_parser.add_argument('backup', help='location of backup instance', type=existing_backup)
    migrate_parser.set_defaults(func=migrate_action.migrate_backup)

    backup_parser = subparsers.add_parser('backup', help='execute a backup', description='runs a backup of the root directory for this backup.')
    backup_parser.add_argument('dest', metavar='backup', help='location of backup instance', type=existing_backup)
    backup_parser.add_argument('--dry_run', help='will go through the motions of a backup without actually copying files or modifying the database.', action='store_true')
    backup_parser.add_argument('--force', help='will ignore problems left over in previous backups', action='store_true')
    backup_parser.set_defaults(func=backup_action.run_backup)

    args = parser.parse_args()
    run_command(args)
