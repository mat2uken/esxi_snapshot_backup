#!/usr/bin/python3
# coding: utf-8

import os, re

from fabric.api import run
from fabric.api import env

from datetime import datetime
now = datetime.now()
DATEDIR = now.strftime("%Y%m%d")

env.hosts = ["172.16.128.12"]
env.user = "root"
env.key_filename = "~/.ssh/id_ecdsa"
env.shell="/bin/sh -c"

def hello():
    run("echo hello!")

def getallvms():
    res = run("vim-cmd vmsvc/getallvms")
    vms = []
    for line in res.split("\n")[1:]:
        cols = re.split("\s{2,}", line)

        try:
            vms.append(dict(vmid=cols[0], name=cols[1], imgfile=cols[2],
                            guestos=cols[3], version=cols[4]))
        except IndexError as e:
            print("split error: {}".format(line))
            continue

    return vms

def backup():
    create_backup_dir()

    vms = getallvms()
    for vm in vms:
        create_snapshot(vm)
        copy_vmx_file(vm)
        dump_monosparse_image(vm)
        remove_snapshot(vm)

VMFS_PREFIX="/vmfs/volumes/{}"
def create_backup_dir():
    bdir = os.path.join(VMFS_PREFIX.format("nfsnas/vmbackups"), DATEDIR)
    run("mkdir -p {}".format(bdir))

def copy_vmx_file(vm):
    device, relpath = vm['imgfile'].split(' ')

    src = os.path.join(VMFS_PREFIX.format(device[1:-1]), relpath)
    dst = os.path.join(VMFS_PREFIX.format("nfsnas/vmbackups/{}".format(DATEDIR)), vm["name"].replace(" ", "_") + ".vmx")

    print("cp {} {}".format(src, dst))
    run("cp {} {}".format(src, dst))

def dump_monosparse_image(vm):
    device, relpath = vm['imgfile'].split(' ')

    inputfile = os.path.join(VMFS_PREFIX.format(device[1:-1]), relpath.replace(".vmx", ".vmdk"))
    outputfile = os.path.join(VMFS_PREFIX.format("nfsnas/vmbackups/{}".format(DATEDIR)), vm["name"].replace(" ", "_") + ".vmdk")

#    print("vmkfstools -i {} -d monosparse {}".format(inputfile, outputfile))
    run("vmkfstools -i {} -d monosparse {}".format(inputfile, outputfile))

def create_snapshot(vm):
#    print("vim-cmd vmsvc/snapshot.create {} {}".format(vm["vmid"], "for-backup"))
    run("vim-cmd vmsvc/snapshot.create {} {}".format(vm["vmid"], "for-backup"))

def get_snapshot_id(vm):
    res = run("vim-cmd vmsvc/snapshot.get {}".format(vm["vmid"]))

    found = True
    for line in res.split("\n"):
        if not "Snapshot Name" in line:
            if "for-backup" in line:
                found = True
                continue

        if found is True and "Snapshot Id" in line:
            name, val = line[2:].replace(' ', '').split(':')
            return val

def remove_snapshot(vm):
    snapshot_id = get_snapshot_id(vm)
#    print("vim-cmd vmsvc/snapshot.remove {} {}".format(vm["vmid"], snapshot_id))
    run("vim-cmd vmsvc/snapshot.remove {} {}".format(vm["vmid"], snapshot_id))
