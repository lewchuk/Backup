"""
Created on Nov 13, 2011

@author Stephen Lewchuk
@email stephen.lewchuk@gmail.com

Handles migrating older backups to the latest version
"""

import os

import __init__ as init
import backup_util as util
from database_action import *
import backup_action

def migrate_backup(backup):
    backup = unicode(os.path.abspath(backup))

    db = BackupDB(backup)

    if not db.exists():
        print "Backup database does not exist, cannot migrate"
        return False

    db.connect()

    version_entry = db.session.query(BackupInfo).filter_by(property_name="version").first()
    version = util.split_version_string(version_entry.property_value)

    if version < [0,1,0]:
        backup_action.add_option(db, **{'exclude':[], 'follow_symbolic':True})

    version_entry.property_value = init.__version__
    db.session.commit()
    db.session.close()

