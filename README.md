3D Vegetation Lab plugin(s) for the ESA BEAM toolkit
=======================================

This repository contains plugin modules developed by Netcetera Zurich for version 4.10 of the ESA BEAM Earth Observation Toolbox and Development Platform.

* [ESA BEAM toolkit](http://www.brockmann-consult.de/cms/web/beam/)
* [3D Vegetation Lab plugin](http://www.geo.uzh.ch/en/units/rsl/research/lidar-remote-sensing-lidarlab/ongoing-projects/3dveglab)

Binary Installation (windows)
------------------------------------------

```dos
rem 1. MANUALLY: Download BEAM  - you have to click to Proceed
start iexplore 'http://www.brockmann-consult.de/cms/web/beam/dlsurvey?p_p_id=downloadportlet_WAR_beamdownloadportlet10&what=software/beam/4.10.3/beam_4.10.3_win32_installer.exe'
rem 2. run installer
beam_4.10.3_win32_installer.exe
rem 3. remove old unpacked auxdata (if it exists)
rd /q /s %HOMEPATH%\.beam\beam-vlab 
rem 4. remove old version of plugin (if it exists)
del /f /q ${HOME}\beam-4.10.3\modules\beam-3dveglab-vlab-*.jar
rem 5. get latest machine-independent java binary of 3dveglab BEAM plugin
cd %HOMEPATH%\beam-4.10.3\modules\ 
echo cd pub/                           >> getvlab-ftpcmds.txt
echo get beam-3dveglab-vlab-LATEST.jar >> getvlab-ftpcmds.txt
echo quit                              >> getvlab-ftpcmds.txt
ftp -s:getvlab-ftpcmds.txt ftp.netcetera.ch
rem 6. run beam 
%HOMEPATH%\beam-4.10.3\bin\visat
rem 7. MANUALLY: start the 3dveglab tool plugin (so it will unpack the module)
rem [Tools/3D Vegetation Lab Processor]
rem 8. get binary snapshots of dependent software (librat, DART, libradtran)
%HOMEPATH%\.beam\beam-vlab\auxdata\replaceWithLatest.bat
```
Binary Installation (linux)
------------------------------------------

```bash
# 1. MANUALLY: Download BEAM  - you have to click to Proceed
firefox 'http://www.brockmann-consult.de/cms/web/beam/dlsurvey?p_p_id=downloadportlet_WAR_beamdownloadportlet10&what=software/beam/4.10.3/beam_4.10.3_linux64_installer.sh'
# 2. run installer
sh beam_4.10.3_linux64_installer.sh
# 3. remove old unpacked auxdata (if it exists)
rm -rf ${HOME}/.beam/beam-vlab 
# 4. remove old version of plugin (if it exists)
rm -f ${HOME}/beam-4.10.3/modules/beam-3dveglab-vlab-*.jar
# 5. get latest machine-independent java binary of 3dveglab BEAM plugin
cd ${HOME}/beam-4.10.3/modules/ && wget ftp://ftp.netcetera.ch/pub/beam-3dveglab-vlab-LATEST.jar
# 6. run beam 
${HOME}/beam-4.10.3/bin/visat
# 7. MANUALLY: start the 3dveglab tool plugin (so it will unpack the module)
# [Tools/3D Vegetation Lab Processor]
# 8. get binary snapshots of dependent software (librat, DART, libradtran)
sh ${HOME}/.beam/beam-vlab/auxdata/replaceWithLatest.sh
```

3D Vegetation Lab Dependent software
-----------------------------------------
The BEAM Vegetation Lab plugin relies on the following 3rd party software, linux64/win32 binary snapshots of which can be obtained by running the replaceWithLatest.sh script above

* [librat (Monte Carlo Ray Tracing library)](http://www2.geog.ucl.ac.uk/~plewis/bpms/src/lib/)
* [DART (Discrete Anisotropic Radiative Transfer)](http://www.cesbio.ups-tlse.fr/us/dart/dart_description.html)
* [libRadtran (library for radiative transfer)](http://www.libradtran.org/)


Build 3D Veglab Plugin from Source 
------------------------------------------
You should be able to make any changes to the plugin you need by editing the [VLabImpl.py](https://raw.github.com/netceteragroup/esa-beam/master/beam-3dveglab-vlab/src/main/resources/auxdata/VLabImpl.py) jython implementation that will have been placed in your BEAM auxdata directory ($HOME/.beam/beam-vlab/auxdata/VLabImpl.py) and restarting the BEAM application. However, if you'd like to recreate the entire Java development environment needed for an official build, you can follow these steps (for Fedora linux). 

**This block for creating a virtual image is OPTIONAL**
```bash
# OPTIONAL - this is used to create a Fedora linux virtual image so that you canbe sure that the build environment setup script below works unmodified 
wget https://raw.github.com/netceteragroup/esa-beam/master/beam-3dveglab-vlab/src/main/scripts/build_fedora_virtual_image.sh
# build the virtual image (side-effect - f17-xfce-dev will be ready to start in VirtualBox)
sh build_fedora_virtual_image.sh
# start up the virtual machine you just created
VirtualBox --startvm f17-xfce-dev
# now login to the virtual machine and execute the commands below...
# if you ssh into it, it is easier to copy/paste from this window :-)
# ssh -Y fedora@localhost -p 2222

```

```bash
# 1. Get the BEAM development env setup script (Fedora 64bit linux)
# This script automates the steps described here http://www.brockmann-consult.de/beam-wiki/display/BEAM/Build+from+Source
wget https://raw.github.com/netceteragroup/esa-beam/master/beam-3dveglab-vlab/src/main/scripts/build_beam_binaries.sh 
# 2. run it
sh build_beam_binaries.sh
# 3. Get development env setup script for this plugin (Fedora 64bit linux)
wget https://raw.github.com/netceteragroup/esa-beam/master/beam-3dveglab-vlab/src/main/scripts/build_beam_vlab_binaries.sh
# 4. run it
sh build_beam_vlab_binaries.sh
# Follow the commented out manual instructions at the end of the build script to finish eclipse configuration
```

Build Dependent Software from Source
------------------------------------------

```bash
# Run this compilation script (Fedora 64bit linux + cross compile for win32 )
wget https://raw.github.com/netceteragroup/esa-beam/master/beam-3dveglab-vlab/src/main/scripts/build_dummy_binaries.sh
sh build_dummy_binaries.sh
# Run this compilation script (Fedora 64bit linux + cross compile for win32 )
wget https://raw.github.com/netceteragroup/esa-beam/master/beam-3dveglab-vlab/src/main/scripts/build_librat_binaries.sh
sh build_librat_binaries.sh
# Run this compilation script (Fedora 64bit linux + cross compile for win32 )
wget https://raw.github.com/netceteragroup/esa-beam/master/beam-3dveglab-vlab/src/main/scripts/build_radtran_binaries.sh
sh build_radtran_binaries.sh
```

BEAM Plugin Contributing Authors
-----------------------------------------
* Daniel Kuekenbrink 
* Joshy Cyriac 
* Marcel Kessler 
* Jason Brazile

License
-----------------------------------------
* [GNU General Public License](http://www.gnu.org/licenses//gpl-3.0-standalone.html)
