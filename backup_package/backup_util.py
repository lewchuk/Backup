'''
Created on Dec 22, 2010

@author: Stephen
'''

from datetime import datetime

def generate_time_stamp(time = None):
    if not time:
        time = datetime.now()
    time_stamp = time.strftime('%Y%m%d%H%M%S')
    return time_stamp 

def generate_log_stamp():
    now = datetime.now()
    time_stamp = now.strftime('%Y/%m/%d %H:%M:%S')
    return time_stamp
    
def determine_size(size):
    endings = ["B","KB","MB","GB","TB"].__iter__()
    size = float(size)
    ending = endings.next()
    try:
        while size > 1024:
            ending = endings.next()
            size = size / 1024
    except StopIteration:
        pass
    return "%.3f %s" % (size,ending)

global log

def open_log(path):
    global log
    log = open(path,'w')
    
def log_string(string, print_it = True):
    log.write("%s\n" % string.encode('utf-8'))
    if print_it:
        print string
    
def close_log():
    log.close()

def split_version_string(ver_str):
  return [int(part) for part in ver_str.split('.')]

def compare_version_strings(db_version, script_version):
  db_ver = split_version_string(db_version)
  sc_ver = split_version_string(script_version)

  migrate_msg = """Backup created with old version of scripts, please 'python backup.py """ \
                """migrate' on this database.\nScript version: %s\nBackup version: %s"""

  upgrade_msg = """Backup created with a new version of scripts, please download the """ \
                """lastest version of the scripts.\nScript version: %s\nBackup version: %s"""

  if db_ver < [0,0,3] or db_ver[0:2] < sc_ver[0:2]:
    print migrate_msg % (script_version, db_version)
    return False
  if db_ver[0:2] > sc_ver[0:2]:
    print upgrage_msg % (script_version, db_version)
    return False

  return True
