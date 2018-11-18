#!/bin/sh

set -x

BDIR=/mnt/nas/vmbackups
#fab backup

cd $BDIR
sudo chown -R ku:ku *
/usr/bin/python3 ~/work/esxibackup/sync_backups.py
