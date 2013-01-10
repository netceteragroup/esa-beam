#!/bin/sh
#
# build dummy native binaries for testing the vlab shim
#

WINNAME=dummy_windows32-`date +%Y%m%d`
LINNAME=dummy_linux64-`date +%Y%m%d`

set -e

sudo yum -y install mingw32-gcc

wget https://raw.github.com/netceteragroup/esa-beam/beam-3dvlab-vlab/src/main/c/dummy.c

mkdir -p ${WINNAME}
mkdir -p ${LINNAME}

gcc -o ${LINNAME}/dummy dummy.c

i686-w64-mingw32-gcc -o ${WINNAME}/dummy.exe dummy.c
