3D Vegetation Lab plugin(s) for the ESA BEAM toolkit
=======================================

This repository contains plugin modules developed by Netcetera Zurich for version 4.11 of the ESA BEAM Earth Observation Toolbox and Development Platform.

* [ESA BEAM toolkit](http://www.brockmann-consult.de/cms/web/beam/)
* [3D Vegetation Lab plugin](http://www.geo.uzh.ch/en/units/rsl/research/lidar-remote-sensing-lidarlab/ongoing-projects/3dveglab)

Binary Installation
---------------------------

Binary installation of the 3D Vegetation Lab plugin is automated [in Java](https://github.com/netceteragroup/esa-beam/blob/master/beam-3dveglab-vlab/src/main/scripts/Install.java) and involves
 * copying/replacing the plugin jar in $HOME/beam-4.11/modules 
 * first-time plugin run to create/unpack $HOME/.beam/beam-vlab/auxdata/
 * fetch/unpack latest versions of dependent 3rd party software into auxdata
 * create command line wrappers in the bin directory for batch operation

Binary Installation (windows version)
------------------------------------------

```dos
rem 1. MANUALLY: Download BEAM  - you have to click to Proceed
rem press Windows-R  to get the "run" prompt
iexplore "http://www.brockmann-consult.de/cms/web/beam/dlsurvey?p_p_id=downloadportlet_WAR_beamdownloadportlet10&what=software/beam/4.11/beam_4.11_win32_installer.exe"
rem 2. run installer
beam_4.11_win32_installer.exe
rem 3. go to the beam bin directory (the directory where you just installed it)
rem press Windows-R to get the "run" prompt 
cmd /K "cd /d C:\Program Files (x86)\beam-4.11\bin"
rem 4. download the 3DVegLabInstaller.jar into the bin directory from step 3.
iexplore "ftp://ftp.netcetera.ch/pub/"
rem 5. run the 3DVegLabInstaller.jar from inside the bin directory 
press Windows-R to get the "run" prompt
cmd /K "cd /d C:\Program Files (x86)\beam-4.11\bin"
java -jar 3DVegLabInstaller.jar
```
Binary Installation (linux version)
------------------------------------------

```bash
# 1. MANUALLY: Download BEAM  - you have to click to Proceed
firefox 'http://www.brockmann-consult.de/cms/web/beam/dlsurvey?p_p_id=downloadportlet_WAR_beamdownloadportlet10&what=software/beam/4.11/beam_4.11_linux64_installer.sh'
# 2. run installer
sh beam_4.11_linux64_installer.sh
# NOTE: an early version of BEAM's 4.11 installer still named the installed directory beam-4.10.3. If so, please rename it to beam-4.11
# 3. go to the beam bin directory (the directory where you just installed it)
cd ${HOME}/beam-4.11/bin
# 4. download 3DVegLabInstaller.jar into the bin directory from step 3.
wget ftp://ftp.netcetera.ch/pub/3DVegLabInstaller.jar
# 5. run the 3DVegLabInstall.jar from inside the bin directory
java -jar 3DVegLabInstaller.jar
# 6. run BEAM
${HOME}/beam-4.11/bin/visat
```

Once you have started BEAM (visat), use Tools/3D Vegetation Lab Processor to start the plugin.

3D Vegetation Lab Dependent software
-----------------------------------------
The BEAM Vegetation Lab plugin relies on the following 3rd party software. Binary snapshots of this software compiled for linux64/win32 platforms are automatically installed by the 3DVegLabInstaller.jar described above

* [librat (Monte Carlo Ray Tracing library)](http://www2.geog.ucl.ac.uk/~plewis/bpms/src/lib/)
* [DART (Discrete Anisotropic Radiative Transfer)](http://www.cesbio.ups-tlse.fr/us/dart/dart_description.html)
* [libRadtran (library for radiative transfer)](http://www.libradtran.org/)


For 3D Vegetation Lab Developers
------------------------------------------
There are two modes of development, which are described in [a separate README](https://github.com/netceteragroup/esa-beam/tree/master/beam-3dveglab-vlab/README.md)
 1. [Development for Scientists](https://github.com/netceteragroup/esa-beam/blob/master/beam-3dveglab-vlab/README.md#for-scientific-developers-) (in python - changing the single jython implementation file, restarting BEAM, browsing log files)
 2. [Development for BEAM developers](https://github.com/netceteragroup/esa-beam/blob/master/beam-3dveglab-vlab/README.md#for-it-developers) (in Java and python - full development, including Java plugin infrastructure, help files, support scripts, etc.)


BEAM Plugin Contributing Authors
-----------------------------------------
* Mat Disney
* Cyrill Schenkel
* Fabian Schneider
* Nicolas Lauret
* Daniel Kuekenbrink 
* Joshy Cyriac 
* Marcel Kessler 
* Jason Brazile

License
-----------------------------------------
* [GNU General Public License](http://www.gnu.org/licenses//gpl-3.0-standalone.html)
