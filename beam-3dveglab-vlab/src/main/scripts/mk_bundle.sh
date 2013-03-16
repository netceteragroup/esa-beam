#!/bin/sh
XTMPDIR=`date +/tmp/tmp-%Y%m%d-%H.%M`

set -e

mkdir $XTMPDIR
cd $XTMPDIR
wget -q -r -nH --cut-dirs=1 --no-parent ftp://ftp.netcetera.ch/pub/

mkentry() {
  type=$1
  globpat=$2
  newname=$3

  for f in `ls -t $globpat | head -1`; do
    sum=`md5sum $f | awk '{print $1}'`
    printf "%s:%s:%s:%s\n" $sum $type $f $newname
  done
}

mkentry modules 'beam-3dveglab*.jar'  ''
mkentry aux     'dummy_linux*'        'dummy_lin64'
mkentry aux     'dummy_win*'          'dummy_win32'
mkentry aux     'librat*linux*'       'librat_lin64'
mkentry aux     'librat*win*'         'librat_win32'
mkentry aux     'libRadtran*linux*'   'libRadtran_lin64'
mkentry aux     'libRadtran*win*'     'libRadtran_win32'
mkentry aux     'DART*linux64*'       'dart_lin64'
mkentry aux     'DART*windows32*'     'dart_win32'

rm -rf $XTMPDIR
