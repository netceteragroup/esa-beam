#!/bin/sh
#
# this script builds librat native binaries for win32 and linux64 platforms
#

VERSION=1_3_3
WINNAME=librat_${VERSION}_windows32-`date +%Y%m%d`
LINNAME=librat_${VERSION}_linux64-`date +%Y%m%d`

sudo yum -y install mingw32-gcc
sudo yum -y install patch

# get official configure
wget http://www2.geog.ucl.ac.uk/~plewis/librat/configure

# get Netcetera patches for cross-compiling win32 binaries under linux
wget -r -nH --cut-dirs=7 --no-parent --reject="build_librat_binaries.sh" --reject="index.html*" -e robots=off https://raw.github.com/netceteragroup/esa-beam/beam-3dvlab-vlab/src/main/scripts/librat-patches

# apply Netcetera win32 top level patch, then run configure
patch < librat-configure.patch
BPMS=`pwd`/bpms csh -x -f ./configure -mingw32 2>&1 | tee build-win23.log
mv bpms ${WINNAME}
zip -r ${WINNAME} ${WINNAME}
rm -f configure

# get official configure again
wget http://www2.geog.ucl.ac.uk/~plewis/librat/configure
BPMS=`pwd`/bpms csh -x -f ./configure 2>&1 | tee build-linux64.log
mv bpms ${LINNAME}
tar -cf ${LINNAME}.tar ${LINNAME}
gzip -9 ${LINNAME}.tar
