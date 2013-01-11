3D Vegetation Lab plugin(s) for the ESA BEAM toolkit
=======================================

This repository contains plugin modules developed by Netcetera Zurich for version 4.10 of the ESA BEAM Earth Observation Toolbox and Development Platform.

* [ESA BEAM toolkit](http://www.brockmann-consult.de/cms/web/beam/)
* [3D Vegetation Lab plugin](http://www.geo.uzh.ch/en/units/rsl/research/lidar-remote-sensing-lidarlab/ongoing-projects/3dveglab)

Binary Installation
------------------------------------------

```bash
# 1. MANUALLY: Download BEAM  - you have to click to Proceed
firefox 'http://www.brockmann-consult.de/cms/web/beam/dlsurvey?p_p_id=downloadportlet_WAR_beamdownloadportlet10&what=software/beam/4.10.3/beam_4.10.3_linux64_installer.sh'
# or for windows32 ...  
# firefox 'http://www.brockmann-consult.de/cms/web/beam/dlsurvey?p_p_id=downloadportlet_WAR_beamdownloadportlet10&what=software/beam/4.10.3/beam_4.10.3_win32_installer.exe'
# 2. run installer
sh beam_4.10.3_linux64_installer.sh
# 3. get latest machine-independent java binary of 3dveglab BEAM plugin
wget ftp://ftp.netcetera.ch/pub/beam-3dveglab-vlab-LATEST.jar 
# 4. (re)place it in BEAM's modules directory
rm -f ${HOME}/.beam/beam-3dveglab-vlab-*.jar
cp beam-3dveglab-vlab-LATEST.jar ${HOME}/.beam/modules
# 5. run beam 
${HOME}/beam-4.10.3/bin/visat
# 6. MANUALLY: start the 3dveglab tool plugin (so it will unpack the module)
# [Tools/3D Vegetation Lab Processor]
# 7. get binary snapshots of dependent software (librat, DART, libradtran)
sh ${HOME}/.beam/beam-vlab/auxdata/replaceWithLatest.sh
```

3D Vegetation Lab Dependent software
-----------------------------------------
The BEAM Vegetation Lab plugin relies on the following 3rd party software, linux64/win32 binary snapshots of which can be obtained with by running the replaceWithLatest.sh script above

* [librat (Monte Carlo Ray Tracing library)](http://www2.geog.ucl.ac.uk/~plewis/bpms/src/lib/)
* [DART (Discrete Anisotropic Radiative Transfer)](http://www.cesbio.ups-tlse.fr/us/dart/dart_description.html)
* [libRadtran (library for radiative transfer)](http://www.libradtran.org/)


Build 3D Veglab Plugin from Source 
------------------------------------------
Generally, you are able to modify the behavior of this plugin by editing the [VLebImpl.py](https://raw.github.com/netceteragroup/esa-beam/master/beam-3dveglab-vlab/src/main/resources/auxdata/VLabImpl.py) jython implementation that will have been placed in your BEAM auxdata directory and restarting the application.

However, if you'd like to recreate the entire Java development environment needed for an official build, you can follow these steps (for Fedora linux). 

```bash
# 1. Get the BEAM development env setup script (Fedora 64bit linux)
# This script automates the steps described here http://www.brockmann-consult.de/beam-wiki/display/BEAM/Build+from+Source
wget https://raw.github.com/netceteragroup/esa-beam/master/beam-3dveglab-vlab/src/main/scripts/build_beam_binaries.sh 
# 2. run it
sh build_beam_binaries.sh
# 3. Get development env setup script for this plugin (Fedora 64bit linux)
wget https://raw.gitbub.com/netceteragroup/esa-beam/master/beam-3dveglab-vlab/src/main/scripts/build_beam_vlab_binaries.sh
# 4. run it
sh build_beam_vlab_binaries.sh
# Follow the commented out manual instructions at the end of the build script to finish eclipse configuration
```

NOTE: If you don't have Fedora linux, you can use [this script](https://raw.github.com/netceteragroup/esa-beam/master/beam-3dveglab-vlab/src/main/scripts/build_fedora_virtal_image.sh) to create the virtual image that was used by Netcetera for development.


Build Dependent Software from Source
------------------------------------------

```bash
# Run this compilation script (Fedora 64bit linux + cross compile for win32 )
wget https://raw.gitbub.com/netceteragroup/esa-beam/master/beam-3dveglab-vlab/src/main/scripts/build_dummy_binaries.sh
sh build_dummy_binaries.sh
# Run this compilation script (Fedora 64bit linux + cross compile for win32 )
wget https://raw.gitbub.com/netceteragroup/esa-beam/master/beam-3dveglab-vlab/src/main/scripts/build_librat_binaries.sh
sh build_librat_binaries.sh
# Run this compilation script (Fedora 64bit linux + cross compile for win32 )
wget https://raw.gitbub.com/netceteragroup/esa-beam/master/beam-3dveglab-vlab/src/main/scripts/build_radtran_binaries.sh
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
