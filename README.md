3D Vegetation Lab plugin(s) for the ESA BEAM toolkit
=======================================

This repository contains plugin modules developed by Netcetera Zurich for version 4.10 of the ESA BEAM Earth Observation Toolbox and Development Platform.

* [ESA BEAM toolkit](http://www.brockmann-consult.de/cms/web/beam/)
* [3D Vegetation Lab plugin](http://www.geo.uzh.ch/en/units/rsl/research/lidar-remote-sensing-lidarlab/ongoing-projects/3dveglab)

Binary Installation
---------------------------

Binary installation of the 3D Vegetation Lab plugin involves
 * copying/replacing the plugin jar file in the beam/modules directory
 * clean/first time plugin run to create/unpack .beam/beam-vlab/auxdata/
 * fetch/unpack latest versions of dependent 3rd party software into auxdata
 * create command line wrappers in the bin directory for batch operation

These were handled by complicated .bat (win32) and shell (linux64) scripts.
The process is now easier and more robust as a command-line java app.

Binary Installation (windows version)
------------------------------------------

```dos
rem 1. MANUALLY: Download BEAM  - you have to click to Proceed
press Windows-R  to get the "run" prompt
iexplore "http://www.brockmann-consult.de/cms/web/beam/dlsurvey?p_p_id=downloadportlet_WAR_beamdownloadportlet10&what=software/beam/4.10.3/beam_4.10.3_win32_installer.exe"
rem 2. run installer
beam_4.10.3_win32_installer.exe
rem 3. go to the beam bin directory (the directory where you just installed it)
press Windows-R to get the "run" prompt 
cmd /K "cd /d C:\ProgramFiles(x86)\beam-4.10.3\bin"
rem 4. download the 3DVegLabInstaller.jar into the bin directory from step 3.
start iexplore "ftp://ftp.netcetera.ch/pub/"
rem 5. run the 3DVegLabInstaller.jar from inside the bin directory 
press Windows-R to get the "run" prompt
cmd /K "cd /d C:\Program Files(x86)\beam-4.10.3\bin"
java -jar 3DVegLabInstaller.jar
```
Binary Installation (linux version)
------------------------------------------

```bash
# 1. MANUALLY: Download BEAM  - you have to click to Proceed
firefox 'http://www.brockmann-consult.de/cms/web/beam/dlsurvey?p_p_id=downloadportlet_WAR_beamdownloadportlet10&what=software/beam/4.10.3/beam_4.10.3_linux64_installer.sh'
# 2. run installer
sh beam_4.10.3_linux64_installer.sh
# 3. go to the beam bin directory (the directory where you just installed it)
cd ${HOME}/beam-4.10.3/bin
# 4. download 3DVegLabInstaller.jar into the bin directory from step 3.
wget ftp://ftp.netcetera.ch/pub/3DVegLabInstaller.jar
# 5. run the 3DVegLabInstall.jar from inside the bin directory
java -jar 3DVegLabInstaller.jar
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
