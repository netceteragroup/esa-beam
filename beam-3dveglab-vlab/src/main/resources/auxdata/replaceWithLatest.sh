#!/bin/sh
#
# this script replaces current beam-3dveglab-vlab plugin with latest software
#

VLABDIR=${HOME}/.beam/beam-vlab
VLABAUX=${VLABDIR}/auxdata
VLABAUXTMP=${VLABDIR}/tmp-vlab-auxdata.$$

# helps during development 
CACHING=true
CACHEDIR=/tmp

INDEX=ftp://ftp.netcetera.ch/pub/beam-3dveglab-vlab-CKSUMS.txt

VLAB_SHIM=ftp://ftp.netcetera.ch/pub/beam-3dveglab-vlab-0.1-SNAPSHOT-20130110.jar

BIN_LIN_DART=ftp://ftp.netcetera.ch/pub/DART_DART_5_3_5_29c_03_2012_linux64.tar.gz
BIN_WIN_DART=ftp://ftp.netcetera.ch/pub/DART_DART_5_3_5_29c_03_2012_windows32.zip

BIN_LIN_LRAT=ftp://ftp.netcetera.ch/pub/librat_1_3_3_linux64-20121231.tar.gz
BIN_WIN_LRAT=ftp://ftp.netcetera.ch/pub/librat_1_3_3_windows32-20121231.zip

BIN_LIN_LRAD=ftp://ftp.netcetera.ch/pub/libRadtran-1.7_linux64-20121231.tar.gz
BIN_WIN_LRAD=

BIN_LIN_DUMMY=ftp://ftp.netcetera.ch/pub/dummy_linux64-20130103.tar.gz
BIN_WIN_DUMMY=ftp://ftp.netcetera.ch/pub/dummy_windows32-20130103.zip

set -e

fail() { echo "Error: $1"; exit 1; }

dload_unpack() {
  BNAME="`basename $2`"
  echo Downloading/unpacking ${BNAME} ...
  if test -f "$CACHEDIR/$BNAME" -a "${CACHING}" = true ; then
    cp "$CACHEDIR/$BNAME" .
  else
    wget -nv $2
    if $CACHING ; then cp "${BNAME}" "${CACHEDIR}" ; fi
  fi
  if echo $BNAME | grep -q .zip ; then
    unzip -q $BNAME
    NAME=`basename $BNAME .zip`
  elif echo $BNAME | grep -q .tar.gz ; then
    tar -xzf $BNAME
    NAME=`basename $BNAME .tar.gz`
  fi
  rm $BNAME
  mv $NAME $1
  printf "%30s is %s\n" ${1} ${NAME} >> 00_README-versions.txt
}

sanity_check_beam() {
  echo "Sanity check..."
  test -d $VLABDIR -a -w $VLABDIR || fail "$VLABDIR is not writable"
  mkdir -p $VLABAUXTMP
}

config_latest_vlabshim() {
  echo "VLab..."

  cd ${HOME}/beam-4.10.3/modules
  if test ! -d  old; then mkdir old; fi
  mv beam-3dveglab-vlab*.jar old
  wget $VLAB_SHIM

  cd ${VLABAUXTMP}
  dload_unpack dummy_linux64 $BIN_LIN_DUMMY
  dload_unpack dummy_win32   $BIN_WIN_DUMMY
}

config_latest_dart() {
  echo "Dart..."
  cd ${VLABAUXTMP}

  dload_unpack dart_linux64 $BIN_LIN_DART
  dload_unpack dart_win32   $BIN_WIN_DART
}

config_latest_librat() {
  echo "Librat..."
  cd ${VLABAUXTMP}

  dload_unpack bpms_linux64 $BIN_LIN_LRAT
  dload_unpack bpms_win32   $BIN_WIN_LRAT
}

config_latest_radtran() {
  echo "Libradtran..."
  cd ${VLABAUXTMP}

  dload_unpack radtran_linux64 $BIN_LIN_LRAD
  #dload_unpack radtran_win32   $BIN_WIN_LRAD
}

swap_auxdirs() {
  mv ${VLABAUX} ${VLABAUX}-`date -u +%Y%d%mt%H%M%Z` && mv ${VLABAUXTMP} ${VLABAUX}
}

handle_duplicates() {
  sync
  BEFORE=`du -sh "${VLABAUXTMP}"`
  find ${VLABAUXTMP} -type f -size +0c -print0 | xargs -0 md5sum | awk '{
  if ($1 in chksums)
    chksums[$1] = sprintf("%s:%s", chksums[$1], substr($0,35))
  else
    chksums[$1] = substr($0,35)
}
END {
  for (cksum in chksums) 
    if ((n = split(chksums[cksum],paths,":")) > 1) {
      printf("echo linking %d duplicates of %s\n", n, paths[1])
      for (p in paths) 
        if (p > 1) 
          printf("rm \"%s\" && ln \"%s\" \"%s\"\n", paths[p], paths[1], paths[p])
    }
}' | sh 
  echo "size before linking duplicates: $BEFORE"
  AFTER=`du -sh "${VLABAUXTMP}"`
  echo "size  after linking duplicates: $AFTER"
}
 
sanity_check_beam
config_latest_vlabshim
config_latest_dart
config_latest_librat
config_latest_radtran
handle_duplicates
swap_auxdirs
