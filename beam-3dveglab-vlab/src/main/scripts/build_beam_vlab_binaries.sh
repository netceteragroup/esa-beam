#!/bin/sh

#
# assuming you have run build_beam_binaries.sh, run this afterwards
#

set -e

JAVA_HOME=/usr/lib/jvm/java-1.7.0; export JAVA_HOME
PRJ=esa-034-5

P=/home/${USER}/projects/esa-034-5

cd ${P}/beam

git clone git://github.com/netceteragroup/esa-beam.git

ln -s ${P}/beam/esa-beam/beam-3dveglab-vlab ${P}/beam/beam-3dveglab-vlab

cat > beampluginspomxml.patch << EOF
*** ./beam-plugins/pom.xml.orig   2012-12-19 16:14:29.866013086 +0100
--- ./beam-plugins/pom.xml        2012-12-19 16:14:42.208993865 +0100
***************
*** 56,61 ****
          <module>../blue-marble-worldmap</module>
          <module>../globcover-worldmap</module>
          <module>../lib-hdf</module>
      </modules>
  
! </project>
\ No newline at end of file
--- 56,62 ----
          <module>../blue-marble-worldmap</module>
          <module>../globcover-worldmap</module>
          <module>../lib-hdf</module>
+         <module>../beam-3dveglab-vlab</module>
      </modules>
  
! </project>
EOF
patch -b -p0 < beampluginspomxml.patch 

mvn install -DskipTests
mvn eclipse:eclipse

# manual steps...
#
# eclipse -showLocation -data ${HOME}/projects/esa-034-5/beam
#
# Window/Prerferences/Java/Build Path/Classpath Variables/[New] Name: M2_REPO Path: /home/${USER}/.m2/repository
#
# File/Import/General/Existing Projects [Next] [Browse] ${P}/beam [OK]/[Finish]
# this will import 20 or so projects like beam-aastr , ...
# and then build them (again)
#
# You should now be able to do this:
# go to the Java perspective
# select Run/Run Configurations.../Java Application/VISAT  then [RUN]
# 

