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
    