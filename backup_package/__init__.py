r"""
Backup is a python implementation of an incremental backup program.  It uses
an sqlite database to keep track of files in the backup and backup settings.

A command line interface is available through backup.py

The major functions are init, backup and restore.

init is located in backup_action.initialize_backup.

backup is located in backup_action.run_backup.

restore is located in restore_action.run_restore.

Other operations include modify_backup, fixup and rollback.
"""
__version__ = "0.1.0"
