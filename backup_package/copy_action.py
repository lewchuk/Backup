'''
Created on Dec 21, 2009

@author: Stephen
'''

from shutil import copy2
import os
from sys import stdout
from os.path import getsize as getfsize, join as pjoin
from backup_util import determine_size, log_string as log

def copy_relative(relative_paths, source, dest, debug=True, dry_run=False):
    """ Copies a set of relative files from the source folder to the
    destination folder.  Will create any necessary folders.

    relative_paths An array of file names to be copies.

    source The source folder to copy from.

    dest The destination folder to copy to.

    debug Should a progress indicator be displayed.

    """

    errors = []

    length = len(relative_paths)
    count = 0
    text = "%d / %d" % (count,length)
    stdout.write(text)


    for file in relative_paths:

        try:
            source_path = os.path.join(source,file)
            dest_path = os.path.join(dest,file)
            dest_folder = os.path.split(dest_path)[0]
            if not os.path.exists(dest_folder):
                os.makedirs(dest_folder)

            if not dry_run:
                copy2(source_path,dest_path)
            size = getfsize(os.path.join(source,file))
            log("%s\t%s\t%s" % (file,determine_size(size),size), False)
        except Exception, e:
            errors.append((source_path,dest_path,e))

        count = count + 1
        backup = '\b'*len(text)
        stdout.write(backup)
        text = "%d / %d" % (count,length)
        stdout.write(text)

    stdout.write("\n")
    return errors

def restore_files(files_map,source,dest):
    """ Restores files from the source directory to the destination
    directory.  The source directory is split into different buckets.

    files_map A map of source buckets to relative path.

    source The source directory.

    dest The destination directory.

    """

    errors = []

    for bucket in files_map.keys():
        source_path = os.path.join(source,bucket)
        sub_error = copy_relative(files_map[bucket],source_path,dest)
        if sub_error:
            errors.extend(sub_error)

    return errors


