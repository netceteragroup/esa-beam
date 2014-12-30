#!/bin/sh
#
# build libRadtran binaries for linux64 and win32 platforms
#

VERSION=2.0-beta
WINNAME=libRadtran-${VERSION}_windows32-`date +%Y%m%d`
LINNAME=libRadtran-${VERSION}_linux64-`date +%Y%m%d`

set -e

#
# ensure that we have dependent packages
#
sudo yum -y install gcc
sudo yum -y install gcc-gfortran
sudo yum -y install mingw32-gcc
sudo yum -y install mingw32-gcc-gfortran
sudo yum -y install patch
sudo yum -y install elinks
sudo yum -y install flex
sudo yum -y install file

download_code_and_patches() {
  rm -f libRadtran-${VERSION}.tar.gz
  wget -nv http://www.libradtran.org/bin/libRadtran-${VERSION}.tar.gz

  rm -rf patches
  mkdir patches
  cd patches
  for f in `elinks -dump https://github.com/netceteragroup/esa-beam/tree/master/beam-3dveglab-vlab/src/main/scripts/libradtran-patches | egrep 'http.*\.patch'`; do
    p=`basename $f`
    wget -nv "https://raw.github.com/netceteragroup/esa-beam/master/beam-3dveglab-vlab/src/main/scripts/libradtran-patches/$p"
  done
  cd ..
}

unpack_and_patch() {
  tar -xzvf libRadtran-${VERSION}.tar.gz
  cd libRadtran-${VERSION}
  for f in ../patches/libradtran-patch-*; do
    patch -b -p0 < $f
  done
  cd ..
}

build_for_linux() {
  # in case left over from windows build
  for v in CC FC CXX LD AR AS NM STRIP RANLIB DLLTOOL OBJDUMP RESCOMP WINDRES; do
    unset $v
  done

  unpack_and_patch
  cd libRadtran-${VERSION}

  ./configure
  make

  # needed at runtime
  for d in libgfortran.so.3 libquadmath.so.0 libgcc_s.so.1; do
    cp /lib64/$d lib
  done

  cd ..
  mv libRadtran-${VERSION} ${LINNAME}
  tar -czf ${LINNAME}.tar.gz ${LINNAME}

  # now run the tests
  cd ${LINNAME}
  cp -r examples "example files"
  patch -p0 < ../patches/libradtran-tests-example-files.patch
  ln -s data "data files"
  # linux-only patches
  for f in ../patches/libradtran-tests-lin*;do
    patch -b -p0 < $f
  done
  (cd test && make)
}

build_for_windows() {
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

  unpack_and_patch
  cd libRadtran-${VERSION}

  ./configure --prefix=/usr/i686-w64-mingw32 --host=i686-w64-mingw32 --build=x86_64-linux
  make

  # add .exe extension to the win32 executables
  find . -type f -print0 | xargs -0 file | grep PE32 | awk -F: '{printf "mv \"%s\" \"%s.exe\"\n", $1,$1}' | egrep -v  '\.exe$' | sh -x

  # needed at runtime
  for d in libquadmath-0.dll libwinpthread-1.dll libgfortran-3.dll libgcc_s_sjlj-1.dll; do
    cp /usr/i686-w64-mingw32/sys-root/mingw/bin/${d} bin
  done

  cd ..
  mv libRadtran-${VERSION} ${WINNAME}
  zip -r ${WINNAME}.zip ${WINNAME}

  cd ${WINNAME}
  cp -r examples "example files"
  patch -p0 < ../patches/libradtran-tests-example-files.patch
  ln -s data "data files"
  # windows-only patches
  for f in ../patches/libradtran-tests-win*;do
    patch -b -p0 < $f
  done
  (cd test && make)
}

download_code_and_patches
build_for_linux
build_for_windows
