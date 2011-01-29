'''
Created on Nov 26, 2010

@author: Stephen
'''

from os.path import join as pjoin, getsize as getfsize
from database_action import *
from backup_util import open_log, log_string as log, close_log, determine_size
from copy_action import copy_relative


def rollback_backup(dest, force=False):
    dest = unicode(os.path.normpath(dest))
    
    db = BackupDB(dest)
    if db.exists():
        db.connect()
        last_backup = db.session.query(BackupHistory).order_by(BackupHistory.revision.desc()).first()
        if last_backup.in_progress and not force:

            message = "Backup: %s\nLast Backup: %s\nIt appears an error occurred during the last backup.\n" +\
              "Please run fixup_backup to correct the problem before rolling back.\n"+ \
              "This issue can be ignored by using the force=True option\n\n"
            print message % (dest,last_backup.time_stamp)
            return False
    else:
        print "No database exists at given location: %s" % dest
        return
    
    print "Requesting latest backup information..."
   
    last_actions = db.session.query(HistoricFile).filter_by(time_stamp=last_backup.time_stamp)

    destination = pjoin(dest,last_backup.time_stamp)
    num = 1;
    log_file = pjoin(destination,"log-rollback1.txt")
    while os.path.exists(log_file):
        num += 1
        log_file = pjoin(destination,"log-rollback%d.txt" % num)
        
    
    open_log(log_file)
    
    log("Requesting latest backup information...", False)
    log("Rolling Back most recent backup...\n\tRevision: %s Timestamp: %s" % (last_backup.revision, last_backup.time_stamp))
    
    for a_file in last_actions.all():
        
        if a_file.action == "add":
            cur = db.session.query(CurrentFile).filter_by(path = a_file.path)
            db.session.delete(cur)
            log("Removing new file entry: %s" % a_file.path,False)
        elif a_file.action == "removed":
            previous = db.session.query(HistoricFile).filter(HistoricFile.path == a_file.path).filter(HistoricFile.time_stamp != last_backup.time_stamp).order_by(HistoricFile.time_stamp.desc()).first()
            cur = CurrentFile(a_file.path,previous.time_stamp)
            db.session.add(cur)
            log("Rolling back deleted file entry: %s" % a_file.path,False)
        elif a_file.action == "changed":
            previous = db.session.query(HistoricFile).filter(HistoricFile.path == a_file.path).filter(HistoricFile.time_stamp != last_backup.time_stamp).order_by(HistoricFile.time_stamp.desc()).first()
            old = db.session.query(CurrentFile).filter_by(path = a_file.path)
            db.session.delete(old)
            cur = CurrentFile(a_file.path,previous.time_stamp)
            db.session.add(cur)
            log("Rolling back changed file entry: %s" % a_file.path,False)
        a_file.action = "rolled"
        
    log("Finished Rollingback backup")
    last_backup.in_progress = False
    last_backup.was_fixed = True
    db.session.commit()
    db.session.close()
    close_log()

