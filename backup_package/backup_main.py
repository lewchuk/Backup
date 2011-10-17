'''
Created on Dec 20, 2009

@author: Stephen
'''
import os
from backup_action import run_backup
import sys
from optparse import OptionParser

if __name__ == '__main__':

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
