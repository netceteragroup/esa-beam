3D Vegation Lab plugin for the ESA BEAM toolkit
=======================================

ESA BEAM toolkit
http://www.brockmann-consult.de/cms/web/beam/

3D Vegetation Lab plugin
http://www.geo.uzh.ch/de/lehrstuehle-und-abteilungen/fernerkundung/forschung/lidar-remote-sensing-lidarlab/ongoing-projects/3dveglab

Binary Installation
------------------------------------------
1. Download and install BEAM (Version 4.10.3) [64bit linux or 32bit windows]
    http://www.brockmann-consult.de/cms/web/beam/software/
2. Download the latest plugin and place it in BEAM's modules directory
    ftp://ftp.netcetera.ch/pub/beam-3dveglab-vlab-LATEST.jar 
3. Run Beam (aka visat)
    ${HOME}/beam-4.10.3/bin/visat
4. Install dependent vegetation lab software (librat, DART, libradtran)
    ${HOME}/.beam/beam-vlab/auxdata/replaceWithLatest.sh

Build 3D Veglab Plugin from Source 
------------------------------------------
1. Run BEAM development env setup script (Fedora 64bit linux)
    wget https://raw.gitbub.com/netceteragroup/esa-beam/beam-3dveglab-vlab/src/main/scripts/master/build_beam_binaries.sh
    sh build_beam_binaries.sh
2. Run this plugin development env setup script (Fedora 64bit linux)
    wget https://raw.gitbub.com/netceteragroup/esa-beam/beam-3dveglab-vlab/src/main/scripts/master/build_beam_vlab_binaries.sh
    sh build_beam_vlab_binaries.sh
3. Follow the commented out manual instructions at the end of the build script


Build Dependent Software from Source
------------------------------------------
1. Run this compilation script (Fedora 64bit linux + cross compile for win32 )
    wget https://raw.gitbub.com/netceteragroup/esa-beam/beam-3dveglab-vlab/src/main/scripts/master/build_dummy_binaries.sh
    sh build_dummy_binaries.sh
2.  Run this compilation script (Fedora 64bit linux + cross compile for win32 )
    wget https://raw.gitbub.com/netceteragroup/esa-beam/beam-3dveglab-vlab/src/main/scripts/master/build_librat_binaries.sh
    sh build_librat_binaries.sh
3.  Run this compilation script (Fedora 64bit linux + cross compile for win32 )
    wget https://raw.gitbub.com/netceteragroup/esa-beam/beam-3dveglab-vlab/src/main/scripts/master/build_radtran_binaries.sh
    sh build_radtran_binaries.sh

3D Vegetation Dependent software
-----------------------------------------
* librat (Monte Carlo Ray Tracing library)
    http://www2.geog.ucl.ac.uk/~plewis/bpms/src/lib/
* DART (Discrete Anisotropic Radiative Transfer)
    http://www.cesbio.ups-tlse.fr/us/dart/dart_description.html
* libRadtran (library for radiative transfer )
    http://www.libradtran.org/

BEAM Plugin Contributing Authors
-----------------------------------------
* Daniel Kueckenbrink 
* Joshy Cyriac 
* Marcel Kessler 
* Jason Brazile

License
-----------------------------------------
* [GNU General Public License](http://www.gnu.org/licenses//gpl-3.0-standalone.html)
