'''
Created on Dec 22, 2009

@author: Stephen
'''

from backup_util import generate_time_stamp, generate_log_stamp, determine_size, open_log, close_log
from backup_util import log_string as log
from database_action import *
from os.path import join as pjoin
from os.path import getsize as getfsize
from datetime import datetime
from copy_action import copy_relative
import simplejson

version = "0.0.3"
""" Changes at x.x.x indicate minor ungrades which will not require any migration except updating scripts.
    Changes at x.x indicate significant upgrades which will require migration.
    Changes at x indicate major upgrades, may not be compatible with previous versions.
"""

def  initiate_backup(source,dest,**options):
    """ Creates a backup system for the source to destination directory.
        Creates an folder with all source code in the destination to execute the backup.
        Creates a custom script to run the backup.

        source - The source directory
        dest - The destination directory
        options - A series of keyword arguments to for setting up the backup
            Supported are:
                exclude = [path,path] - where path are paths to exclude from the backup
    """

    source = unicode(os.path.normpath(source))
    dest = unicode(os.path.normpath(dest))

    db = BackupDB(dest)

    if db.exists():
        message = "Backup database already exists at the specified " + \
              "destination.\nCannot create backup"
        print message
        return False

    db.create(source)

    info_version = BackupInfo('version',version)
    db.session.add(info_version)

    add_option(db, **options)

    db.session.commit()
    db.session.close()

    print "Database Created at %s" % dest

    """TODO: Create executable package here.  """

    return True

def add_option(db, **options):

    if 'exclude' in options:
        excluded = options['exclude']
        uni_excl = []
        for excl in excluded:
            uni_excl.append(unicode(os.path.normpath(excl)))

        exclude_entry = db.session.query(BackupInfo).filter_by(property_name="exclude").first()
        if not exclude_entry:
            exclude_entry = BackupInfo('exclude','[]')
            db.session.add(exclude_entry)

        existing = simplejson.loads(exclude_entry.property_value)
        existing.extend(uni_excl)

        json_str = simplejson.dumps(existing)
        exclude_entry.property_value = json_str
        db.session.commit()

def modify_backup(destination,**options):
    dest = unicode(os.path.normpath(destination))
    db = BackupDB(dest)

    if not db.exists():
        print "No database to modify"

    db.connect()
    add_option(db,**options)

    db.session.commit()
    db.session.close()

