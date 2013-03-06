#!/bin/sh
NAME=f17-xfce-dev
OS=Fedora_64
IMAGE=/tmp/${NAME}.vmdk
SZMB=1500
INSTDIR=/tmp/boxes/
BUILDDIR=/tmp/builds/

set -e 

sudo yum install -y rubygem-boxgrinder-build

mkdir -p ${BUILDDIR}
cat > ${BUILDDIR}/${NAME}.appl << EOF
name: $NAME
summary: Fedora with xfce
os:
  name: fedora
  version: 17
hardware:
  partitions:
    "/":
      size: 5
packages:
  - @base
  - @base-x
  - @fonts
  - @xfce-desktop
  - @critical-path-xfce
post:
  base:
   - "useradd fedora && echo reverse | passwd fedora --stdin"
   - "echo reverse | passwd root --stdin"
   - "ln -s --force /lib/systemd/system/runlevel5.target /etc/systemd/system/default.target"
EOF

cd ${BUILDDIR}
sudo -E boxgrinder-build --trace -p virtualbox ${NAME}.appl
cp ${BUILDDIR}/build/appliances/x86_64/fedora/17/${NAME}/1.0/virtualbox-plugin/tmp/${NAME}.vmdk ${IMAGE}
VBoxManage createvm --name ${NAME} --ostype ${OS} --register --basefolder ${INSTDIR}
VBoxManage modifyvm ${NAME} --memory ${SZMB} --vram 32
VBoxManage modifyvm ${NAME} --natpf1 "Rule 1,tcp,,2222,,22"
VBoxManage storagectl ${NAME} --name "SATA Controller" --add sata --controller IntelAHCI
VBoxManage storageattach ${NAME} --storagectl "SATA Controller" --type hdd --port 0 --device 0 --medium ${IMAGE}
# VBoxManage export ${NAME} --manifest -o ${BUILDDIR}/${NAME}.ova
# VirtualBox --startvm ${NAME}
