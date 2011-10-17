'''
Created on Dec 28, 2009

@author: Stephen
'''

from backup_action import *
from backup_util import generate_log_stamp, open_log, log_string as log
from copy_action import restore_files
from os.path import join as pjoin

def run_restore(backup,restore_point, revision=None):
    backup = unicode(backup)
    restore_point = unicode(restore_point)
    
    db = BackupDB(backup)
    if not db.exists():
        print "No database exists cannot restore. %s" % backup
        return
    
    log_file = pjoin(restore_point,"log.txt")

    open_log(log_file)
    
    db.connect()
    
    time_stamps = db.session.query(BackupHistory).order_by(BackupHistory.revision).all()
    
    log("%s\tDetermining Revision History..." % generate_log_stamp())
    
    revisions = []
    found = False
    for ts in time_stamps:
        revisions.append(ts)
        if revision is ts.revision:
            found = True
            break
    
    if not found and revision is not None:
        log("Revision not valid, valid revisions and timestamps are:")
        for rev in revisions:
            log("%s, %s" %(rev.revision,rev.time_stamp))
    
    log("%s\tBuilding Restore Map..." % generate_log_stamp())
    
    restore_map = { }
     
    for rev in revisions:
        file_query = db.session.query(HistoricFile).filter_by(time_stamp=rev.time_stamp).all()
        time_stamp = rev.time_stamp
        for file in file_query:
            path = file.path
            action = file.action
            if action == "add" or action == "change":
                restore_map[path] = time_stamp
            if action == "removed":
                del restore_map[path]
            if action == "rolled":
                continue
                
    log("%s\tConverting To Time Map...\t" % generate_log_stamp())
    
    time_map = { }
    
    for path in restore_map.keys():
        time_stamp = restore_map.get(path)
        if time_stamp not in time_map.keys():
            time_map[time_stamp] = []
        time_map[time_stamp].append(path)
    
    log("%s\tRestoring Files...\t" % generate_log_stamp())
    
    errors = restore_files(time_map,backup,restore_point)
    
    log("%s\tFile Restoration Complete...\t" % generate_log_stamp())
    
    if errors:
        log("The following errors occurred in file transfer:")
        error_log_path = os.path.join(restore_point,"error-restore.log")
        error_log = open(error_log_path,'w')
        for error in errors:
            log(error)
            error_log.write("%s - %s - %s" % (error[0], error[1], error[2]))
            error_log.write("\n")
    
   
        
