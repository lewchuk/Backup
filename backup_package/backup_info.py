'''

Created Dec 11, 2011

Author: Stephen Lewchuk

'''

from database_action import BackupDB, BackupHistory, BackupInfo

def collect_revisions(db):
    time_stamps = db.session.query(BackupHistory).order_by(BackupHistory.revision).all()
    return[(rev.revision, rev.time_stamp) for rev in time_stamps]

def collect_info(db):
    info = db.session.query(BackupInfo).all()
    return [(pair.property_name, pair.property_value) for pair in info]

def print_revisions(backup):
    backup = unicode(backup)
    db = BackupDB(backup)
    if not db.exists():
        print "No database exists cannot query. %s" % backup
        return

    db.connect()
    print "Bakup Info:"
    for pair in collect_info(db):
        print "%s = %s" % pair

    print "Revision History:"
    for rev in collect_revisions(db):
      print "Rev: %s - %s" % rev