def run_backup(source,dest,force=False, dry_run=False):
    """ Runs a backup of the source directory to the destination directory

    source The source for the backup.

    dest The destination for the backup.

    """

    source = unicode(os.path.normpath(source))
    dest = unicode(os.path.normpath(dest))

    time_stamp = generate_time_stamp()

    db = BackupDB(dest)
    if db.exists():
        db.connect()
        last_backup = db.session.query(BackupHistory).order_by(BackupHistory.revision.desc()).first()
        if last_backup.in_progress and not force:

            message = "Backup: %s\nLast Backup: %s\nIt appears an error occurred during the last backup.\n" +\
              "Please run fixup_backup to correct the problem.\n"+ \
              "This issue can be ignored by using the force=True option\n\n"
            print message % (dest,last_backup.time_stamp)
            return False
    else:
        print "No backup database exists. Please run initiate_backup()."
        return False

    version_entry = db.session.query(BackupInfo).filter_by(property_name="version").first()
    ver_str = version_entry.property_value
    if ver_str[0:ver_str.rfind('.')] != version[0:ver_str.rfind('.')]:
        message = "The version of the backup script you are using is not compatibale\n" +\
            "with the backup database. Please determine if a migration script exists\n" + \
            "or find an onlder version of the scripts to run with this database."
        print message
        print "Database version: %s, script version: %s" % (ver_str,version)
        return False
    elif ver_str != version:
        version_entry.property_value = version

    exclude_entry = db.session.query(BackupInfo).filter_by(property_name="exclude").first()
    if not exclude_entry:
        excluded = []
    else:
        excluded = simplejson.loads(exclude_entry.property_value)

    print "Excluding: %s" % excluded

    if not dry_run:
        db.create_backup_session(time_stamp)

    added = changed = removed = 0

    destination = pjoin(dest,time_stamp)
    os.mkdir(destination)
    log_file = pjoin(destination,"log.txt")

    open_log(log_file)
    if dry_run:
        log("This is a dry run only, no backup was made")

    log("Starting Backup\t%s" % generate_log_stamp())
    log("Backup root: %s" % source)
    log("Backup dest: %s" % dest)
    log("Timestamp: %s" % time_stamp)
    print "Beginning Root Analysis...\n"

    files = []

    collect_files(source,'',files,excluded = excluded,dry_run = dry_run)

    size = 0.0
    copy_files = []

    for file in files:
        entry = db.session.query(CurrentFile).filter_by(path=file).first()
        if not entry:
            copy_files.append(file)
            if not dry_run:
                historic_entry = HistoricFile(file,time_stamp,'add')
                db.session.add(historic_entry)
                current_entry = CurrentFile(file,time_stamp)
                db.session.add(current_entry)
            added = added + 1
            size += getfsize(pjoin(source,file))

        else:
            last_backup = entry.time_stamp
            last_edit_time = os.path.getmtime(pjoin(source,file))
            last_edit = generate_time_stamp(datetime.fromtimestamp(last_edit_time))
            if last_edit > last_backup:
                copy_files.append(file)
                if not dry_run:
                    historic_entry = HistoricFile(file,time_stamp,'change')
                    db.session.add(historic_entry)
                    entry.time_stamp = time_stamp
                changed = changed + 1
                size += getfsize(pjoin(source,file))

    unchanged = db.session.query(CurrentFile)\
            .filter(CurrentFile.time_stamp != time_stamp)\
            .order_by(CurrentFile.path).all()

    for entry in unchanged:
        rel_path = entry.path
        if not os.path.exists(pjoin(source,rel_path)):
            if not dry_run:
                historic_entry = HistoricFile(rel_path,time_stamp,'removed')
                db.session.add(historic_entry)
                db.session.delete(entry)
            removed = removed + 1


    if not dry_run:
        backup_hist = db.session.query(BackupHistory).filter_by(time_stamp=time_stamp).first()
        backup_hist.num_added = added
        backup_hist.num_changed = changed
        backup_hist.num_removed = removed
        db.session.commit()

    db.session.close()

    print "Finished Analyzing Root\t%s" % generate_log_stamp()
    log("Added: %s" % added)
    log("Changed: %s" % changed)
    log("Removed: %s" % removed)

    collapsed_size = determine_size(size)

    if not copy_files:
        log("No files to transfer backup finished")
    else:
        log("Transfering %s (%d bytes) to backup" % (collapsed_size, size))
        print "Beginning File Transfer..."

        errors = copy_relative(copy_files,source,destination,dry_run = dry_run)
        if errors:
            error_log_path = pjoin(destination,"error-%s.log" % time_stamp)
            error_log = open(error_log_path,'w')
            log("See %s for details." % ("error-%s.log" % time_stamp))
            log("The following errors occurred in file transfer:")
            for error in errors:
                print error
                error_log.write("%s - %s - %s" % (error[0], error[1], error[2]))
                error_log.write("\n")

        print "Finished File Transfer\t%s" % generate_log_stamp()

    if not dry_run:
        db.initialize()
        this_backup = db.session.query(BackupHistory).filter_by(time_stamp=time_stamp).first()
        this_backup.in_progress = False
        db.session.commit()
        db.session.close()
    close_log()

def collect_files(root,source,files,excluded = None, dry_run = False, level = 0):
    excluded = excluded or []

    if source.startswith("$"):
        return
    dirs = []
    path = pjoin(root,source)
    try:
        for f in os.listdir(path):
            fpath = pjoin(path,f)
            norm = unicode(os.path.normpath(fpath))
            if norm in excluded:
                log("Skipping: %s" % fpath)
                continue
            if os.path.isfile(fpath):
                rel_path = os.path.relpath(fpath,root)
                """ This is to deal with a bug in python when
                dealing with roots like C:\ or /
                """
                if os.path.ismount(root) and rel_path.startswith(".."):
                    rel_path = rel_path[3:]
                files.append(rel_path)
            elif os.path.isdir(fpath):
                dirs.append(pjoin(source,f))
    except WindowsError:
        log("Error accessing: %s" % path)
        return
    for dir in dirs:
        collect_files(root,dir,files,excluded = excluded, dry_run = dry_run, level = level + 1)
