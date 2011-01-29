'''
Created on May 29, 2010

@author: Stephen
'''

from os.path import join as pjoin, getsize as getfsize
from database_action import *
from backup_util import open_log, log_string as log, close_log, determine_size
from copy_action import copy_relative


def fixup_backup(source,dest,complete_transfer=False):
    source = unicode(os.path.normpath(source))
    dest = unicode(os.path.normpath(dest))
    
    db = BackupDB(dest)
    if db.exists():
        db.connect()
    else:
        print "No database exists at given location: %s" % dest
        return
    
    print "Requesting latest backup information..."
    
    last_update = db.session.query(BackupHistory).order_by(BackupHistory.revision.desc()).first()
    last_files = db.session.query(CurrentFile).filter_by(time_stamp=last_update.time_stamp)

    destination = pjoin(dest,last_update.time_stamp)
    num = 1;
    log_file = pjoin(destination,"log-fix1.txt")
    while os.path.exists(log_file):
        num += 1
        log_file = pjoin(destination,"log-fix%d.txt" % num)
        
    
    open_log(log_file)
    
    log("Requesting latest backup information...", False)
    log("Analysing most recent backup...\n\tRevision: %s Timestamp: %s" % (last_update.revision, last_update.time_stamp))
    
    needs_fixing = []
    
    for a_file in last_files.all():
        full_path = os.path.join(destination,a_file.path)
        if not os.path.exists(full_path):
            needs_fixing.append((a_file,full_path))
    
    if needs_fixing:
        log("%d files need fixing in this backup." % len(needs_fixing))
    else:
        log("No errors detected in latest backup.")
        last_update.in_progress = False
        db.session.commit()
        db.session.close()
        close_log()
        return

    if complete_transfer:
        finish_backup(source,destination,needs_fixing,db,last_update, num)
    else:
        roll_back_files(needs_fixing,db,last_update)

    log("Finished fixing backup")
    last_update.in_progress = False
    last_update.was_fixed = True
    db.session.commit()
    db.session.close()
    close_log()

def roll_back_files(needs_fixing,db,last_update):
    log("Preparing to roll back files")
    for a_file in needs_fixing:
        historic = db.session.query(HistoricFile).filter_by(time_stamp=last_update.time_stamp,path=a_file[0].path).one()
        db.session.delete(a_file[0])
        if historic.action == 'change':
            log("Rolled back: %s" % a_file[0].path, False)
            all_historic = db.session.query(HistoricFile).filter_by(path=a_file[0].path).order_by(HistoricFile.time_stamp.desc()).all()
            previous = all_historic[1]
            new_entry = CurrentFile(previous.path,previous.time_stamp)
            db.session.add(new_entry)
        else:
            log("Deleted entry: %s" % a_file[0].path, False)
        db.session.delete(historic)
        

def finish_backup(source,destination,needs_fixing,db, last_update, num):
    to_copy = []
    
    log("Preparing to copy files...")
    
    size = 0.0

    for a_file in needs_fixing:
        f_source = pjoin(source,a_file[0].path)
        if os.path.exists(f_source):
            to_copy.append(a_file[0].path)
            size += getfsize(f_source)
            log("Need to copy: %s" % f_source, False)
        else:
            log("File no longer exists: %s" % f_source, False)
            historic = db.session.query(HistoricFile).filter_by(time_stamp=last_update.time_stamp,path=a_file[0].path).one()
            if historic.action == 'add':
                db.session.delete(historic)
            elif historic.action == 'change':
                historic.action = 'fixed'
            else:
                log("Error: unexpected historic action: %s" % historic.action)
                log("Cannot fix file: %s" % f_source)
                continue
            db.session.delete(a_file[0])
    
    collapsed_size = determine_size(size)
    
    if not to_copy:
        log("All files to fix no longer exist")
        return
    else:
        log("Fixing %d files..." % len(to_copy))
        log("Transfering %s (%d bytes) to backup" % (collapsed_size, size))
        print "Beginning File Transfer..."
        
        errors = copy_relative(to_copy,source,destination)
        if errors:
            error_log_path = pjoin(destination,"error-fix%d.log" % num)
            error_log = open(error_log_path,'w')
            log("See %s for details." % ("error-fix%d.log" % num))
            log("The following errors occurred in file transfer:")
            for error in errors:
                print error
                error_log.write("%s - %s - %s" % (error[0], error[1], error[2]))
                error_log.write("\n")
    