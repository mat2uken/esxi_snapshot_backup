#!/usr/bin/python3
# coding: utf-8

import os
import glob
import shutil
import subprocess

VM_BACKUP_DIR = "/mnt/nas/vmbackups"

def remove_dirs(rm_dirs):
    for d in rm_dirs:
        if not os.path.exists(d):
            print("Directory is not found: {}".format(d))
            continue

        purge_dir_path = "365g:/vmbackups/{}".format(d)
        rclone_cmd = ["/usr/bin/rclone", "purge", purge_dir_path]
        print(rclone_cmd)
        res = subprocess.run(rclone_cmd, stdout=subprocess.PIPE)

        print("rmtree: {}".format(d))
#        shutil.rmtree("{}".format(d))
        subprocess.run(["sudo", "rm", "-rf", d])

def upload_dirs(up_dirs):
    for d in up_dirs:
        if not os.path.exists(d):
            print("Directory is not found: {}".format(d))
            continue

        rclone_cmd = ["/usr/bin/rclone", "copy", d, "365g:/vmbackups/{}".format(d)]
        print(rclone_cmd)
        res = subprocess.run(rclone_cmd, stdout=subprocess.PIPE)

def main():
    os.chdir(VM_BACKUP_DIR)
    dirs = glob.glob("*")
    dirs.sort()

    rm_dirs = dirs[:-3]
    print(rm_dirs)
    remove_dirs(rm_dirs)

    up_dirs = dirs[-3:]
    print(up_dirs)
    upload_dirs(up_dirs)

if __name__ == '__main__':
    main()
