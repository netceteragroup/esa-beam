#!/bin/sh
#
# build radtran binaries
#

VERSION=1.7
WINNAME=libRadtran-${VERSION}_windows32-`date +%Y%m%d`
LINNAME=libRadtran-${VERSION}_linux64-`date +%Y%m%d`

set -e

sudo yum -y install mingw32-gcc
sudo yum -y install mingw32-gcc-gfortran
sudo yum -y install patch
sudo yum -y install elinks
sudo yum -y install flex

wget http://www.libradtran.org/bin/history/libRadtran-${VERSION}.tar.gz
tar -xzvf libRadtran-${VERSION}.tar.gz
cd libRadtran-${VERSION}
./configure
make

for d in libgfortran.so.3 libquadmath.so.0 libgcc_s.so.1; do
  cp /lib64/$d lib
done

cd ..
mv libRadtran-${VERSION} ${LINNAME}
tar -czf ${LINNAME}.tar.gz ${LINNAME}

     CC=i686-w64-mingw32-gcc
     FC=i686-w64-mingw32-gfortran
    CXX=i686-w64-mingw32-c++
     LD=i686-w64-mingw32-ld
     AR=i686-w64-mingw32-ar
     AS=i686-w64-mingw32-as
     NM=i686-w64-mingw32-nm
  STRIP=i686-w64-mingw32-strip
 RANLIB=i686-w64-mingw32-ranlib
DLLTOOL=i686-w64-mingw32-dlltool
OBJDUMP=i686-w64-mingw32-objdump
RESCOMP=i686-w64-mingw32-windres
WINDRES=i686-w64-mingw32-windres

tar -xzvf libRadtran-${VERSION}.tar.gz
cd libRadtran-${VERSION}

# get Netcetera patches for cross-compiling win32 binaries under linux
for f in `elinks -dump https://github.com/netceteragroup/esa-beam/tree/master/beam-3dveglab-vlab/src/main/scripts/libradtran-patches | egrep 'http.*\.patch'`; do
  p=`basename $f`
  wget "https://raw.github.com/netceteragroup/esa-beam/master/beam-3dveglab-vlab/src/main/scripts/libradtran-patches/$p"
  patch -b -p0 < $p
done

./configure --prefix=/usr/i686-w64-mingw32 --host=i686-w64-mingw32 --build=x86_64-linux

make
# add .exe extension to the win32 executables
find . -type f -print0 | xargs -0 file | grep PE32 | awk -F: '{printf "mv \"%s\" \"%s.exe\"\n", $1,$1}' | egrep -v  '\.exe$' | sh -x

for d in libquadmath-0.dll libwinpthread-1.dll libgfortran-3.dll libgcc_s_sjlj-1.dll; do
  cp /usr/i686-w64-mingw32/sys-root/mingw/bin/${d} bin
done

cd ..
mv libRadtran-${VERSION} ${WINNAME}
zip -r ${WINNAME}.zip ${WINNAME}

