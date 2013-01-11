3D Vegation Lab plugin for the ESA BEAM toolkit
=======================================

* [ESA BEAM toolkit](http://www.brockmann-consult.de/cms/web/beam/)
* [3D Vegetation Lab plugin](http://www.geo.uzh.ch/en/units/rsl/research/lidar-remote-sensing-lidarlab/ongoing-projects/3dveglab)

Binary Installation
------------------------------------------

```bash
# MANUALLY: Download BEAM  - you have to click to Proceed
firefox 'http://www.brockmann-consult.de/cms/web/beam/dlsurvey?p_p_id=downloadportlet_WAR_beamdownloadportlet10&what=software/beam/4.10.3/beam_4.10.3_linux64_installer.sh'
# or windows32 ...  http://www.brockmann-consult.de/cms/web/beam/dlsurvey?p_p_id=downloadportlet_WAR_beamdownloadportlet10&what=software/beam/4.10.3/beam_4.10.3_win32_installer.exe
sh beam_4.10.3_linux64_installer.sh
# get latest machine-independent java binary of 3dveglab BEAM plugin
wget ftp://ftp.netcetera.ch/pub/beam-3dveglab-vlab-LATEST.jar 
# (re)place it in BEAM's modules directory
rm -f ${HOME}/.beam/beam-3dveglab-vlab-*.jar
cp beam-3dveglab-vlab-LATEST.jar ${HOME}/.beam/modules
# run beam 
${HOME}/beam-4.10.3/bin/visat
# MANUALLY: start the 3dveglab tool plugin (so it will unpack the module)
# get snapshots of dependent vegetation lab software (librat, DART, libradtran)
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

```bash
# Run BEAM development env setup script (Fedora 64bit linux)
wget https://raw.github.com/netceteragroup/esa-beam/master/beam-3dveglab-vlab/src/main/scripts/build_beam_binaries.sh 
sh build_beam_binaries.sh
# Run this plugin development env setup script (Fedora 64bit linux)
wget https://raw.gitbub.com/netceteragroup/esa-beam/master/beam-3dveglab-vlab/src/main/scripts/build_beam_vlab_binaries.sh
sh build_beam_vlab_binaries.sh
# Follow the commented out manual instructions at the end of the build script
```


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
* Daniel Kueckenbrink 
* Joshy Cyriac 
* Marcel Kessler 
* Jason Brazile

License
-----------------------------------------
* [GNU General Public License](http://www.gnu.org/licenses//gpl-3.0-standalone.html)
