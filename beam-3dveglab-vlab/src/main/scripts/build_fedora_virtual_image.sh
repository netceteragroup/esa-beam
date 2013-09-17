#!/bin/sh

INAME=f19-xfce-dev
OS=Fedora_64
IDIR=/var/tmp/images
CFG=${IDIR}/${INAME}.ks
IMAGE=${IDIR}/${INAME}.vdi
ORIGKS=fedora-19-x86_64.ks
CACHE=/var/cache/appcreator

set -e

cd ${IDIR}
wget https://git.fedorahosted.org/cgit/cloud-kickstarts.git/plain/generic/${ORIGKS}

cat > ks-patch.txt <<EOF
--- fedora-19-x86_64.ks	2013-09-17 16:45:54.000000000 +0200
+++ ${INAME}.ks	2013-09-17 16:50:44.030231488 +0200
@@ -1,3 +1,5 @@
+# https://git.fedorahosted.org/cgit/cloud-kickstarts.git/tree/
+#
 # This is a basic Fedora 19 spin designed to work in OpenStack and other
 # private cloud environments. This flavor isn't configured with cloud-init
 # or any other metadata service; you'll need your own say of getting
@@ -26,12 +28,14 @@
 
 
 
-part / --size 10000 --fstype ext4
+part / --size 15360 --fstype ext4
 
 
 # Repositories
 repo --name=fedora --mirrorlist=http://mirrors.fedoraproject.org/mirrorlist?repo=fedora-19&arch=\$basearch
 repo --name=fedora-updates --mirrorlist=http://mirrors.fedoraproject.org/mirrorlist?repo=updates-released-f19&arch=\$basearch
+repo --name=rpmfusion-free --baseurl=http://download1.rpmfusion.org/free/fedora/releases/19/Everything/\$basearch/os/
+repo --name=rpmfusion-free-updates --baseurl=http://download1.rpmfusion.org/free/fedora/updates/19/\$basearch
 
 
 # Package list.
@@ -40,6 +44,15 @@
 %packages --nobase
 @core
 kernel
+@base-x
+@fonts
+@xfce-desktop
+@critical-path-xfce
+shadow-utils
+passwd
+sudo
+vim
+VirtualBox-guest
 
 # We need this image to be portable; also, rescue mode isn't useful here.
 dracut-nohostonly
@@ -81,9 +94,9 @@
 sed -i 's/^timeout 10/timeout 1/' /boot/extlinux/extlinux.conf
 
 # setup systemd to boot to the right runlevel
-echo -n "Setting default runlevel to multiuser text mode"
+echo -n "Setting default runlevel to multiuser graphical mode"
 rm -f /etc/systemd/system/default.target
-ln -s /lib/systemd/system/multi-user.target /etc/systemd/system/default.target
+ln -s /lib/systemd/system/runlevel5.target /etc/systemd/system/default.target
 echo .
 
 # If you want to remove rsyslog and just use journald, remove this!
@@ -171,6 +184,14 @@
 EOF
 fi
 
+echo -n "Installing rpmfusion-free repo"
+rpm -ivh http://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-19.noarch.rpm
+echo .
+
+echo -n "Adding fedora user"
+/sbin/useradd fedora && echo reverse | /bin/passwd fedora --stdin
+echo .
+
 # make sure firstboot doesn't start
 echo "RUN_FIRSTBOOT=NO" > /etc/sysconfig/firstboot
 
@@ -178,11 +199,8 @@
 yum clean all
 truncate -c -s 0 /var/log/yum.log
 
-echo "Zeroing out empty space."
-# This forces the filesystem to reclaim space from deleted files
-dd bs=1M if=/dev/zero of=/var/tmp/zeros || :
-rm -f /var/tmp/zeros
-echo "(Don't worry -- that out-of-space error was expected.)"
+echo "Zeroing out empty space with fstrim."
+/usr/sbin/fstrim /
 
 %end
 
EOF

patch < ks-patch.txt

#ensure that patch created the file we expect
test -f ${ORIGKS}
mv -f ${ORIGKS} ${CFG}

sudo appliance-creator -d -v -t ${IDIR} --config ${CFG} --cache=${CACHE} -o ${IDIR} --name ${INAME} --vmem 512 --vcpu 1 --format raw

sudo chown -R `sudo who am i | cut -d' ' -f1` ${IDIR}

VBoxManage convertdd ${IDIR}/${INAME}/${INAME}-sda.raw ${IMAGE} --format VDI
VBoxManage createvm --name ${INAME} --ostype ${OS} --register --basefolder /var/tmp/images
VBoxManage modifyvm        ${INAME} --memory 1800 --vram 32 --rtcuseutc on --largepages on
VBoxManage storagectl      ${INAME} --name "scsi-ctrl" --add scsi
VBoxManage storageattach   ${INAME} --storagectl "scsi-ctrl" --port 0 --device 0 --type hdd --medium ${IMAGE}
VBoxManage storagectl      ${INAME} --name "ide-ctrl" --add ide
VBoxManage modifyvm        ${INAME} --boot1 dvd --boot2 disk --boot3 none --boot4 none
VBoxManage modifyvm        ${INAME} --natpf1 "guestssh,tcp,,2222,,22"
# VBoxManage export ${INAME} --manifest -o ${IDIR}/${INAME}.ova
# VirtualBox --startvm ${INAME}
