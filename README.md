3D Vegetation Lab plugin(s) for the ESA BEAM toolkit
=======================================

This repository contains plugin modules developed by Netcetera Zurich for version 4.11 of the ESA BEAM Earth Observation Toolbox and Development Platform.

* [ESA BEAM toolkit](http://www.brockmann-consult.de/cms/web/beam/)
* [3D Vegetation Lab plugin](http://www.geo.uzh.ch/en/units/rsl/research/lidar-remote-sensing-lidarlab/ongoing-projects/3dveglab)

Binary Installation
---------------------------

Binary installation of the 3D Vegetation Lab plugin is automated [in Java](https://github.com/netceteragroup/esa-beam/blob/master/beam-3dveglab-vlab/src/main/scripts/Install.java) and involves
 * copying (or replacing) the plugin jar into ${BEAMHOME}/beam-4.11/modules
 * first-time batch run to install ${HOME}/.beam/beam-vlab/auxdata/beam-vlab
 * fetch/unpack 3rd-party software into ${HOME}/.beam/beam-vlab/auxdata/beam-vlab
 * create command line wrappers in the bin directory for batch operation 

Binary Installation (windows version)
------------------------------------------
Two pre-install steps:
 1. Visit the [windows 32-bit BEAM-installer page](http://www.brockmann-consult.de/cms/web/beam/dlsurvey?p_p_id=downloadportlet_WAR_beamdownloadportlet10&what=software/beam/4.11/beam_4.11_win32_installer.exe) and download into your **_Downloads_** folder
 2. Save our [3DVegLab plugin installer jar](http://www.geo.uzh.ch/microsite/3dveglab/software/3DVegLabInstaller.jar) file in your **_Downloads_** folder.

```dos
rem press Windows-R to get the "run" prompt, then type "cmd" to get a shell
cd %HOMEDRIVE%%HOMEPATH%\Downloads
rem Note: when prompted, we suggest C:\data\Program Files (x86)\beam-4.11
rem because 3DVeglabInstaller.jar will fail if Administrator access is needed
beam_4.11_win32_installer.exe
move 3DVegLabInstaller.jar "C:\data\Program Files (x86)\beam-4.11\bin"
cd /d "C:\data\Program Files (x86)\beam-4.11\bin"
..\jre\bin\java -jar 3DVegLabInstaller.jar
```
Binary Installation (linux version)
------------------------------------------
Two pre-install steps:
 1. Visit the [linux 64-bit BEAM installer page](http://www.brockmann-consult.de/cms/web/beam/dlsurvey?p_p_id=downloadportlet_WAR_beamdownloadportlet10&what=software/beam/4.11/beam_4.11_linux64_installer.sh) and download into your **_Downloads_** folder
 2. Save our [3DVegLab plugin installer jar](http://www.geo.uzh.ch/microsite/3dveglab/software/3DVegLabInstaller.jar) file in your **_Downloads_** folder

```bash
cd ${HOME}/Downloads
sh beam_4.11_linux64_installer.sh
mv 3DVegLabInstaller.jar ${HOME}/beam-4.11/bin
cd ${HOME}/beam-4.11/bin
../jre/bin/java -jar 3DVegLabInstaller.jar
```

Once you have started BEAM (visat), use Tools/3D Vegetation Lab Processor to start the plugin.

3D Vegetation Lab Dependent software
-----------------------------------------
The BEAM Vegetation Lab plugin relies on the following 3rd party software. Binary snapshots of this software compiled for linux64/win32 platforms are automatically installed by the 3DVegLabInstaller.jar described above

* [librat (Monte Carlo Ray Tracing library)](http://www2.geog.ucl.ac.uk/~plewis/bpms/src/lib/)
* [DART (Discrete Anisotropic Radiative Transfer)](http://www.cesbio.ups-tlse.fr/dart/license/en/dartModel.php)
* [libRadtran (library for radiative transfer)](http://www.libradtran.org/)


For 3D Vegetation Lab Developers
------------------------------------------
There are two modes of development, which are described in [a separate README](https://github.com/netceteragroup/esa-beam/tree/master/beam-3dveglab-vlab/README.md)
 1. [Development for Scientists](https://github.com/netceteragroup/esa-beam/blob/master/beam-3dveglab-vlab/README.md#for-scientific-developers-) (in python - changing the single jython implementation file, restarting BEAM, browsing log files)
 2. [Development for BEAM developers](https://github.com/netceteragroup/esa-beam/blob/master/beam-3dveglab-vlab/README.md#for-it-developers) (in Java and python - full development, including Java plugin infrastructure, help files, support scripts, etc.)


BEAM 3DVegLab Plugin Contributing Authors
-----------------------------------------
* Mat Disney
* Cyrill Schenkel
* Fabian Schneider
* Nicolas Lauret
* Tristan Gregoire
* Daniel Kuekenbrink 
* Joshy Cyriac 
* Marcel Kessler 
* Jason Brazile

License
-----------------------------------------
* [GNU General Public License](http://www.gnu.org/licenses//gpl-3.0-standalone.html)
