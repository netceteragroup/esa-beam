Developer Info for beam-3dveglab-vlab
=======================================

Developer information is split into 2 sections
* [For Scientific Developers](https://github.com/netceteragroup/esa-beam/blob/master/beam-3dveglab-vlab/README.md#for-scientific-developers-)
* [For IT Developers](https://github.com/netceteragroup/esa-beam/blob/master/beam-3dveglab-vlab/README.md#for-it-developers)

For Scientific Developers 
---------------------------
This plugin has been written in a way that nearly everything can be coded in python (the jython variant) rather than Java. We hope this increases maintainability:

* Scientists are more likely to be able to contribute a single python file than a bundle of Java files
* It is easy to try changes yourself - just edit a single file and restart Beam - no development environment or tools needed
* If your like your change, it is easy to email us your modified python file

You can directly make logic changes to the plugin by editing the [${HOME}/.beam/beam-vlab/auxdata/VLabImpl.py](https://raw.github.com/netceteragroup/esa-beam/master/beam-3dveglab-vlab/src/main/resources/auxdata/VLabImpl.py) jython implementation that will have been installed in your BEAM auxdata directory and restarting the BEAM application e.g. ${HOME}/beam-4.11/bin/visat. 

Example change: add an additional sensor 
---------------------------
You only need the typical binary installation for this.

1. Perform [binary only installation](https://github.com/netceteragroup/esa-beam#binary-installation)
2. Enable logging (in ${HOME}/beam-4.11/config/beam.config, uncomment beam.logLevel = INFO)
3. in [${HOME}/.beam/beam-vlab/auxdata/VLabImpl.py](https://raw.github.com/netceteragroup/esa-beam/master/beam-3dveglab-vlab/src/main/resources/auxdata/VLabImpl.py) search for "Sentinel 2" (aka K_SENTINEL2) and everywhere it appears, add your new one e.g. "Sentinel 99" aka K_SENTINEL99
4. You should see your change after selecting the 3D VegLab processor from within BEAM
5. If not, you can add logging e.g. VLAB.logger.info('hello %s' % 'world')
6. And check logfiles in ${HOME}/.beam/log/ and ${HOME}/beam-4.11/log/
7. mailx -s "my esa-beam 3dveglab updates" info@netcetera.com < ${HOME}/.beam/beam-vlab/auxdata/VLabImpl.py

Caveats
---------------------------
Since we are using the jython variant that ships with BEAM, there are limitations
* No 3rd-party modules like numpy, matplotlib, etc
* Not even some typically native python libraries like os, copy, ...
* There is no chdir() so you have to manually prepend directories in many places

But, in the BEAM case, you have access to anything that BEAM (and Java) provides. We have made use of the BEAM-provided jfreechart java library to plot some auxilliary information for example.

For testing purposes, we try to ensure the code can execute from both jython and python. Here is an example of a helper fileExists() routine we have written to support this.

```python
def fileExists(fname):
  """check if fname exists as a file"""
  if sys.platform.startswith('java'):
    from java.io import File
    return File(fname).exists()
  else:
    import os
    return os.path.exists(fname)
```

Testing
---------------------------
Since nearly everything is implemented in that single python file, we were able to provide multiple alternatives for testing.

1. From within BEAM, using log statements (as described in the "Example change" above)
2. Standalone "headless" (either jython or python)
```jython -Dpython.path=${HOME}/beam-4.11/lib/jcommon-1.0.16.jar:${HOME}/beam-4.11/lib/jfreechart-1.0.13.jar VLabImpl.py```
3. Standalone with a "fake" swing-based GUI (jython only)
```jython -Dvlab.fakebeam=1 -Dpython.path=${HOME}/beam-4.11/lib/jcommon-1.0.16.jar:${HOME}/beam-4.11/lib/jfreechart-1.0.13.jar VLabImpl.py```

For case 2, search for the method selftests() to see (or change) which tests will be run in a GUI-less way (with log messages appearing on the console from where the command is run).

VLabImpl.py Code Layout
---------------------------
The code is laid out in the following sections.

1. VLAB class - for constants, configuration, and static utility methods
2. Minimize_NMSimplex - a utility class for one of the minimization libraries
3. DUMMY - a dummy to show how to integrate a trivial 3rd party binary
4. Dart_* - classes for DART data cube creation
5. DART - the driver for the dart integration code
6. Librat_* - classes for supporting LIBRAT integration
7. LIBRAT - the driver for the LIBRAT integration code
8. MAIN - dispatching logic for the three ways to run this code
9. BEAM-only code - classes needed only to integrate with BEAM

For IT Developers
---------------------------

Full development environment
------------------------------------------
This describes the complete variant for installing the entire (Java-based) development environment needed for a complete build. You shouldn't need this unless you want to build a release, change the help files, etc.

The [first script](https://github.com/netceteragroup/esa-beam/blob/master/beam-3dveglab-vlab/src/main/scripts/build_beam_binaries.sh) automates the steps for building BEAM as described in http://www.brockmann-consult.de/beam-wiki/display/BEAM/Build+from+Source

**See below for OPTIONAL step on creating a linux virtual image**

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
Most of the plugin's dependent software is open source and can be compiled yourself. Here are scripts that we used to build the binary snapshots of [librat](http://www2.geog.ucl.ac.uk/~plewis/bpms/src/lib/) and [libradtran](http://www.libradtran.org/doku.php)

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

Build Linux Virtual Image (OPTIONAL)
------------------------------------------
To ensure reproducibility of builds, we use a standard fedora linux install
built in a virtual machine for development. Here is a script to do it yourself.

**This block for creating a virtual image is OPTIONAL**
```bash
# OPTIONAL - this is used to create a Fedora linux virtual image so that you can be sure that the build environment setup script below works unmodified 
wget https://raw.github.com/netceteragroup/esa-beam/master/beam-3dveglab-vlab/src/main/scripts/build_fedora_virtual_image.sh
# build the virtual image (side-effect - f19-xfce-dev will be ready to start in VirtualBox)
sh build_fedora_virtual_image.sh
# start up the virtual machine you just created
VirtualBox --startvm f19-xfce-dev
# now login to the virtual machine and execute the commands below...
# if you ssh into it, it is easier to copy/paste from this window :-)
# ssh -Y fedora@localhost -p 2222

```

License
-----------------------------------------
* [GNU General Public License](http://www.gnu.org/licenses//gpl-3.0-standalone.html)
