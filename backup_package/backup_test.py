'''
Created on Apr 26, 2010

@author: Stephen
'''


from backup_action import run_backup,modify_backup
from fixup import fixup_backup
from rollback import rollback_backup

if __name__ == '__main__':
    #source = "E:\\"
    #dest = "S:\\Backup\\Backup_E"
    #modify_backup(dest,exclude = ["Downloads\Deluge"])
    #fixup_backup(source,dest)

    source = "D:\\"
    dest = "S:\\Backup\\Backup_D"
    rollback_backup(dest)
    raw_input("Press any key to continue...")
