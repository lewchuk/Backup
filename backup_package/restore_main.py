'''
Created on Jan 28, 2010

@author: Stephen
'''

from restore_action import run_restore

if __name__ == '__main__':
    restore_point = "E:\\Stephen\\Restore_Doc1"
    backup = "S:\\Backup\\Backup_Docs"
    run_restore(backup,restore_point)
