#!/bin/sh
#
# build radtran binaries
#

VERSION=1.7
WINNAME=libRadtran-${VERSION}_windows32-`date +%Y%m%d`
LINNAME=libRadtran-${VERSION}_linux64-`date +%Y%m%d`

set -e

wget http://www.libradtran.org/bin/libRadtran-${VERSION}.tar.gz
tar -xzvf libRadtran-${VERSION}.tar.gz
cd libRadtran-${VERSION}
./configure
make
cd ..
mv libRadtran-${VERSION} ${LINNAME}

