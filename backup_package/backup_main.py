'''
Created on Dec 20, 2009

@author: Stephen
'''
import os
from backup_action import run_backup
import sys
from optparse import OptionParser

if __name__ == '__main__':

    """
    TODO: Consider ways to store diffs only, look at xdelta (http://xdelta.org/ - GPL) and bsdiff (http://www.daemonology.net/bsdiff/ - BSD Protection License)
    TODO: Build in move detection, i.e. compare added and removed to try and find identical files, try using filecmp
    TODO: Build a full commandline app
    TODO: Add a collapse command which takes a range of backup instances and removes changes so that only add/remove and a single change (the most recent) are included
            This will be an irreversible action (though the DB entries may remain but with a new flag).  It will be used to reduce the size of a backup when being able to
            restore backups except the most recent is as critical.
    TODO: Add ability to roll backup back up previous version.
    TODO: Document the various abilities.
    TODO: When versions change and not running from backup, copy self to backup
    """
    
    parser = OptionParser(usage="usage: %prog [options]")
    parser.add_option("-d","--directory", action="append", dest="dirs", help="the directories to backup")
    (options,args) = parser.parse_args()
        
    if not options.dirs:
        print "Insufficient directories"
        raw_input("Press any key to continue...")
        exit()
    
    if (os.path.exists("S:\\")):

        for dir in options.dirs:
            if dir == "E":
                source = "%s:\\Stephen\\" % dir
            else:
                source = "%s:\\" % dir
            dest = "S:\\Backup\\Backup_%s" % dir[0]
            run_backup(source,dest)

        raw_input("Press any key to continue...")
    else:
        print "S drive cannot be found cannot backup"
        raw_input("Press any key to continue...")