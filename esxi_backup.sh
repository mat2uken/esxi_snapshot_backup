#!/bin/sh

set -x

BDIR=/mnt/nas/vmbackups

cd ~/work/esxi_snapshot_backup
fab -f ~/work/esxi_snapshot_backup/fabfile.py backup

cd $BDIR
sudo chown -R ku:ku *
/usr/bin/python3 ~/work/esxi_snapshot_backup/sync_backups.py
