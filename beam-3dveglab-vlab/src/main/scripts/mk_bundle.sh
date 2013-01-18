#!/bin/sh
XTMPDIR=`date +/tmp/tmp-%Y%m%d-%H.%M`

set -e

mkdir $XTMPDIR
cd $XTMPDIR
wget -q -r -nH --cut-dirs=1 --no-parent ftp://ftp.netcetera.ch/pub/

mkentry() {
  type=$1
  globpat=$2

  for f in `ls -t $globpat | head -1`; do
    sum=`md5sum $f | awk '{print $1}'`
    printf "%s:%s:%s\n" $sum $type $f 
  done
}

mkentry modules 'beam-3dveglab*.jar'
mkentry aux     'dummy_linux*'
mkentry aux     'dummy_win*'
mkentry aux     'librat*linux*'
mkentry aux     'librat*win*'
# mkentry aux     'libRat*lin*'

rm -rf $XTMPDIR
