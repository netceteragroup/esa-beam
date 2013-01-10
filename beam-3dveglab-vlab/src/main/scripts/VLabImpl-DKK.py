#coding: utf-8
import sys

from array import *
from java import awt
from java import io
from java import lang
from java.io import BufferedReader
from java.io import BufferedWriter
from java.io import File
from java.io import File
from java.io import FileInputStream
from java.io import FileOutputStream
from java.io import InputStreamReader
from java.io import IOException
from java.io import OutputStreamWriter
from java.lang import IllegalArgumentException
from java.lang import Integer
from java.lang import ProcessBuilder
from java.lang import RuntimeException
from java.lang import System
from java.nio.channels import FileChannel
from java.util import HashMap
from java.util import Map
from java.util.logging import Logger
from javax import swing
import java.awt.GridBagConstraints as GridBagConstraints
import java.util.ArrayList as ArrayList
import java.util.Arrays as Arrays
import java.util.Vector as Vector

from com.bc.ceres.core import ProgressMonitor

from org.esa.beam.framework.dataio import ProductSubsetDef
from org.esa.beam.framework.dataio import ProductWriter
from org.esa.beam.framework.datamodel import PixelPos
from org.esa.beam.framework.datamodel import Product
from org.esa.beam.framework.datamodel import RasterDataNode

from org.esa.beam.framework.param import Parameter
from org.esa.beam.framework.processor import Processor
from org.esa.beam.framework.processor import ProcessorException
from org.esa.beam.framework.processor import ProcessorUtils
from org.esa.beam.framework.processor import ProductRef
from org.esa.beam.framework.processor import Request
from org.esa.beam.framework.processor import RequestElementFactory
from org.esa.beam.framework.processor.ui import ProcessorUI
from org.esa.beam.dataio.dimap import DimapProductConstants;

from org.esa.beam.framework.param import ParamValidateException
from org.esa.beam.framework.processor import ProcessorConstants
from org.esa.beam.framework.processor import RequestElementFactoryException
from org.esa.beam.framework.ui import GridBagUtils
from org.esa.beam.framework.ui import UIUtils
from org.esa.beam.framework.dataop.resamp import ResamplingFactory

from org.esa.beam.framework.dataop.dem import ElevationModelDescriptor
from org.esa.beam.framework.dataop.dem import ElevationModelRegistry
from org.esa.beam.framework.dataop.maptransf import MapInfo
from org.esa.beam.framework.param import ParamProperties
from org.esa.beam.framework.param.validators import NumberValidator
from org.esa.beam.framework.processor import DefaultRequestElementFactory
from org.esa.beam.util import Guardian 

from com.netcetera.vlab import IVLabProcessor
from com.netcetera.vlab import IVLabProcessorUi
from com.netcetera.vlab import VLabProcessor
from com.netcetera.vlab import VLabUi

class VLabImpl(IVLabProcessor):
    
    
    def getName(self):
        return VLabConstants.PROCESSOR_NAME
    
    def getSymbolicName(self):
        return VLabConstants.PROCESSOR_SYMBOLIC_NAME
    
    def getVersion(self):
        return VLabConstants.VERSION_STRING
    
    def getCopyrightInformation(self):
        return VLabConstants.COPYRIGHT_INFO
    
    def getUITitle(self):
        return VLabConstants.UI_TITLE
    
    def getLogger(self):
        return self._logger
    def getLoggerName(self):
        return VLabConstants.LOGGER_NAME
    
    def process(self, pm, request):
        
        ProcessorUtils.setProcessorLoggingHandler(
                VLabConstants.DEFAULT_LOG_PREFIX, request, self.getName(),
                self.getVersion(), self.getCopyrightInformation())
        

        self._logger = Logger.getLogger(VLabConstants.LOGGER_NAME)
        
        self._logger.info("process gets started")
        
        self._logger.info("Parameter list:")
        for i in range(request.getNumParameters()):
            self._logger.info(request.getParameterAt(i).getName() + " = " + request.getParameterAt(i).getValueAsText())
        
        pm.beginTask("Running VegetationLab Metaprocessor...", 10)
        
        try:
          Thread.sleep(2000);
        except Exception, e:
          raise RuntimeException(e.getMessage())
        
        opdir = File(request.getParameter("output_folder").getValueAsText())
        if (request.getParameter("output_folder").getValueAsText() == ""):
            self._logger.severe("No output folder defined.")
        examplesdir = File(VLabProcessor.auxdataInstallDir.getAbsolutePath() + File.separator + "examplefiles")
        
        
        #function to generate .obj file (doscene.py) only called when Default RAMI is chosen as 3D Scene
        if (request.getParameter("3d_scene").getValueAsText() == "Default RAMI"):
            opdir = File(request.getParameter("output_folder").getValueAsText())
            examplesdir = File(VLabProcessor.auxdataInstallDir.getAbsolutePath() + File.separator + "examplefiles")
        
            #copy necessary files from auxdata/examplefiles to outputdir, if default files should be used
            self._logger.info("Copying files for default scene creation...")
            location = File(examplesdir.getAbsolutePath() + File.separator + "locations.dat")
            plantsMatlib = File(examplesdir.getAbsolutePath() + File.separator + "plants.matlib")
            soil = File(examplesdir.getAbsolutePath() + File.separator + "soil.dat")
            sphere = File(examplesdir.getAbsolutePath() + File.separator + "sphere.obj")
            refl = File(examplesdir.getAbsolutePath() + File.separator + "refl")
        
            self.copy(location, File(opdir.getAbsolutePath() + File.separator + "locations.dat"))
            self.copy(plantsMatlib, File(opdir.getAbsolutePath() + File.separator + "plants.matlib"))
            self.copy(soil, File(opdir.getAbsolutePath() + File.separator + "soil.dat"))
            self.copy(sphere, File(opdir.getAbsolutePath() + File.separator + "sphere.obj"))
            self.copy(refl, File(opdir.getAbsolutePath() + File.separator + "refl"))
            self.doscene(request)
        
        
        # calling the different processor according to parameter rt_processor:
        if (request.getParameter("rt_processor").getValueAsText() == "librat"):
            #function to initialize and run librat
            #when scene Default RAMI was chosen, this will use the generated scene from the doscene and the generated wb and
            #angles file from the method writeInputFiles. At the moment, if the Scene Laegeren will be implemented, all the 
            #necessary file (.obj file, refl folder) for this case need to be copied into the output folder. Maybe this should
            #be changed
            if (self.exitVal == 0):
                self.writeInputFiles(request)
                self.runLibrat(request)
                
        if (request.getParameter("rt_processor").getValueAsText() == "dart"):
            #function call for the dart rt. At the moment still a cheat, as it is not entirely sure, how to get to the
            #input files for dart out of the GUI inputs.
            
            if (self.exitVal == 0):
                self.runDart(request)
                
        #if librat or dart finished successfully, libradtran will be called now. At the moment this is still a cheat
        #as it's still not clear how to create the input data for uvspec out of the librat/dart output...
        if(self.exitVal == 0):
            #if the conversion of librat/dart output to uvspec input is cleared, the conversion algorithm should be 
            #called here:
            #self.writeUVSPECInput(request)
            #this should have created a file called "output_prefix"_uvspec.INP plus probalby several additional files
            #which get references in this .INP file. (Maybe put all this files into one folder i.e. UVSPEC_INP)
            
            
            #CHEAT taking input file from examples folder in the libradtran auxdata folder... delete these lines, when 
            #input file can be created.
            
            libradtranAuxdataDir = VLabProcessor.auxdataInstallDir.getAbsolutePath() + File.separator + "libradtran" + File.separator + "auxdata" + File.separator
            inputFile = File(libradtranAuxdataDir)
            if (self.isUnix()):
                inputFile = File(inputFile, "linux" + File.separator + "lib" + File.separator + "examples" + File.separator + "UVSPEC_CLEAR.INP")
            elif (self.isMac()):
                inputFile = file(inputFile, "mac" + File.separator + "lib" + File.separator + "examples" + File.separator + "UVSPEC_CLEAR.INP")
            elif (self.isWindows()):
                inputfile = file(inputFile, "windows" + File.separator + "lib" + File.separator + "examples" + File.separator + "UVSPEC_CLEAR.INP")
            
            
            
            
            #calling uvspec:
            self.runLibradtran(request, inputFile)
        
        
        if (self.exitVal == 0):
            self._logger.info("Request has been processed successfully!")
        else:
            self._logger.severe("An error occured at the end of the process...")  
        pm.done()
        
        
    def writeInputFiles(self, request):
        
        self.writeAnglesFile(request)
        self.writeWBFile(request)
        
        #maybe this has to be implemented as well to copy necessery files to op directory (e.g. soil, location files):
        #self.copyFiles()
    
    def writeAnglesFile(self, request):
        outputFolder = request.getParameter("output_folder").getValueAsText()
        outputPrefix = request.getParameter("output_prefix").getValueAsText()
        filename = outputFolder + File.separator + outputPrefix + "_angles.dat"
        
        anglesFile = open(filename, 'w')
        view_zen = (request.getParameter("viewing_zenith").getValueAsText())
        view_az = request.getParameter("viewing_azimuth").getValueAsText()
        illum_zen = request.getParameter("illumination_zenith").getValueAsText()
        illum_az = request.getParameter("illumination_azimuth").getValueAsText()
        anglesFile.write(view_zen + " " + view_az + " " + illum_zen + " " + illum_az)
        anglesFile.close()
        self._logger.info("Angles File got created")
        
    def writeWBFile(self, request):
        outputFolder = request.getParameter("output_folder").getValueAsText()
        outputPrefix = request.getParameter("output_prefix").getValueAsText()
        filename = outputFolder + File.separator + outputPrefix + "_wavebands.dat"
        
        spec_bands = request.getParameter("spec_bands").getValueAsText()
        bands_str = spec_bands.split(',')
        bands = [0] * len(bands_str)
        for i in range(len(bands_str)):
            bands[i] = Integer.parseInt(bands_str[i].strip())
        wvls = [0]*len(bands)
        if (request.getParameter("sensors").getValueAsText() == "Sentinel-2"):
            for i in range(len(bands)):
                wvls[i] = VLabConstants.WB_SENTINEL_2[bands[i] - 1]
        if (request.getParameter("sensors").getValueAsText() == "Sentinel-3"):
            for i in range(len(bands)):
                wvls[i] = VLabConstants.WB_SENTINEL_3[bands[i] - 1]
                
            
        
        
        wbFile = open(filename, 'w')
        for i in range(len(bands)):
            wbFile.write(str(i) + " " + str(wvls[i]) + "\n")
            
        wbFile.close()
        
        self._logger.info("Wavebandfile got created")
        
        
        
        
    def doscene(self, request):
        self._logger.info("Generation of the scene object got called")
        
        linux_doscene_exe = VLabProcessor.auxdataInstallDir.getAbsolutePath() + File.separator + "doscene.py"
        
        
        input = request.getParameter("output_folder").getValueAsText() + File.separator + "locations.dat"
        soil = request.getParameter("output_folder").getValueAsText() + File.separator + "soil.dat"
        output = request.getParameter("output_folder").getValueAsText() + File.separator + request.getParameter("output_prefix").getValueAsText() +"_scene.obj"
        cmd = linux_doscene_exe + " -i " + input + " -s " + soil + " -o " + output + " -r"
        self._logger.info("scene creation command: " + cmd)
        working_dir = VLabProcessor.auxdataInstallDir
        exec_file = File(working_dir.getPath() + File.separator + "doscene.py")
        exec_file.setExecutable(True)
        pb = ProcessBuilder(["sh", "-c", cmd])
        pb.directory(working_dir)
        pb.redirectErrorStream(True)
        env = pb.environment()
        path = env.get("PATH")
        path = path + File.pathSeparator + working_dir.getAbsolutePath()
        env.put("PATH", path)

        
        try:
            proc = pb.start()
            self.exitVal = proc.waitFor()
            br = BufferedReader(InputStreamReader(proc.getInputStream()))
            line = br.readLine()
            error = ""
            while line != None :
                print '> ', line.encode('ascii', 'ignore')
                error = line.encode('ascii', 'ignore')
                line = br.readLine()
            if (self.exitVal != 0):
                self._logger.severe("An error occured while trying to generate scene: Exit Value: " + self.exitVal + "Error Message: " + error)
        except IOException, e:
            self._logger.severe("ERROR: " + e.getMessage())
            raise RuntimeException(e.getMessage())
    
    def runLibrat(self, request):
        self._logger.info("starting Librat process")
        librat_lib_linux_path = VLabProcessor.auxdataInstallDir.getAbsolutePath() + File.separator + "librat" + File.separator + "auxdata" + File.separator + "linux" + File.separator + "lib" + File.separator + "lib"
        librat_exec_linux_path = VLabProcessor.auxdataInstallDir.getAbsolutePath() + File.separator + "librat" + File.separator + "auxdata" + File.separator + "linux" + File.separator + "lib" + File.separator + "bin"
        librat_lib_mac_path = VLabProcessor.auxdataInstallDir.getAbsolutePath() + File.separator + "librat" + File.separator + "auxdata" + File.separator + "mac" + File.separator + "lib" + File.separator + "lib"
        librat_exec_mac_path = VLabProcessor.auxdataInstallDir.getAbsolutePath() + File.separator + "librat" + File.separator + "auxdata" + File.separator + "mac" + File.separator + "lib" + File.separator + "bin"
        librat_lib_win_path = "not yet implemented..."
        
        #start binary file has to be set executable:
        exec_file = File("")
        if self.isUnix():
            exec_file = File(librat_exec_linux_path + File.separator + "start")
        if self.isMac():
            exec_file = File(librat_exec_mac_path + File.separator + "start")
        
        exec_file.setExecutable(True)
           
        #all files in the lib folder have to be set executable...
        if self.isUnix():
            lib_dir = File(librat_lib_linux_path)
            list = lib_dir.list()
            for path in list:
                file = File(librat_lib_linux_path + File.separator + path)
                file.setExecutable(True)    
            
        #also bin folder, some files need to be set executable
        if self.isUnix():
            bs = File(librat_exec_linux_path + File.separator + "bs")
            bs.setExecutable(True)
            hips2pbm = File(librat_exec_linux_path + File.separator + "hips2pbm")
            hips2pbm.setExecutable(True)
            hipstats = File(librat_exec_linux_path + File.separator + "hipstats")
            hipstats.setExecutable(True)
            linear = File(librat_exec_linux_path + File.separator + "linear")
            linear.setExecutable(True)
            reseq = File(librat_exec_linux_path + File.separator + "reseq")
            reseq.setExecutable(True)
            stripheader = File(librat_exec_linux_path + File.separator + "stripheader")
            stripheader.setExecutable(True)
        
       
        
        exec_file = File(VLabProcessor.auxdataInstallDir.getAbsolutePath() + File.separator + "dobrdf.py")
        exec_file.setExecutable(True)
        
        output_dir = "brdf"
        object = request.getParameter("output_prefix").getValueAsText() + "_scene.obj"
        angles = request.getParameter("output_prefix").getValueAsText() + "_angles.dat"
        wb = request.getParameter("output_prefix").getValueAsText() + "_wavebands.dat"
        
        cmd = exec_file.getAbsolutePath() + " -opdir " + output_dir + " -obj " + object + " -angles " + angles + " -wb " + wb + " -v &"
        self._logger.info("Command for librat: " + cmd)
        pb = ProcessBuilder(["sh", "-c", cmd])
        working_dir = File(request.getParameter("output_folder").getValueAsText())
        pb.directory(working_dir)
        pb.redirectErrorStream(True)
        env = pb.environment()
        path = env.get("PATH")
        if self.isUnix():
            path = path + File.pathSeparator + librat_exec_linux_path
        elif self.isMac():
            path = path + File.pathSeparator + librat_exec_mac_path
        elif self.iWindows():
            self._logger.warning("sorry, only mac an linus is supported at the moment")
        env.put("PATH", path)
        path = env.get("LD_LIBRARY_PATH")
        if self.isUnix():
            path = path + File.pathSeparator + librat_lib_linux_path
        elif self.isMac():
            path = path + File.pathSeparator + librat_lib_mac_path
        elif self.isWindows():
            self._logger.warning("sorry, only mac an linux is supported at the moment...")
            
        env.put("LD_LIBRARY_PATH", path)
        #usr_home = System.getProperty("user.home")
        #bpms = usr_home + File.separator + "bpms"
        #env.put("BPMS", bpms)
        try:
            proc = pb.start()
            self.exitVal = proc.waitFor()
            br = BufferedReader(InputStreamReader(proc.getInputStream()))
            br_error = BufferedReader(InputStreamReader(proc.getErrorStream()))
            line = br.readLine()
            error = ""
            while line != None:
                print '> ', line.encode('ascii', 'ignore')
                error = line.encode('ascii', 'ignore')
                line = br.readLine()
            if (self.exitVal != 0):
                self._logger.severe("An error occured while trying to run librat: Exit Value: " + self.exitVal + "Error Message: " + error)
        except IOException, e:
            self._logger.severe("ERROR: " + e.getMessage())
            raise RuntimeException(e.getMessage())
       
           
 
    
    def runLibradtran(self, request, inputFile):
        #self._logger.info("starting Libradtran process...")
        inputFile = inputFile.getAbsolutePath()
        outputFile = request.getParameter("output_folder").getValueAsText() + File.separator + request.getParameter("output_prefix").getValueAsText() + "_uvspec.out"
        
        exec_file = File(VLabProcessor.auxdataInstallDir.getAbsolutePath() + File.separator + "libradtran" + File.separator + "auxdata" + File.separator)
        if (self.isUnix()):
            exec_file = File(exec_file, "linux" + File.separator + "lib" + File.separator + "bin" + File.separator + "uvspec")
            exec_file.setExecutable(True)
        elif (self.isMac()):
            exec_file = File(exec_file, "mac" + File.separator + "lib" + File.separator + "bin" + File.separator + "uvspec")
            exec_file.setExecutable(True)
        elif (self.isWindows()):
            exec_file = File(exec_file, "windows" + File.separator + "lib" + File.separator + "bin" + File.separator + "uvspec.exe")
            exec_file.setExecutable(True)
        
        
        
        cmd = exec_file.getAbsolutePath() + " < " + inputFile + " > " + outputFile
        #self._logger.info("Command for running libradtran: " + cmd)
        pb = ProcessBuilder(["sh", "-c", cmd])
        pb.directory(exec_file.getParentFile())
        pb.redirectErrorStream(True)
        
        try:
            proc = pb.start()
            self.exitVal = proc.waitFor()
            br = BufferedReader(InputStreamReader(proc.getInputStream()))
            self.line = br.readLine()
                #parser = make_parser()
            while self.line != None :
                print '> ', self.line.encode('ascii', 'ignore')
                self.error = self.line.encode('ascii', 'ignore')
                self.line = br.readLine()
            if (self.exitVal != 0):
                self._logger.severe("An error occured while trying to run libradtran: Exit Value: " + self.exitVal + "Error Message: " + self.error)
        except IOException, e:
            self._logger.severe("ERROR: " + e.getMessage())
            raise RuntimeException(e.getMessage())
        
    def runDart(self, request):
        self._logger.info("starting Dart process...")
        
        # defining simulation folder, still a cheat, a new simulation with case specific input files should be generated
        libdart_auxdata = File(VLabProcessor.auxdataInstallDir, File.separator + "libdart" + File.separator + "auxdata" + File.separator)
        simu_folder = File("")
        exec_file = File("")
        dart_home = File("")
        dart_local = File("")
        if (self.isUnix()):
            simu_folder = File(libdart_auxdata, "linux" + File.separator + "dart_local" + File.separator + "simulations" + File.separator + "3D_VegLab_simu")
            exec_file = File(libdart_auxdata, "linux" + File.separator + "tools" + File.separator + "lignes_commande" + File.separator + "linux" + File.separator + "LancementDART_complet.sh")
            exec_file.setExecutable(True)
            dart_home = File(libdart_auxdata, "linux" + File.separator + "dart" + File.separator + "bin")
            dart_local = File(libdart_auxdata, "linux" + File.separator + "dart_local")
        #if (self.iMac()):
        #    simu_folder = (simu_folder, "mac" + File.separator + "dart_local" + File.separator + "simulations" + File.separator + "3D_VegLab_simu")
        if (self.isWindows()):
            #apparantely on windows, the different steps have to be called seperatelly.
            simu_folder = File(simu_folder, "windows" + File.separator + "dart_local" + File.separator + "simulations" + File.separator + "3D_VegLab_simu")
            directions = File(libdart_auxdata, "windows" + File.separator + "tools" + File.separator + "lignes_commande" + File.separator + "windows" + File.separator + "1_directions.bat")
            phase = File(libdart_auxdata, "windows" + File.separator + "tools" + File.separator + "lignes_commande" + File.separator + "windows" + File.separator + "2_phase.bat")
            maket = File(libdart_auxdata, "windows" + File.separator + "tools" + File.separator + "lignes_commande" + File.separator + "windows" + File.separator + "3_maket.bat")
            dart = File(libdart_auxdata, "windows" + File.separator + "tools" + File.separator + "lignes_commande" + File.separator + "windows" + File.separator + "4_dart.bat")
            dart_home = File(libdart_auxdata, "windows" + File.separator + "dart" + File.separator + "bin")
            dart_local = File(libdart_auxdata, "windows" + File.separator + "dart_local")
            
        #Cheat, copy Simulation folder form auxdata install dir to defined output folder. When it's clear how to create the
        #inputs for dart, delete these lines and replace it with the input creation functions..
        
        self.copy(simu_folder, File(request.getParameter("output_folder").getValueAsText() + File.separator + "3d_VegLab_simu"))
        
        simu_input = File(request.getParameter("output_folder").getValueAsText() + File.separator + "3D_VegLab_simu" + File.separator + "input")
        
        if (self.isUnix()):
            #Cheat you have to overwrite the environment variables of dart in order to specify an simulation input
            #folder, which is not in the DART_LOCAL directory. At the moment this cmd just works on an external installation
            #of dart on the machine. Need to figure out, how to overwrite these environments (they get set, when LancementDARTComplet.sh is called)
            self._logger.info("running dart with default input from local installation...")
            cmd = exec_file.getAbsolutePath() + " 3D_VegLab_simu"
            self._logger.info("Command for running dart: " + cmd)
            pb = ProcessBuilder(["sh", "-c", cmd])
            pb.directory(exec_file.getParentFile())
            env = pb.environment()
            env.put("DART_HOME", dart_home.getAbsolutePath())
            env.put("DART_LOCAL", dart_local.getAbsolutePath())
            path = env.get("PATH")
            path = path + File.pathSeparator + dart_home.getAbsolutePath() + File.pathSeparator + dart_home.getAbsolutePath() + File.separator + "hapke" 
            path = path + File.pathSeparator + dart_home.getAbsolutePath() + File.separator + "prospect"
            env.put("PATH", path)
            ld_library = env.get("LD_LIBRARY_PATH")
            ld_library = ld_library + File.pathSeparator + dart_home.getAbsolutePath()
            env.put("LD_LIBRARY_PATH", ld_library)
            env.put("DART_JAVA_MAX_MEMORY", "601m")
            pb.redirectErrorStream(True)
            
            try:
                proc = pb.start()
                self.exitVal = proc.waitFor()
                br = BufferedReader(InputStreamReader(proc.getInputStream()))
                self.line = br.readLine()
                while self.line != None:
                    print '>', self.line.encode('ascii', 'ignore')
                    self.error = self.line.encode('ascii', 'ignore')
                    self.line = br.readLine()
                if (self.exitVal != 0):
                    self._logger.severe("An error occured while trying to run Dart: Exit Value: " + self.exitVal + "Error Message: " + self.error)
            except IOException, e:
                self._logger.severe("ERROR: " + e.getMessage())
                raise RuntimeException(e.getMessage())
        
        
        
        
           
           
    def isWindows(self):
        os = System.getProperty("os.name").lower()
        return (os.find( "win" ) >= 0)
    
    def isUnix(self):
        os = System.getProperty("os.name").lower()
        return (os.find( "nix" ) >= 0 or os.find( "nux" ) >= 0)
    
    def isMac(self):
        os = System.getProperty("os.name").lower()
        return (os.find( "mac" ) >= 0)
    
    def copy(self, source, destination):
        try:
            if (source.isDirectory()):
                self.copyDirectory(source, destination)
            else:
                self.copyFile(source, destination)
        except IOException, e:
            self._logger.severe("An error occured when trying to copy " + source.getAbsolutePath() + " to " + destination.getAbsolutePath())
            self._logger.severe("Error Message: " + e.getMessage())
            raise IOException(e)
    
    def copyDirectory(self, source, destination):
        try:
            destination.mkdirs()
            list = source.listFiles()
           
            for file in list:
               if(file.isDirectory()):
                   self.copyDirectory(file, File(destination, file.getName()))
               else:
                   self.copyFile(file, File(destination, file.getName()))
                   
        except IOException, e:
            self._logger.severe("An error occured when trying to copy " + source.getAbsolutePath() + " to " + destination.getAbsolutePath())
            self._logger.severe("Error Message: " + e.getMessage())
            raise IOException(e)
                   
    def copyFile(self, source, destination):
        try:
            sourceChannel = FileInputStream(source).getChannel()
            targetChannel = FileOutputStream(destination).getChannel()
            sourceChannel.transferTo(0, sourceChannel.size(), targetChannel)
            sourceChannel.close()
            targetChannel.close()
        except IOException, e:
            self._logger.severe("An error occured when trying to copy " + source.getAbsolutePath() + " to " + destination.getAbsolutePath())
            self._logger.severe("Error Message: " + e.getMessage())
            raise IOException(e)
        
        

class VLabUiImpl(IVLabProcessorUi):
    
    def __init__(self):
        self._reqElemFac = VLabRequestElementFactory() #before: VLabRequestElementFactory.getInstance()
        self._requestFile = File("")
        self.STANDARD_INSETS_TOP = 3
        self.LARGE_INSETS_TOP = self.STANDARD_INSETS_TOP + 15
        #VLabConstants = VLabConstants()
        
        
    def getFactory(self):
        return self._reqElemFac
    
    def getGuiComponent(self):
        guiComponent = self.createTabbedPane()
        #sets the main window size
        VLabUi.setWindowSize(700, 900)
        return guiComponent
    
    def setRequests(self, requests):
        if (not requests.isEmpty()):
            print "request not empty!"
            for i in range(requests.size()):
                request = requests.elementAt(i)
                if (request == None):
                    continue;
                if (str(VLabConstants.REQUEST_TYPE) == request.getType()):
                    self.setRequest(request);
                    break;
                
            
        else:
            self.setDefaultRequests()
            
    def setRequest(self, request):
        print "setRequest got called"
        self._requestFile = request.getFile()
        print self._requestFile.getAbsolutePath()
        outputProductAt = request.getOutputProductAt(0)
        if (outputProductAt != None):
            self._paramOutputProduct.setValueAsText(outputProductAt.getFilePath(), None)
        
        self.updateParameters(request)
        
        numParameters = request.getNumParameters()
        
        parameters = request.getAllParameters()
        for i in range(numParameters):
            print parameters[i].getName() + " / " + str(parameters[i].getValue())
            
            
            
        
        #numInputProducts = request.getNumInputProducts()
        #inputFiles = ArrayList(numInputProducts)
        #for i in range(numInputProducts):
        #    inputFiles.add(File(request.getInputProductAt(i).getFilePath))
        
        #setProductDefinitionAndProcessingParameters(request.getAllParameters())
        
        self.updateLogParameter(request)
        
    def updateParameters(self, request):
        print "updateParameters got called."
        self._paramFM3dScene.setValue(request.getParameter(VLabConstants.PARAM_NAME_3D_SCENE).getValue())
        self._paramFMRTProcessor.setValue(request.getParameter(VLabConstants.PARAM_NAME_RT_PROCESSOR).getValue())
        self._paramSensor.setValue(request.getParameter(VLabConstants.PARAM_NAME_SENSORS).getValue())
        self._paramBands.setValue(request.getParameter(VLabConstants.PARAM_NAME_SPECCHAR_BANDS).getValue())
        self._paramViewingZenith.setValue(float(request.getParameter(VLabConstants.PARAM_NAME_VIEWING_ZENITH).getValue()))
        self._paramViewingAzimuth.setValue(float(request.getParameter(VLabConstants.PARAM_NAME_VIEWING_AZIMUTH).getValue()))
        self._paramIlluminationZenith.setValue(float(request.getParameter(VLabConstants.PARAM_NAME_ILLUMINATION_ZENITH).getValue()))
        self._paramIlluminationAzimuth.setValue(float(request.getParameter(VLabConstants.PARAM_NAME_ILLUMINATION_AZIMUTH).getValue()))
        self._paramScenePixel.setValue(int(request.getParameter(VLabConstants.PARAM_NAME_SCENE_PIXEL).getValue()))
        self._paramSceneXC.setValue(float(request.getParameter(VLabConstants.PARAM_NAME_SCENE_XC).getValue()))
        self._paramSceneYC.setValue(float(request.getParameter(VLabConstants.PARAM_NAME_SCENE_YC).getValue()))
        self._paramSceneXW.setValue(float(request.getParameter(VLabConstants.PARAM_NAME_SCENE_XW).getValue()))
        self._paramSceneYW.setValue(float(request.getParameter(VLabConstants.PARAM_NAME_SCENE_YW).getValue()))
        self._paramAtmosphereDay.setValue(int(request.getParameter(VLabConstants.PARAM_NAME_ATMOSPHERE_DAY).getValue()))
        self._paramAtmosphereLat.setValue(float(request.getParameter(VLabConstants.PARAM_NAME_ATMOSPHERE_LAT).getValue()))
        self._paramAtmosphereLong.setValue(float(request.getParameter(VLabConstants.PARAM_NAME_ATMOSPHERE_LONG).getValue()))
        self._paramAtmosphereCO2.setValue(request.getParameter(VLabConstants.PARAM_NAME_ATMOSPHERE_CO2).getValue())
        self._paramAtmosphereAerosol.setValue(request.getParameter(VLabConstants.PARAM_NAME_ATMOSPHERE_AEROSOL).getValue())
        self._paramAtmosphereWater.setValue(request.getParameter(VLabConstants.PARAM_NAME_ATMOSPHERE_WATER).getValue())
        self._paramAtmosphereOzone.setValue(request.getParameter(VLabConstants.PARAM_NAME_ATMOSPHERE_OZONE).getValue())
        self._paramFMOutputPrefix.setValue(request.getParameter(VLabConstants.PARAM_NAME_OUTPUT_PREFIX).getValue())
        if(request.getParameter(VLabConstants.PARAM_NAME_IMAGE_FILE).getValue() == "false"):
            self._paramFMImageFile.setValue(False)
        elif(request.getParameter(VLabConstants.PARAM_NAME_IMAGE_FILE).getValue() == "true"):
            self._paramFMImageFile.setValue(True)
        if(request.getParameter(VLabConstants.PARAM_NAME_ASCII_FILE).getValue() == "false"):
            self._paramFMAsciiFile.setValue(False)
        elif(request.getParameter(VLabConstants.PARAM_NAME_ASCII_FILE).getValue() == "true"):
            self._paramFMAsciiFile.setValue(True)
        self._paramFMOutputFolder.setValue(request.getParameter(VLabConstants.PARAM_NAME_OUTPUT_FOLDER).getValue())
    
        #Parameters in DHP Tab
        self._paramDHP3dScene.setValue(request.getParameter(VLabConstants.PARAM_NAME_DHP_3D_SCENE).getValue())
        self._paramDHPRTProcessor.setValue(request.getParameter(VLabConstants.PARAM_NAME_DHP_RT_PROCESSOR).getValue())
        self._paramResolution.setValue(request.getParameter(VLabConstants.PARAM_NAME_RESOLUTION).getValue())
        self._paramDHPLocationX.setValue(float(request.getParameter(VLabConstants.PARAM_NAME_LOCATION_X).getValue()))
        self._paramDHPLocationY.setValue(float(request.getParameter(VLabConstants.PARAM_NAME_LOCATION_Y).getValue()))
        self._paramDHPZenith.setValue(float(request.getParameter(VLabConstants.PARAM_NAME_DHP_PROP_ZENITH).getValue()))
        self._paramDHPAzimuth.setValue(float(request.getParameter(VLabConstants.PARAM_NAME_DHP_PROP_AZIMUTH).getValue()))
        self._paramDHPOrientation.setValue(float(request.getParameter(VLabConstants.PARAM_NAME_IMAGING_PLANE_ORIENTATION).getValue()))
        self._paramDHPHeight.setValue(float(request.getParameter(VLabConstants.PARAM_NAME_IMAGING_PLANE_HEIGHT).getValue()))
        self._paramDHPOutputPrefix.setValue(request.getParameter(VLabConstants.PARAM_NAME_DHP_OUTPUT_PREFIX).getValue())
        if(request.getParameter(VLabConstants.PARAM_NAME_DHP_IMAGE_FILE).getValue() == "false"):
            self._paramDHPImageFile.setValue(False)
        elif(request.getParameter(VLabConstants.PARAM_NAME_DHP_IMAGE_FILE).getValue() == "true"):
            self._paramDHPImageFile.setValue(True)
        if(request.getParameter(VLabConstants.PARAM_NAME_DHP_ASCII_FILE).getValue() == "false"):
            self._paramDHPAsciiFile.setValue(False)
        elif(request.getParameter(VLabConstants.PARAM_NAME_DHP_ASCII_FILE).getValue() == "true"):
            self._paramDHPAsciiFile.setValue(True)
        self._paramDHPOutputFolder.setValue(request.getParameter(VLabConstants.PARAM_NAME_DHP_OUTPUT_FOLDER).getValue())
        
    
    def updateLogParameter(self, request):
        prefixParam = request.getParameter(ProcessorConstants.LOG_PREFIX_PARAM_NAME)
        if (prefixParam != None):
            self._logPrefixParameter.setValue(prefixParam.getValue(), None)
        
        logOutputParam = request.getParameter(ProcessorConstants.LOG_TO_OUTPUT_PARAM_NAME)
        if (logOutputParam != None):
            self._logToOutputParameter.setValue(logOutputParam.getValue(), None)
        
        
    
    def getRequests(self):
        requests = Vector()
        requests.add(self.getRequest())
        return requests
    
    def getRequest(self):
        request = Request()
        request.setFile(self._requestFile)
        request.setType(VLabConstants.REQUEST_TYPE)

        outputFile = self._paramOutputProduct.getValueAsText()
        request.addOutputProduct(ProcessorUtils.createProductRef(outputFile, DimapProductConstants.DIMAP_FORMAT_NAME));
        
        request.addParameter(self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_3D_SCENE, self._paramFM3dScene.getValueAsText()))
        request.addParameter(self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_DHP_3D_SCENE, self._paramDHP3dScene.getValueAsText()))
        request.addParameter(self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_RT_PROCESSOR, self._paramFMRTProcessor.getValueAsText()))
        request.addParameter(self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_DHP_RT_PROCESSOR, self._paramDHPRTProcessor.getValueAsText()))
        request.addParameter(self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_SENSORS, self._paramSensor.getValueAsText()))
        request.addParameter(self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_SPECCHAR_BANDS, self._paramBands.getValueAsText()))
        request.addParameter(self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_VIEWING_ZENITH, self._paramViewingZenith.getValueAsText()))
        request.addParameter(self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_VIEWING_AZIMUTH, self._paramViewingAzimuth.getValueAsText()))
        request.addParameter(self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_ILLUMINATION_ZENITH, self._paramIlluminationZenith.getValueAsText()))
        request.addParameter(self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_ILLUMINATION_AZIMUTH, self._paramIlluminationAzimuth.getValueAsText()))
        request.addParameter(self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_SCENE_PIXEL, self._paramScenePixel.getValueAsText()))
        request.addParameter(self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_SCENE_XC, self._paramSceneXC.getValueAsText()))
        request.addParameter(self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_SCENE_XW, self._paramSceneXW.getValueAsText()))
        request.addParameter(self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_SCENE_YC, self._paramSceneYC.getValueAsText()))
        request.addParameter(self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_SCENE_YW, self._paramSceneYW.getValueAsText()))
        request.addParameter(self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_ATMOSPHERE_DAY, self._paramAtmosphereDay.getValueAsText()))
        request.addParameter(self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_ATMOSPHERE_LAT, self._paramAtmosphereLat.getValueAsText()))
        request.addParameter(self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_ATMOSPHERE_LONG, self._paramAtmosphereLong.getValueAsText()))
        request.addParameter(self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_ATMOSPHERE_CO2, self._paramAtmosphereCO2.getValueAsText()))
        request.addParameter(self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_ATMOSPHERE_AEROSOL, self._paramAtmosphereAerosol.getValueAsText()))
        request.addParameter(self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_ATMOSPHERE_WATER, self._paramAtmosphereWater.getValueAsText()))
        request.addParameter(self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_ATMOSPHERE_OZONE, self._paramAtmosphereOzone.getValueAsText()))
        request.addParameter(self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_IMAGE_FILE, self._paramFMImageFile.getValueAsText()))
        request.addParameter(self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_ASCII_FILE, self._paramFMAsciiFile.getValueAsText()))
        request.addParameter(self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_OUTPUT_PREFIX, self._paramFMOutputPrefix.getValueAsText()))
        request.addParameter(self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_OUTPUT_FOLDER, self._paramFMOutputFolder.getValueAsText()))
        
        
        #add request from DHP Simulation panel
        request.addParameter(self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_RESOLUTION, self._paramResolution.getValueAsText()))
        request.addParameter(self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_LOCATION_X, self._paramDHPLocationX.getValueAsText()))
        request.addParameter(self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_LOCATION_Y, self._paramDHPLocationY.getValueAsText()))
        request.addParameter(self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_DHP_PROP_ZENITH, self._paramDHPZenith.getValueAsText()))
        request.addParameter(self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_DHP_PROP_AZIMUTH, self._paramDHPAzimuth.getValueAsText()))
        request.addParameter(self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_IMAGING_PLANE_ORIENTATION, self._paramDHPOrientation.getValueAsText()))
        request.addParameter(self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_IMAGING_PLANE_HEIGHT, self._paramDHPHeight.getValueAsText()))
        request.addParameter(self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_DHP_IMAGE_FILE, self._paramDHPImageFile.getValueAsText()))
        request.addParameter(self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_DHP_ASCII_FILE, self._paramDHPAsciiFile.getValueAsText()))
        request.addParameter(self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_DHP_OUTPUT_PREFIX, self._paramDHPOutputPrefix.getValueAsText()))
        request.addParameter(self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_DHP_OUTPUT_FOLDER, self._paramDHPOutputFolder.getValueAsText()))
        
        request.addParameter(self._logToOutputParameter);
        request.addParameter(self._logPrefixParameter);
        
        
        
        return request;



            
    def setDefaultRequests(self):
        #not sure if this is realy needed... probably yes, but trying it without...
        #self.disposeExampleProduct()
        print "set DefaultRequests got called"
        self.setDefaultRequest()
        
    def setDefaultRequest(self):
        print "setDefaultRequest got called"
        self._requestFile = None
        #self._inputProductEditor.setFiles(ArrayList(1))
        outputProductFile = self._paramOutputProduct.getValue()
        print "outputProductFile got init"
        if (outputProductFile != None and outputProductFile.getParentFile() != None):
            parentFile = outputProductFile.getParentFile()
            self._paramOutputProduct.setValue(File(parentFile, VLabConstants.DEFAULT_OUTPUT_PRODUCT_NAME), None)
        else:
            self._paramOutputProduct.setDefaultValue()

        #self._paramProjectionName.setDefaultValue();
        print "if else ok"
        self._paramFM3dScene.setDefaultValue()

        #_paramWestLon.setDefaultValue();
        #_paramEastLon.setDefaultValue();

        #final float northLatDefault = (Float) _paramNorthLat.getProperties().getDefaultValue();
        #final float southLatCurrent = (Float) _paramSouthLat.getValue();
        #if (northLatDefault < southLatCurrent) {
        #    _paramSouthLat.setDefaultValue();
        #    _paramNorthLat.setDefaultValue();
        #} else {
        #    _paramNorthLat.setDefaultValue();
        #    _paramSouthLat.setDefaultValue();
        #}

        #self._paramUpdateMode.setDefaultValue()
        #print "setDefaultValue ok"
        #self._paramUpdateMode.setUIEnabled(False)
        #print "setUIEnabled ok"
        #self._paramConditionsOperator.setDefaultValue()
        
        
        print "setDefaultRequest is finished..."

        #_paramOrthorectify.setDefaultValue();
        #_paramElevation.setDefaultValue();
        
     
        
    def createTabbedPane(self):
        print "createTabbedPane got called"
        self.initParameters()
        print "initParameters finished"
        panel = swing.JPanel(awt.BorderLayout())
        tabbedPane = swing.JTabbedPane()
        self.addTabs(tabbedPane)
        panel.add(tabbedPane, awt.BorderLayout.NORTH)
        panel.add(swing.JLabel("  "), awt.BorderLayout.CENTER)
#        panel.add(_paramUpdateMode.getEditor().getEditorComponent(), BorderLayout.SOUTH);
        print "Tabbed Pane has been created and ready to return"
        return panel;
    
    def addTabs(self, panel):
        print "addTabs got called"
        panel.add("Forward Modeling", self.createForwardModelingPanel())
        panel.add("DHP Simulation", self.createDHPSimulationPanel())
        
    def createForwardModelingPanel(self):
        
       # print "inputProductEditor should get init now"
       # self._inputProductEditor = FileArrayEditor(parent, "Input products")
       # listener = FileArrayEditor.FileArrayEditorListener(actionPerformed=self.updatedList(files))
       #    
       # _inputProductEditor.setListener(listener);

        

        print "createForwardModelingPanel got called"
        panel = GridBagUtils.createPanel()
        print "createPanel"
        gbc = GridBagUtils.createDefaultConstraints()
        print "createConstraints"
        gbc.gridy = 1
        gbc.weightx = 1
        gbc.fill = awt.GridBagConstraints.HORIZONTAL
        gbc.insets.top = self.LARGE_INSETS_TOP
        
        print "initialised"
        
        gbc.gridy = gbc.gridy + 1
        gbc.insets.top = self.LARGE_INSETS_TOP
        panel.add(self.createFMHeaderPanel(), gbc)
        
        print "FMHeaderPanel got created"
        
        gbc.gridy = gbc.gridy + 1
        gbc.insets.top = self.LARGE_INSETS_TOP
        panel.add(self.createSpectralCharacteristics(), gbc)
        
        gbc.gridy = gbc.gridy + 1
        gbc.insets.top = self.LARGE_INSETS_TOP
        panel.add(self.createViewingCharacteristics(), gbc)

        gbc.gridy = gbc.gridy + 1
        gbc.insets.top = self.LARGE_INSETS_TOP
        panel.add(self.createIlluminationCharacteristics(), gbc)

        gbc.gridy = gbc.gridy + 1
        gbc.insets.top = self.LARGE_INSETS_TOP
        panel.add(self.createSceneProportions(), gbc)
        
        gbc.gridy = gbc.gridy + 1
        gbc.insets.top = self.LARGE_INSETS_TOP
        panel.add(self.createAtmosphericProperties(), gbc)
        
        gbc.gridy = gbc.gridy + 1
        gbc.insets.top = self.LARGE_INSETS_TOP
        panel.add(self.createFMFooterPanel(), gbc)
        
        gbc.gridy = gbc.gridy + 1
        gbc.insets.top = self.LARGE_INSETS_TOP
        gbc.weighty = 999
        panel.add(swing.JLabel(""), gbc)

        return panel
    
    def createDHPSimulationPanel(self):
        
        print "createDHPSimulationPanel got called"
        panel = GridBagUtils.createPanel()
        print "createPanel"
        gbc = GridBagUtils.createDefaultConstraints()
        print "createConstraints"
        gbc.gridy = 1
        gbc.weightx = 1
        gbc.fill = awt.GridBagConstraints.HORIZONTAL
        gbc.insets.top = self.LARGE_INSETS_TOP
        
        print "initialised"
        
        gbc.gridy = gbc.gridy + 1
        gbc.insets.top = self.LARGE_INSETS_TOP
        panel.add(self.createDHPHeaderPanel(), gbc)
        
        print "DHPHeaderPanel got created"
        
        gbc.gridy = gbc.gridy + 1
        gbc.insets.top = self.LARGE_INSETS_TOP
        panel.add(self.createDHPLocation(), gbc)
        
        gbc.gridy = gbc.gridy + 1
        gbc.insets.top = self.LARGE_INSETS_TOP
        panel.add(self.createDHPProperties(), gbc)

        gbc.gridy = gbc.gridy + 1
        gbc.insets.top = self.LARGE_INSETS_TOP
        panel.add(self.createDHPImagingPlane(), gbc)
        print "DHPImagingPlane got created"

        gbc.gridy = gbc.gridy + 1
        print "1"
        gbc.insets.top = self.LARGE_INSETS_TOP
        print"2"
        panel.add(self.createOutputParameters(), gbc)
        
        gbc.gridy = gbc.gridy + 1
        gbc.insets.top = self.LARGE_INSETS_TOP
        gbc.weighty = 999
        panel.add(swing.JLabel(""), gbc)

        return panel
    
    def createDHPHeaderPanel(self):
        print "createDHPHeaderPanel got called"
        panel = GridBagUtils.createPanel()
        panel.setBorder(UIUtils.createGroupBorder("Model Selection"))
        gbc = GridBagUtils.createDefaultConstraints()
        gbc.gridy = 1
        gbc.weightx = 1
        gbc.insets.top = self.STANDARD_INSETS_TOP
#       gbc.gridwidth = 1

        gbc.gridy = gbc.gridy + 1
        panel.add(self._paramDHP3dScene.getEditor().getLabelComponent(), gbc)
#        gbc.anchor = awt.GridBagConstraints.WEST
        gbc.weightx = 40
        panel.add(self._paramDHP3dScene.getEditor().getComponent(), gbc)
        
        gbc.gridy = gbc.gridy + 1
        gbc.weightx = 1
        panel.add(self._paramDHPRTProcessor.getEditor().getLabelComponent(), gbc)
#        gbc.anchor = awt.GridBagConstraints.WEST
        gbc.weightx = 40
        panel.add(self._paramDHPRTProcessor.getEditor().getComponent(), gbc)
        
        gbc.gridy = gbc.gridy + 1
        gbc.weightx = 1
        panel.add(self._paramResolution.getEditor().getLabelComponent(), gbc)
        gbc.weightx = 40
        panel.add(self._paramResolution.getEditor().getComponent(), gbc)
        
        print "DHPHeaderPanel got init"
        
        return panel
    
    def createDHPLocation(self):
        print "createDHPLocation got called"
        panel = GridBagUtils.createPanel()
        panel.setBorder(UIUtils.createGroupBorder("DHP Location"))
        gbc = GridBagUtils.createDefaultConstraints()
        gbc.gridy = 1
        
        gbc.insets.top = self.STANDARD_INSETS_TOP
        gbc.gridwidth = 4
        
        
        gbc.weightx = 0.1
        gbc.gridy = gbc.gridy + 1
        panel.add(self._paramDHPLocationX.getEditor().getLabelComponent(), gbc)
        gbc.weightx = 1
        gbc.fill = GridBagConstraints.NONE
        panel.add(self._paramDHPLocationX.getEditor().getComponent(), gbc)
        print "Location X ok"
        
        gbc.weightx = 0.1
        gbc.fill = GridBagConstraints.NONE
        panel.add(self._paramDHPLocationY.getEditor().getLabelComponent(), gbc)
        gbc.weightx = 1
        gbc.fill = GridBagConstraints.NONE
        panel.add(self._paramDHPLocationY.getEditor().getComponent(), gbc)
        
        print "DHP Location got init"
        
        return panel
    
    def createDHPProperties(self):
        print "createDHPProperties got called"
        panel = GridBagUtils.createPanel()
        panel.setBorder(UIUtils.createGroupBorder("DHP Properties"))
        gbc = GridBagUtils.createDefaultConstraints()
        gbc.gridy = 1
        gbc.weightx = 0.1
        gbc.insets.top = self.STANDARD_INSETS_TOP
        gbc.gridwidth = 4
        
        gbc.gridy = gbc.gridy + 1
        panel.add(self._paramDHPZenith.getEditor().getLabelComponent(), gbc)
        gbc.weightx = 1
        panel.add(self._paramDHPZenith.getEditor().getComponent(), gbc)
        
        gbc.weightx = 0.1
        panel.add(self._paramDHPAzimuth.getEditor().getLabelComponent(), gbc)
        gbc.weightx = 1
        panel.add(self._paramDHPAzimuth.getEditor().getComponent(), gbc)
        
        print "DHP Properties got init"
        
        return panel
        
    def createDHPImagingPlane(self):
        print "createDHPImagingPlane got called"
        panel = GridBagUtils.createPanel()
        panel.setBorder(UIUtils.createGroupBorder("DHP Imaging Plane"))
        gbc = GridBagUtils.createDefaultConstraints()
        gbc.gridy = 1
        gbc.weightx = 0.1
        gbc.insets.top = self.STANDARD_INSETS_TOP
        gbc.gridwidth = 4
        
        gbc.gridy = gbc.gridy + 1
        panel.add(self._paramDHPOrientation.getEditor().getLabelComponent(), gbc)
        gbc.weightx = 1
        panel.add(self._paramDHPOrientation.getEditor().getComponent(), gbc)
        
        gbc.weightx = 0.1
        panel.add(self._paramDHPHeight.getEditor().getLabelComponent(), gbc)
        gbc.weightx = 1
        panel.add(self._paramDHPHeight.getEditor().getComponent(), gbc)
        
        print "DHP Imaging Plane got init"
        
        return panel
    
    def createOutputParameters(self):
        print "createOutputParameters got called"
        panel = GridBagUtils.createPanel()
#        panel.setBorder(UIUtils.createGroupBorder("Projection"))
        gbc = GridBagUtils.createDefaultConstraints()
        gbc.gridy = 1
        gbc.weightx = 1
        gbc.insets.top = self.STANDARD_INSETS_TOP
#        gbc.gridwidth = 1

        gbc.gridy = gbc.gridy + 1
        panel.add(self._paramDHPOutputPrefix.getEditor().getLabelComponent(), gbc)
#        gbc.anchor = awt.GridBagConstraints.WEST
        gbc.weightx = 40
        panel.add(self._paramDHPOutputPrefix.getEditor().getComponent(), gbc)
        
        gbc.gridy = gbc.gridy + 1
        gbc.weightx = 0.1
        panel.add(self._paramDHPOutputFolder.getEditor().getLabelComponent(), gbc)
        gbc.weightx = 0.1
        panel.add(self._paramDHPOutputFolder.getEditor().getComponent(), gbc)
        gbc.weightx = 0.1
        self.browse_button_dhp = swing.JButton("Browse", actionPerformed=self.browse_dhp) 
        panel.add(self.browse_button_dhp, gbc)
        
        gbc.gridy = gbc.gridy + 1
#        gbc.gridwidth = 2
        gbc.weightx = 1
        panel.add(self._paramDHPImageFile.getEditor().getComponent(), gbc)
        panel.add(self._paramDHPAsciiFile.getEditor().getComponent(), gbc)

        return panel

        
        
    def createFMHeaderPanel(self):
        print "createFMHeaderPanel got called"
        panel = GridBagUtils.createPanel()
        panel.setBorder(UIUtils.createGroupBorder("Model Selection"))
        gbc = GridBagUtils.createDefaultConstraints()
        gbc.gridy = 1
        gbc.weightx = 1
        gbc.insets.top = self.STANDARD_INSETS_TOP
#       gbc.gridwidth = 1

        gbc.gridy = gbc.gridy + 1
        panel.add(self._paramFM3dScene.getEditor().getLabelComponent(), gbc)
#        gbc.anchor = awt.GridBagConstraints.WEST
        gbc.weightx = 40
        panel.add(self._paramFM3dScene.getEditor().getComponent(), gbc)
        
        gbc.gridy = gbc.gridy + 1
        gbc.weightx = 1
        panel.add(self._paramFMRTProcessor.getEditor().getLabelComponent(), gbc)
#        gbc.anchor = awt.GridBagConstraints.WEST
        gbc.weightx = 40
        panel.add(self._paramFMRTProcessor.getEditor().getComponent(), gbc)
        
        return panel
    
    def createSpectralCharacteristics(self):
        print "createSpectralChar got called"
        panel = GridBagUtils.createPanel()
        panel.setBorder(UIUtils.createGroupBorder("Spectral Characteristics"))
        gbc = GridBagUtils.createDefaultConstraints()
        gbc.gridy = 1
        gbc.weightx = 1
        gbc. insets.top = self.STANDARD_INSETS_TOP
        gbc.gridwidth = 1
        print "SpectralChar inits stuff..."
        
        gbc.gridy = gbc.gridy + 1
        panel.add(self._paramSensor.getEditor().getLabelComponent(), gbc)
        gbc.weightx = 40
        panel.add(self._paramSensor.getEditor().getComponent(), gbc)
        print "Sensor got init"
        
        gbc.weightx = 1
        gbc.gridy = gbc.gridy + 1
        panel.add(self._paramBands.getEditor().getLabelComponent(), gbc)
        gbc.weightx = 40
        panel.add(self._paramBands.getEditor().getComponent(), gbc)
        
        print "bands got init"
        
        return panel
    
    def createViewingCharacteristics(self):
        print "createViewingChar got called"
        panel = GridBagUtils.createPanel()
        panel.setBorder(UIUtils.createGroupBorder("Viewing Characteristics"))
        gbc = GridBagUtils.createDefaultConstraints()
        gbc.gridy = 1
        gbc.weightx = 1
        gbc.insets.top = self.STANDARD_INSETS_TOP
        gbc.gridwidth = 1

        gbc.gridy = gbc.gridy + 1
        panel.add(self._paramViewingZenith.getEditor().getLabelComponent(), gbc)
#       gbc.anchor = awt.GridBagConstraints.WEST
        gbc.weightx = 40
        panel.add(self._paramViewingZenith.getEditor().getComponent(), gbc)

        gbc.weightx = 1
#        gbc.anchor = awt.GridBagConstraints.EAST;
        panel.add(self._paramViewingAzimuth.getEditor().getLabelComponent(), gbc)
        gbc.weightx = 40
        panel.add(self._paramViewingAzimuth.getEditor().getComponent(), gbc)

        return panel
    
    def createIlluminationCharacteristics(self):
        print "createIllumChar got called"
        panel = GridBagUtils.createPanel()
        panel.setBorder(UIUtils.createGroupBorder("Illumination Characteristics"))
        gbc = GridBagUtils.createDefaultConstraints()
        gbc.gridy = 1
        gbc.weightx = 1
        gbc.insets.top = self.STANDARD_INSETS_TOP;
        gbc.gridwidth = 1

        gbc.gridy = gbc.gridy + 1
        panel.add(self._paramIlluminationZenith.getEditor().getLabelComponent(), gbc)
#        gbc.anchor = awt.GridBagConstraints.WEST;
        gbc.weightx = 40
        panel.add(self._paramIlluminationZenith.getEditor().getComponent(), gbc)

        gbc.weightx = 1
#        gbc.anchor = awt.GridBagConstraints.EAST;
        panel.add(self._paramIlluminationAzimuth.getEditor().getLabelComponent(), gbc)
        gbc.weightx = 40
        panel.add(self._paramIlluminationAzimuth.getEditor().getComponent(), gbc)

        return panel
    
    def createSceneProportions(self):
        print "createSceneProps got called"
        panel = GridBagUtils.createPanel()
        panel.setBorder(UIUtils.createGroupBorder("Scene Proportions"))
        gbc = GridBagUtils.createDefaultConstraints()
        gbc.gridy = 1
        gbc.weightx = 1
        gbc.insets.top = self.STANDARD_INSETS_TOP
        gbc.gridwidth = 1

        gbc.gridy = gbc.gridy + 1
        panel.add(self._paramScenePixel.getEditor().getLabelComponent(), gbc)
#        gbc.anchor = awt.GridBagConstraints.WEST;
        gbc.weightx = 40
        panel.add(self._paramScenePixel.getEditor().getComponent(), gbc)

        gbc.weightx = 1
        gbc.gridy = gbc.gridy + 1
        panel.add(swing.JLabel(""), gbc)
        
        gbc.gridy = gbc.gridy + 1
#        gbc.anchor = awt.GridBagConstraints.EAST;
#        gbc.weightx = 40;
        panel.add(self._paramSceneXC.getEditor().getLabelComponent(), gbc)
        gbc.weightx = 40
        panel.add(self._paramSceneXC.getEditor().getComponent(), gbc)
        gbc.weightx = 1
        panel.add(self._paramSceneYC.getEditor().getLabelComponent(), gbc)
        gbc.weightx = 40
        panel.add(self._paramSceneYC.getEditor().getComponent(), gbc)
        
        gbc.weightx = 1
        gbc.gridy = gbc.gridy + 1
        panel.add(self._paramSceneXW.getEditor().getLabelComponent(), gbc)
        gbc.weightx = 40
        panel.add(self._paramSceneXW.getEditor().getComponent(), gbc)
        gbc.weightx = 1
        panel.add(self._paramSceneYW.getEditor().getLabelComponent(), gbc)
        gbc.weightx = 40
        panel.add(self._paramSceneYW.getEditor().getComponent(), gbc)

        return panel
    
    def createAtmosphericProperties(self):
        print "createAtmosph. Props got called"
        panel = GridBagUtils.createPanel()
        panel.setBorder(UIUtils.createGroupBorder("Atmospheric Properties"))
        gbc = GridBagUtils.createDefaultConstraints()
        gbc.gridy = 1
        gbc.weightx = 1
        gbc.insets.top = self.STANDARD_INSETS_TOP
        gbc.gridwidth = 1

        gbc.gridy = gbc.gridy + 1
        panel.add(self._paramAtmosphereDay.getEditor().getLabelComponent(), gbc)
#        gbc.anchor = awt.GridBagConstraints.WEST;
        gbc.weightx = 40
        panel.add(self._paramAtmosphereDay.getEditor().getComponent(), gbc)

        gbc.weightx = 1
        gbc.gridy = gbc.gridy + 1
#        gbc.anchor = awt.GridBagConstraints.EAST
        panel.add(self._paramAtmosphereLat.getEditor().getLabelComponent(), gbc)
        gbc.weightx = 40
        panel.add(self._paramAtmosphereLat.getEditor().getComponent(), gbc)
        gbc.weightx = 1
        panel.add(self._paramAtmosphereLong.getEditor().getLabelComponent(), gbc)
        gbc.weightx = 40
        panel.add(self._paramAtmosphereLong.getEditor().getComponent(), gbc)

        gbc.weightx = 1
        gbc.gridy = gbc.gridy + 1
        panel.add(swing.JLabel(""), gbc)
        
        gbc.gridy = gbc.gridy + 1
        panel.add(self._paramAtmosphereCO2.getEditor().getLabelComponent(), gbc)
#        gbc.anchor = awt.GridBagConstraints.WEST
        gbc.weightx = 40
        panel.add(self._paramAtmosphereCO2.getEditor().getComponent(), gbc)
        
        gbc.weightx = 1
#        gbc.anchor = awt.GridBagConstraints.EAST
        panel.add(self._paramAtmosphereAerosol.getEditor().getLabelComponent(), gbc)
        gbc.weightx = 40
        panel.add(self._paramAtmosphereAerosol.getEditor().getComponent(), gbc)
        
        gbc.weightx = 1
        gbc.gridy = gbc.gridy + 1
        panel.add(self._paramAtmosphereWater.getEditor().getLabelComponent(), gbc)
#        gbc.anchor = awt.GridBagConstraints.WEST;
        gbc.weightx = 40
        panel.add(self._paramAtmosphereWater.getEditor().getComponent(), gbc)
        
        gbc.weightx = 1
#        gbc.anchor = awt.GridBagConstraints.EAST
        panel.add(self._paramAtmosphereOzone.getEditor().getLabelComponent(), gbc)
        gbc.weightx = 40
        panel.add(self._paramAtmosphereOzone.getEditor().getComponent(), gbc)
                
        return panel
    
    def createFMFooterPanel(self):
        print "createFMFotterPanel got called"
        panel = GridBagUtils.createPanel()
#        panel.setBorder(UIUtils.createGroupBorder("Projection"))
        gbc = GridBagUtils.createDefaultConstraints()
        gbc.gridy = 1
        gbc.weightx = 1
        gbc.insets.top = self.STANDARD_INSETS_TOP
#        gbc.gridwidth = 1

        gbc.gridy = gbc.gridy + 1
        panel.add(self._paramFMOutputPrefix.getEditor().getLabelComponent(), gbc)
#        gbc.anchor = awt.GridBagConstraints.WEST
        gbc.weightx = 40
        panel.add(self._paramFMOutputPrefix.getEditor().getComponent(), gbc)
        
        gbc.gridy = gbc.gridy + 1
        gbc.weightx = 0.1
        panel.add(self._paramFMOutputFolder.getEditor().getLabelComponent(), gbc)
        gbc.weightx = 0.1
        panel.add(self._paramFMOutputFolder.getEditor().getComponent(), gbc)
        gbc.weightx = 0.1
        self.browse_button = swing.JButton("Browse", actionPerformed=self.browse) 
        panel.add(self.browse_button, gbc)
        
        gbc.gridy = gbc.gridy + 1
#        gbc.gridwidth = 2
        gbc.weightx = 1
        panel.add(self._paramFMImageFile.getEditor().getComponent(), gbc)
        panel.add(self._paramFMAsciiFile.getEditor().getComponent(), gbc)

        return panel
    

        
    def initParameters(self):
        print "initParameters got called"
        self._labelWidthInfo = swing.JLabel("####")
        self._labelHeightInfo = swing.JLabel("####")
        self._labelCenterLatInfo = swing.JLabel("##°")
        self._labelCenterLonInfo = swing.JLabel("##°")

        try:
            #Parameters for FM Pane
            print "try statement got called"
            self._FM3dScenes = [""] * 2
            self._FM3dScenes[0] = "Laegeren"
            self._FM3dScenes[1] = "Default RAMI"
            print "Array has been initialised..."
            print self._FM3dScenes[0]
            Arrays.sort(self._FM3dScenes)
            print "Arrays.sort got called"
            self._paramFM3dScene = Parameter(VLabConstants.PARAM_NAME_3D_SCENE, VLabConstants.PARAM_DEFAULT_VALUE_3D_SCENE)
            self._paramFM3dScene.getProperties().setValueSet(self._FM3dScenes)
            self._paramFM3dScene.getProperties().setValueSetBound(True)
            self._paramFM3dScene.getProperties().setDefaultValue(VLabConstants.PARAM_DEFAULT_VALUE_3D_SCENE)
            self._paramFM3dScene.getProperties().setLabel("3D Scene")
            print "3dSenes got init"

            self. _FMRTProcessors = [""] * 3
            self._FMRTProcessors[0] = "librat"
            self._FMRTProcessors[1] = "dart"
            self._FMRTProcessors[2] = "libradtran"
            print self._FMRTProcessors[0]
            Arrays.sort(self._FMRTProcessors)
            self._paramFMRTProcessor = Parameter(VLabConstants.PARAM_NAME_RT_PROCESSOR, VLabConstants.PARAM_DEFAULT_VALUE_RT_PROCESSOR)
            self._paramFMRTProcessor.getProperties().setValueSet(self._FMRTProcessors)
            self._paramFMRTProcessor.getProperties().setValueSetBound(True)
            self._paramFMRTProcessor.getProperties().setDefaultValue(VLabConstants.PARAM_DEFAULT_VALUE_RT_PROCESSOR)
            self._paramFMRTProcessor.getProperties().setLabel("RT Processor")
            print "RTProcessor got init"
            
            self._Sensors = [""] * 2
            self._Sensors[0] = "Sentinel-2"
            self._Sensors[1] = "Sentinel-3"
            Arrays.sort(self._Sensors)
            self._paramSensor = Parameter(VLabConstants.PARAM_NAME_SENSORS, VLabConstants.PARAM_DEFAULT_VALUE_SENSORS)
            self._paramSensor.getProperties().setValueSet(self._Sensors)
            self._paramSensor.getProperties().setValueSetBound(True)
            self._paramSensor.getProperties().setDefaultValue(VLabConstants.PARAM_DEFAULT_VALUE_SENSORS)
            self._paramSensor.getProperties().setLabel("Sensor")
            print "Sensor got init"
            
            self._paramBands = self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_SPECCHAR_BANDS, None)
            
            self._paramViewingZenith = self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_VIEWING_ZENITH, None)
            self._paramViewingAzimuth = self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_VIEWING_AZIMUTH, None)
            self._paramIlluminationZenith = self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_ILLUMINATION_ZENITH, None)
            self._paramIlluminationAzimuth = self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_ILLUMINATION_AZIMUTH, None)
            self._paramScenePixel = self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_SCENE_PIXEL, None)
            self._paramSceneXC = self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_SCENE_XC, None)
            self._paramSceneYC = self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_SCENE_YC, None)
            self._paramSceneXW = self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_SCENE_XW, None)
            self._paramSceneYW = self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_SCENE_YW, None)
            self._paramAtmosphereDay = self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_ATMOSPHERE_DAY, None)
            self._paramAtmosphereLat = self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_ATMOSPHERE_LAT, None)
            self._paramAtmosphereLong = self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_ATMOSPHERE_LONG, None)

            self._CO2Profiles = [""]
            self._CO2Profiles[0] = "standard"
            Arrays.sort(self._CO2Profiles)
            self._paramAtmosphereCO2 = Parameter(VLabConstants.PARAM_NAME_ATMOSPHERE_CO2, VLabConstants.PARAM_DEFAULT_VALUE_ATMOSPHERE_CO2)
            self._paramAtmosphereCO2.getProperties().setValueSet(self._CO2Profiles)
            self._paramAtmosphereCO2.getProperties().setValueSetBound(True)
            self._paramAtmosphereCO2.getProperties().setDefaultValue(VLabConstants.PARAM_DEFAULT_VALUE_ATMOSPHERE_CO2)
            self._paramAtmosphereCO2.getProperties().setLabel("CO2 Profile")
            print "CO2 got init"
            
            self._AerosolProfiles = [""]
            self._AerosolProfiles[0] = "standard"
            Arrays.sort(self._AerosolProfiles)
            self._paramAtmosphereAerosol = Parameter(VLabConstants.PARAM_NAME_ATMOSPHERE_AEROSOL, VLabConstants.PARAM_DEFAULT_VALUE_ATMOSPHERE_AEROSOL)
            self._paramAtmosphereAerosol.getProperties().setValueSet(self._AerosolProfiles)
            self._paramAtmosphereAerosol.getProperties().setValueSetBound(True)
            self._paramAtmosphereAerosol.getProperties().setDefaultValue(VLabConstants.PARAM_DEFAULT_VALUE_ATMOSPHERE_AEROSOL)
            self._paramAtmosphereAerosol.getProperties().setLabel("Aerosol Profile")
            print "AerosolProfile got init"
            
            self._WaterProfiles = [""]
            self._WaterProfiles[0] = "standard"
            Arrays.sort(self._WaterProfiles)
            self._paramAtmosphereWater = Parameter(VLabConstants.PARAM_NAME_ATMOSPHERE_WATER, VLabConstants.PARAM_DEFAULT_VALUE_ATMOSPHERE_WATER)
            self._paramAtmosphereWater.getProperties().setValueSet(self._WaterProfiles)
            self._paramAtmosphereWater.getProperties().setValueSetBound(True)
            self._paramAtmosphereWater.getProperties().setDefaultValue(VLabConstants.PARAM_DEFAULT_VALUE_ATMOSPHERE_WATER)
            self._paramAtmosphereWater.getProperties().setLabel("Water Vapor")
            print "Water Profiles got init"
            
            self._OzoneProfiles = [""]
            self._OzoneProfiles[0] = "standard"
            Arrays.sort(self._OzoneProfiles)
            self._paramAtmosphereOzone = Parameter(VLabConstants.PARAM_NAME_ATMOSPHERE_OZONE, VLabConstants.PARAM_DEFAULT_VALUE_ATMOSPHERE_OZONE)
            self._paramAtmosphereOzone.getProperties().setValueSet(self._OzoneProfiles)
            self._paramAtmosphereOzone.getProperties().setValueSetBound(True)
            self._paramAtmosphereOzone.getProperties().setDefaultValue(VLabConstants.PARAM_DEFAULT_VALUE_ATMOSPHERE_OZONE)
            self._paramAtmosphereOzone.getProperties().setLabel("Ozone")
            print "Ozone got init"
            
            self._paramFMOutputPrefix = self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_OUTPUT_PREFIX, None)
            self._paramFMImageFile = self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_IMAGE_FILE, None)
            self._paramFMAsciiFile = self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_ASCII_FILE, None)
            print "Check boxes got init"
            
            
            #additional Parameters for DHP Panel
            self._DHP3dScenes = [""]
            self._DHP3dScenes[0] = "Laegeren"
            print "Array has been initialised..."
            print self._DHP3dScenes[0]
            Arrays.sort(self._DHP3dScenes)
            print "Arrays.sort got called"
            self._paramDHP3dScene = Parameter(VLabConstants.PARAM_NAME_DHP_3D_SCENE, VLabConstants.PARAM_DEFAULT_VALUE_DHP_3D_SCENE)
            self._paramDHP3dScene.getProperties().setValueSet(self._DHP3dScenes)
            self._paramDHP3dScene.getProperties().setValueSetBound(True)
            self._paramDHP3dScene.getProperties().setDefaultValue(VLabConstants.PARAM_DEFAULT_VALUE_DHP_3D_SCENE)
            self._paramDHP3dScene.getProperties().setLabel(VLabConstants.PARAM_LABEL_DHP_3D_SCENE)
            print "3dSenes got init"
            
            self. _DHPRTProcessors = [""] * 3
            self._DHPRTProcessors[0] = "librat"
            self._DHPRTProcessors[1] = "dart"
            self._DHPRTProcessors[2] = "libradtran"
            Arrays.sort(self._DHPRTProcessors)
            self._paramDHPRTProcessor = Parameter(VLabConstants.PARAM_NAME_DHP_RT_PROCESSOR, VLabConstants.PARAM_DEFAULT_VALUE_DHP_RT_PROCESSOR)
            self._paramDHPRTProcessor.getProperties().setValueSet(self._DHPRTProcessors)
            self._paramDHPRTProcessor.getProperties().setValueSetBound(True)
            self._paramDHPRTProcessor.getProperties().setDefaultValue(self._DHPRTProcessors[0])
            self._paramDHPRTProcessor.getProperties().setLabel(VLabConstants.PARAM_LABEL_DHP_RT_PROCESSOR)
            print "RTProcessor got init"

            self._paramResolution = self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_RESOLUTION, None)
            self._paramDHPLocationX = self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_LOCATION_X, None)
            self._paramDHPLocationY = self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_LOCATION_Y, None)
            self._paramDHPZenith = self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_DHP_PROP_ZENITH, None)
            self._paramDHPAzimuth = self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_DHP_PROP_AZIMUTH, None)
            self._paramDHPOrientation = self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_IMAGING_PLANE_ORIENTATION, None)
            self._paramDHPHeight = self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_IMAGING_PLANE_HEIGHT, None)
            
            self._paramDHPOutputPrefix = self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_DHP_OUTPUT_PREFIX, None)
            self._paramDHPImageFile = self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_DHP_IMAGE_FILE, None)
            self._paramDHPAsciiFile = self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_DHP_ASCII_FILE, None)
            print "Check boxes got init"

            
            
            
            self._paramOutputProduct = self._reqElemFac.createDefaultOutputProductParameter()
            print "OutputProduct Product should be created..."
            
            self._paramFMOutputFolder = self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_OUTPUT_FOLDER, None)
            self._paramDHPOutputFolder = self._reqElemFac.createParameter(VLabConstants.PARAM_NAME_DHP_OUTPUT_FOLDER, None)

            try:
                print "new try statement got called"
                self._logToOutputParameter = self._reqElemFac.createLogToOutputParameter("false")
            except ParamValidateException, ignored:
                print "ignore"
                #ignore
            
            self._logPrefixParameter = self._reqElemFac.createDefaultLogPatternParameter("vlab")
            print "createDefaultLogPatternParam..."

            #self._paramUpdateMode = self._reqElemFac.createParameter("update_mode", None)
            #print "paramUpdateMode"
            #Needed????
            #_paramWestLon = _reqElemFac.createParameter(VLabConstants.PARAM_NAME_WEST_LON, null);
            #_paramEastLon = _reqElemFac.createParameter(VLabConstants.PARAM_NAME_EAST_LON, null);
            #_paramNorthLat = _reqElemFac.createParameter(VLabConstants.PARAM_NAME_NORTH_LAT, null);
            #_paramSouthLat = _reqElemFac.createParameter(VLabConstants.PARAM_NAME_SOUTH_LAT, null);
            #_paramPixelSizeX = _reqElemFac.createParameter(VLabConstants.PARAM_NAME_PIXEL_SIZE_X, null);
            #_paramPixelSizeY = _reqElemFac.createParameter(VLabConstants.PARAM_NAME_PIXEL_SIZE_Y, null);
            #_paramConditionsOperator = _reqElemFac.createParameter(VLabConstants.PARAM_NAME_CONDITION_OPERATOR, null);
            #_paramOrthorectify = _reqElemFac.createParameter(VLabConstants.PARAM_NAME_ORTHORECTIFY_INPUT_PRODUCTS,
            #                                                 null);
            #_paramElevation = _reqElemFac.createParameter(
            #        VLabConstants.PARAM_NAME_ELEVATION_MODEL_FOR_ORTHORECTIFICATION, null);
        except RequestElementFactoryException, e:
            raise IllegalStateException("Unable to initialize parameters for processor UI.", e.getMessage())
        

       


        #not sure if this ParamListener is neede...
        #addParamListeners();
        
        
    def updatedList(self, files): 
        print "Listener Function updateList got called..."
        if (files == None or files.length == 0):
            self._inputProductBoundaries = None
            #WorlMape stuff needed?
            #if (self._worldMapWindow != None):
            #            self._worldMapWindow.setPathesToDisplay(None)
            self._paramUpdateMode.setDefaultValue()
            self._paramUpdateMode.setUIEnabled(false)
            return
            self._paramUpdateMode.setUIEnabled(True)
            filesSize = files.length
            for i in range(fileSize):
                if (self.setExampleProduct(files[i])):
                        break
            #WorlMap stuff... not needed?
            #if self.isWorldMapWindowVisible():
            #    self.scanInputProducts(getApp().getMainFrame());
                
                    
                    
                    
    def setExampleProduct(self, files):
        print "something"
        
    def browse(self, event):
        fc = swing.JFileChooser()
    
        fc.setFileSelectionMode(swing.JFileChooser.DIRECTORIES_ONLY)
    
    
        answer_fm = fc.showOpenDialog(self.browse_button)
    
    
        if(answer_fm == swing.JFileChooser.APPROVE_OPTION):
            file = fc.getSelectedFile()
            self._paramFMOutputFolder.setValueAsText(file.getAbsolutePath(), None)
            
    def browse_dhp(self, event):
        fc = swing.JFileChooser()
        
        fc.setFileSelectionMode(swing.JFileChooser.DIRECTORIES_ONLY)
        
        answer_dhp = fc.showOpenDialog(self.browse_button_dhp)
        
        if (answer_dhp == swing.JFileChooser.APPROVE_OPTION):
            file = fc.getSelectedFile()
            self._paramDHPOutputFolder.setValueAsText(file.getAbsolutePath(), None)
            
            
class VLabRequestElementFactory(RequestElementFactory):

    def __init__(self):
        self._defaultFactory = DefaultRequestElementFactory.getInstance()
        self._paramInfoMap = HashMap()
        self.initParamInfoMap()

    
    def getInstance(self):
        return VLabRequestElementFactory()
    

    def createParameter(self, name, value):
        print name
        print value
        Guardian.assertNotNullOrEmpty("name", name)

        #param = Parameter()
        try:
            print "try statement got called"
            param = self.createParamWithDefaultValueSet(name)
            if (value != None):
                print value
                param.setValueAsText(value, None)
            
        except IllegalArgumentException, e:
            print e.getMessage
            raise RequestElementFactoryException(e.getMessage())
        
        return param
    

    def createDefaultInputProductParameter(self):
        return self._defaultFactory.createDefaultInputProductParameter()
    

   
    def createDefaultLogPatternParameter(self, prefix):
        return self._defaultFactory.createDefaultLogPatternParameter(prefix)
    

    
    def createDefaultOutputProductParameter(self):
        defaultOutputProductParameter = self._defaultFactory.createDefaultOutputProductParameter()
        print "create Default Output Parameter"
        properties = defaultOutputProductParameter.getProperties()
        print "properties got called"
        defaultValue = properties.getDefaultValue()
        print defaultValue
        if (isinstance(defaultValue, File)):
            properties.setDefaultValue(File(defaultValue, VLabConstants.DEFAULT_OUTPUT_PRODUCT_NAME))
        
        defaultOutputProductParameter.setDefaultValue()
        # @todo 1 nf/se - also set default output format here, so that it fits to SmileConstants.DEFAULT_FILE_NAME's extension (.dim)
        return defaultOutputProductParameter
    

    
    def createInputProductRef(self, file, fileFormat, typeId):
        try:
            return self._defaultFactory.createInputProductRef(file, fileFormat, typeId)
        except RequestElementFactoryException, e:
            raise RequestElementFactoryException(e.getMessage())
    

    
    def createLogToOutputParameter(self, value):
        try:
            return self._defaultFactory.createLogToOutputParameter(value)
        except ParamValidateException, e:
            raise ParamValidateException(e.getMessage())
            
    

    def createOutputProductRef(self, file, fileFormat, typeId):
        try:
            return self._defaultFactory.createOutputProductRef(file, fileFormat, typeId)
        except RequestElementFactoryException, e:
            raise RequestElementFactoryException(e.getMessage())
    

   
   
    def initParamInfoMap(self):
        self._paramInfoMap.put(VLabConstants.PARAM_NAME_3D_SCENE, self.createParamInfo3dScene())
        self._paramInfoMap.put(VLabConstants.PARAM_NAME_RT_PROCESSOR, self.createParamInfoRtProcessor())
        self._paramInfoMap.put(VLabConstants.PARAM_NAME_SENSORS, self.createParamInfoSensor())
        self._paramInfoMap.put(VLabConstants.PARAM_NAME_SPECCHAR_BANDS, self.createParamSpeccharBands())
        self._paramInfoMap.put(VLabConstants.PARAM_NAME_VIEWING_ZENITH, self.createParamViewingZenith())
        self._paramInfoMap.put(VLabConstants.PARAM_NAME_VIEWING_AZIMUTH, self.createParamViewingAzimuth())
        self._paramInfoMap.put(VLabConstants.PARAM_NAME_ILLUMINATION_ZENITH, self.createParamIlluminationZenith())
        self._paramInfoMap.put(VLabConstants.PARAM_NAME_ILLUMINATION_AZIMUTH, self.createParamIlluminationAzimuth())
        self._paramInfoMap.put(VLabConstants.PARAM_NAME_SCENE_PIXEL, self.createParamScenePixel())
        self._paramInfoMap.put(VLabConstants.PARAM_NAME_SCENE_XC, self.createParamSceneXC())
        self._paramInfoMap.put(VLabConstants.PARAM_NAME_SCENE_YC, self.createParamSceneYC())
        self._paramInfoMap.put(VLabConstants.PARAM_NAME_SCENE_YW, self.createParamSceneYW())
        self._paramInfoMap.put(VLabConstants.PARAM_NAME_SCENE_XW, self.createParamSceneXW())
        self._paramInfoMap.put(VLabConstants.PARAM_NAME_ATMOSPHERE_DAY, self.createParamAtmosphereDay())
        self._paramInfoMap.put(VLabConstants.PARAM_NAME_ATMOSPHERE_LAT, self.createParamAtmosphereLat())
        self._paramInfoMap.put(VLabConstants.PARAM_NAME_ATMOSPHERE_LONG, self.createParamAtmosphereLong())
        self._paramInfoMap.put(VLabConstants.PARAM_NAME_ATMOSPHERE_CO2, self.createParamAtmosphereCO2())
        self._paramInfoMap.put(VLabConstants.PARAM_NAME_ATMOSPHERE_AEROSOL, self.createParamAtmosphereAerosol())
        self._paramInfoMap.put(VLabConstants.PARAM_NAME_ATMOSPHERE_WATER, self.createParamAtmosphereWater())
        self._paramInfoMap.put(VLabConstants.PARAM_NAME_ATMOSPHERE_OZONE, self.createParamAtmosphereOzone())
        self._paramInfoMap.put(VLabConstants.PARAM_NAME_OUTPUT_PREFIX, self.createParamOutputPrefix())
        self._paramInfoMap.put(VLabConstants.PARAM_NAME_IMAGE_FILE, self.createParamImageFile())
        self._paramInfoMap.put(VLabConstants.PARAM_NAME_ASCII_FILE, self.createParamAsciiFile())
        self._paramInfoMap.put(VLabConstants.PARAM_NAME_OUTPUT_FOLDER, self.createParamOutputfolder())
        
        #Parameters for DHP Simulation Pane
        self._paramInfoMap.put(VLabConstants.PARAM_NAME_DHP_3D_SCENE, self.createParamInfoDHP3dScene())
        self._paramInfoMap.put(VLabConstants.PARAM_NAME_DHP_RT_PROCESSOR, self.createParamInfoDHPRtProcessor())
        self._paramInfoMap.put(VLabConstants.PARAM_NAME_RESOLUTION, self.createParamInfoResolution())
        self._paramInfoMap.put(VLabConstants.PARAM_NAME_LOCATION_X, self.createParamInfoLocationX())
        self._paramInfoMap.put(VLabConstants.PARAM_NAME_LOCATION_Y, self.createParamInfoLocationY())
        self._paramInfoMap.put(VLabConstants.PARAM_NAME_DHP_PROP_ZENITH, self.createParamInfoDHPZenith())
        self._paramInfoMap.put(VLabConstants.PARAM_NAME_DHP_PROP_AZIMUTH, self.createParamInfoDHPAzimuth())
        self._paramInfoMap.put(VLabConstants.PARAM_NAME_IMAGING_PLANE_ORIENTATION, self.createParamInfoPlaneOrientation())
        self._paramInfoMap.put(VLabConstants.PARAM_NAME_IMAGING_PLANE_HEIGHT, self.createParamInfoPlaneHeight())
        self._paramInfoMap.put(VLabConstants.PARAM_NAME_DHP_OUTPUT_PREFIX, self.createParamDHPOutputPrefix())
        self._paramInfoMap.put(VLabConstants.PARAM_NAME_DHP_IMAGE_FILE, self.createParamDHPImageFile())
        self._paramInfoMap.put(VLabConstants.PARAM_NAME_DHP_ASCII_FILE, self.createParamDHPAsciiFile())
        self._paramInfoMap.put(VLabConstants.PARAM_NAME_DHP_OUTPUT_FOLDER, self.createParamDHPOutputfolder())
        
    

    def createParamOutputfolder(self):
        paramProps = self._defaultFactory.createStringParamProperties()
        paramProps.setLabel(VLabConstants.PARAM_LABEL_OUTPUT_FOLDER)
        paramProps.setDescription(VLabConstants.PARAM_DESCRIPTION_OUTPUT_FOLDER)
        paramProps.setDefaultValue(VLabConstants.PARAM_DEFAULT_VALUE_OUTPUT_FOLDER)
        return paramProps
    
    def createParamDHPOutputfolder(self):
        paramProps = self._defaultFactory.createStringParamProperties()
        paramProps.setLabel(VLabConstants.PARAM_LABEL_DHP_OUTPUT_FOLDER)
        paramProps.setDescription(VLabConstants.PARAM_DESCRIPTION_DHP_OUTPUT_FOLDER)
        paramProps.setDefaultValue(VLabConstants.PARAM_DEFAULT_VALUE_DHP_OUTPUT_FOLDER)
        return paramProps
    

    def createParamInfoPlaneHeight(self):
        paramProps = self._defaultFactory.createFloatParamProperties()
        paramProps.setLabel(VLabConstants.PARAM_LABEL_IMAGING_PLANE_HEIGHT)
        paramProps.setDescription(VLabConstants.PARAM_DESCRIPTION_IMAGING_PLANE_HEIGHT)
        paramProps.setDefaultValue(VLabConstants.PARAM_DEFAULT_VALUE_IMAGING_PLANE_HEIGHT)
        return paramProps
    

    def createParamInfoPlaneOrientation(self):
        paramProps = self._defaultFactory.createFloatParamProperties()
        paramProps.setLabel(VLabConstants.PARAM_LABEL_IMAGING_PLANE_ORIENTATION)
        paramProps.setDescription(VLabConstants.PARAM_DESCRIPTION_IMAGING_PLANE_ORIENTATION)
        paramProps.setDefaultValue(VLabConstants.PARAM_DEFAULT_VALUE_IMAGING_PLANE_ORIENTATION)
        return paramProps
    

    def createParamInfoDHPAzimuth(self):
        paramProps = self.createAngleProperties()
        paramProps.setLabel(VLabConstants.PARAM_LABEL_DHP_PROP_AZIMUTH)
        paramProps.setDescription(VLabConstants.PARAM_DESCRIPTION_DHP_PROP_AZIMUTH)
        paramProps.setDefaultValue(VLabConstants.PARAM_DEFAULT_VALUE_DHP_PROP_AZIMUTH)
        paramProps.setPhysicalUnit(VLabConstants.PARAM_UNIT_DEGREES)
        return paramProps
    

    def createParamInfoDHPZenith(self):
        paramProps = self.createAngleProperties()
        paramProps.setLabel(VLabConstants.PARAM_LABEL_DHP_PROP_ZENITH)
        paramProps.setDescription(VLabConstants.PARAM_DESCRIPTION_DHP_PROP_ZENITH)
        paramProps.setDefaultValue(VLabConstants.PARAM_DEFAULT_VALUE_DHP_PROP_ZENITH)
        paramProps.setPhysicalUnit(VLabConstants.PARAM_UNIT_DEGREES)
        return paramProps

    def createParamInfoLocationY(self):
        paramProps = self._defaultFactory.createFloatParamProperties()
        paramProps.setLabel(VLabConstants.PARAM_LABEL_LOCATION_Y)
        paramProps.setDescription(VLabConstants.PARAM_DESCRIPTION_LOCATION_Y)
        paramProps.setDefaultValue(VLabConstants.PARAM_DEFAULT_VALUE_LOCATION_Y)
        paramProps.setPhysicalUnit(VLabConstants.PARAM_UNIT_METERS)
        return paramProps

    def createParamInfoLocationX(self):
        paramProps = self._defaultFactory.createFloatParamProperties()
        paramProps.setLabel(VLabConstants.PARAM_LABEL_LOCATION_X)
        paramProps.setDescription(VLabConstants.PARAM_DESCRIPTION_LOCATION_X)
        paramProps.setDefaultValue(VLabConstants.PARAM_DEFAULT_VALUE_LOCATION_X)
        paramProps.setPhysicalUnit(VLabConstants.PARAM_UNIT_METERS)
        return paramProps

    def createParamInfoResolution(self):
        paramProps = self._defaultFactory.createStringParamProperties()
        paramProps.setLabel(VLabConstants.PARAM_LABEL_RESOLUTION)
        paramProps.setDescription(VLabConstants.PARAM_DESCRIPTION_RESOLUTION)
        paramProps.setDefaultValue(VLabConstants.PARAM_DEFAULT_VALUE_RESOLUTION)
        return paramProps

    def createParamInfo3dScene(self):
        paramProps = self._defaultFactory.createStringParamProperties()
        paramProps.setLabel(VLabConstants.PARAM_LABEL_3D_SCENE)
        paramProps.setDescription(VLabConstants.PARAM_DESCRIPTION_3D_SCENE)
        paramProps.setDefaultValue(VLabConstants.PARAM_DEFAULT_VALUE_3D_SCENE)
        return paramProps
    
    def createParamInfoDHP3dScene(self):
        paramProps = self._defaultFactory.createStringParamProperties()
        paramProps.setLabel(VLabConstants.PARAM_LABEL_DHP_3D_SCENE)
        paramProps.setDescription(VLabConstants.PARAM_DESCRIPTION_DHP_3D_SCENE)
        paramProps.setDefaultValue(VLabConstants.PARAM_DEFAULT_VALUE_DHP_3D_SCENE)
        return paramProps

    def createParamInfoRtProcessor(self):
        paramProps = self._defaultFactory.createStringParamProperties()
        paramProps.setLabel(VLabConstants.PARAM_LABEL_RT_PROCESSOR)
        paramProps.setDescription(VLabConstants.PARAM_DESCRIPTION_RT_PROCESSOR)
        paramProps.setDefaultValue(VLabConstants.PARAM_DEFAULT_VALUE_RT_PROCESSOR)
        return paramProps
    
    def createParamInfoDHPRtProcessor(self):
        paramProps = self._defaultFactory.createStringParamProperties()
        paramProps.setLabel(VLabConstants.PARAM_LABEL_DHP_RT_PROCESSOR)
        paramProps.setDescription(VLabConstants.PARAM_DESCRIPTION_DHP_RT_PROCESSOR)
        paramProps.setDefaultValue(VLabConstants.PARAM_DEFAULT_VALUE_DHP_RT_PROCESSOR)
        return paramProps
    
    def createParamInfoSensor(self):
        paramProps = self._defaultFactory.createStringParamProperties()
        paramProps.setLabel(VLabConstants.PARAM_LABEL_SENSORS)
        paramProps.setDescription(VLabConstants.PARAM_DESCRIPTION_SENSORS)
        paramProps.setDefaultValue(VLabConstants.PARAM_DEFAULT_VALUE_SENSORS)
        return paramProps
    
    def createParamSpeccharBands(self):
        paramProps = self._defaultFactory.createStringParamProperties()
        paramProps.setLabel(VLabConstants.PARAM_LABEL_SPECCHAR_BANDS)
        paramProps.setDescription(VLabConstants.PARAM_DESCRIPTION_SPECCHAR_BANDS)
        paramProps.setDefaultValue(VLabConstants.PARAM_DEFAULT_VALUE_SPECCHAR_BANDS)
        return paramProps

    def createParamViewingZenith(self):
        paramProps = self.createAngleProperties()
        paramProps.setLabel(VLabConstants.PARAM_LABEL_VIEWING_ZENITH)
        paramProps.setDescription(VLabConstants.PARAM_DESCRIPTION_VIEWING_ZENITH)
        paramProps.setDefaultValue(VLabConstants.PARAM_DEFAULT_VALUE_VIEWING_ZENITH)
        paramProps.setPhysicalUnit(VLabConstants.PARAM_UNIT_DEGREES)
        return paramProps


    def createParamViewingAzimuth(self):
        paramProps = self.createAngleProperties()
        paramProps.setLabel(VLabConstants.PARAM_LABEL_VIEWING_AZIMUTH)
        paramProps.setDescription(VLabConstants.PARAM_DESCRIPTION_VIEWING_AZIMUTH)
        paramProps.setDefaultValue(VLabConstants.PARAM_DEFAULT_VALUE_VIEWING_AZIMUTH)
        paramProps.setPhysicalUnit(VLabConstants.PARAM_UNIT_DEGREES)
        return paramProps

    def createParamIlluminationZenith(self):
        paramProps = self.createAngleProperties()
        paramProps.setLabel(VLabConstants.PARAM_LABEL_ILLUMINATION_ZENITH)
        paramProps.setDescription(VLabConstants.PARAM_DESCRIPTION_ILLUMINATION_ZENITH)
        paramProps.setDefaultValue(VLabConstants.PARAM_DEFAULT_VALUE_ILLUMINATION_ZENITH)
        paramProps.setPhysicalUnit(VLabConstants.PARAM_UNIT_DEGREES)
        return paramProps
    

    def createParamIlluminationAzimuth(self):
        paramProps = self.createAngleProperties()
        paramProps.setLabel(VLabConstants.PARAM_LABEL_ILLUMINATION_AZIMUTH)
        paramProps.setDescription(VLabConstants.PARAM_DESCRIPTION_ILLUMINATION_AZIMUTH)
        paramProps.setDefaultValue(VLabConstants.PARAM_DEFAULT_VALUE_ILLUMINATION_AZIMUTH)
        paramProps.setPhysicalUnit(VLabConstants.PARAM_UNIT_DEGREES)
        return paramProps

    def createParamScenePixel(self):
        paramProps = self._defaultFactory.createIntegerParamProperties()
        paramProps.setLabel(VLabConstants.PARAM_LABEL_SCENE_PIXEL)
        paramProps.setDescription(VLabConstants.PARAM_DESCRIPTION_SCENE_PIXEL)
        paramProps.setDefaultValue(VLabConstants.PARAM_DEFAULT_VALUE_SCENE_PIXEL)
        paramProps.setPhysicalUnit(VLabConstants.PARAM_UNIT_PIXELS)
        return paramProps
    
    
    def createParamSceneXC(self):
        paramProps = self._defaultFactory.createBoundFloatParamProperties()
        #paramProps.setValidatorClass(PixelSizeValidator.class)
        paramProps.setLabel(VLabConstants.PARAM_LABEL_SCENE_XC)
        paramProps.setDescription(VLabConstants.PARAM_DESCRIPTION_SCENE_XC)
        paramProps.setDefaultValue(VLabConstants.PARAM_DEFAULT_VALUE_SCENE_XC)
        paramProps.setPhysicalUnit(VLabConstants.PARAM_UNIT_PIXELS)
        return paramProps
    

    def createParamSceneYC(self):
        paramProps = self._defaultFactory.createBoundFloatParamProperties()
        #paramProps.setValidatorClass(PixelSizeValidator.class)
        paramProps.setLabel(VLabConstants.PARAM_LABEL_SCENE_YC)
        paramProps.setDescription(VLabConstants.PARAM_DESCRIPTION_SCENE_YC)
        paramProps.setDefaultValue(VLabConstants.PARAM_DEFAULT_VALUE_SCENE_YC)
        paramProps.setPhysicalUnit(VLabConstants.PARAM_UNIT_PIXELS)
        return paramProps
    
    

    def createParamSceneXW(self):
        paramProps = self._defaultFactory.createBoundFloatParamProperties()
        #paramProps.setValidatorClass(PixelSizeValidator.class)
        paramProps.setLabel(VLabConstants.PARAM_LABEL_SCENE_XW)
        paramProps.setDescription(VLabConstants.PARAM_DESCRIPTION_SCENE_XW)
        paramProps.setDefaultValue(VLabConstants.PARAM_DEFAULT_VALUE_SCENE_XW)
        paramProps.setPhysicalUnit(VLabConstants.PARAM_UNIT_PIXELS)
        return paramProps
    
    def createParamSceneYW(self):
        paramProps = self._defaultFactory.createBoundFloatParamProperties()
        #paramProps.setValidatorClass(PixelSizeValidator.class)
        paramProps.setLabel(VLabConstants.PARAM_LABEL_SCENE_YW)
        paramProps.setDescription(VLabConstants.PARAM_DESCRIPTION_SCENE_YW)
        paramProps.setDefaultValue(VLabConstants.PARAM_DEFAULT_VALUE_SCENE_YW)
        paramProps.setPhysicalUnit(VLabConstants.PARAM_UNIT_PIXELS)
        return paramProps
    
    def createParamAtmosphereDay(self):
        paramProps = self._defaultFactory.createIntegerParamProperties()
        paramProps.setLabel(VLabConstants.PARAM_LABEL_ATMOSPHERE_DAY)
        paramProps.setDescription(VLabConstants.PARAM_DESCRIPTION_ATMOSPHERE_DAY)
        paramProps.setDefaultValue(VLabConstants.PARAM_DEFAULT_VALUE_ATMOSPHERE_DAY)
        return paramProps

    def createParamAtmosphereLat(self):
        paramProps = self.createLatitudeProperties()
        paramProps.setLabel(VLabConstants.PARAM_LABEL_ATMOSPHERE_LAT)
        paramProps.setDescription(VLabConstants.PARAM_DESCRIPTION_ATMOSPHERE_LAT)
        paramProps.setDefaultValue(VLabConstants.PARAM_DEFAULT_VALUE_ATMOSPHERE_LAT)
        paramProps.setPhysicalUnit(VLabConstants.PARAM_UNIT_DEGREES)
        return paramProps
    
    def createParamAtmosphereLong(self):
        paramProps = self.createLongitudeProperties()
        paramProps.setLabel(VLabConstants.PARAM_LABEL_ATMOSPHERE_LONG)
        paramProps.setDescription(VLabConstants.PARAM_DESCRIPTION_ATMOSPHERE_LONG)
        paramProps.setDefaultValue(VLabConstants.PARAM_DEFAULT_VALUE_ATMOSPHERE_LONG)
        paramProps.setPhysicalUnit(VLabConstants.PARAM_UNIT_DEGREES)
        return paramProps
    
    def createParamAtmosphereCO2(self):
        paramProps = self._defaultFactory.createStringParamProperties()
        paramProps.setLabel(VLabConstants.PARAM_LABEL_ATMOSPHERE_CO2)
        paramProps.setDescription(VLabConstants.PARAM_DESCRIPTION_ATMOSPHERE_CO2)
        paramProps.setDefaultValue(VLabConstants.PARAM_DEFAULT_VALUE_ATMOSPHERE_CO2)
        return paramProps

    def createParamAtmosphereAerosol(self):
        paramProps = self._defaultFactory.createStringParamProperties()
        paramProps.setLabel(VLabConstants.PARAM_LABEL_ATMOSPHERE_AEROSOL)
        paramProps.setDescription(VLabConstants.PARAM_DESCRIPTION_ATMOSPHERE_AEROSOL)
        paramProps.setDefaultValue(VLabConstants.PARAM_DEFAULT_VALUE_ATMOSPHERE_AEROSOL)
        return paramProps

    def createParamAtmosphereWater(self):
        paramProps = self._defaultFactory.createStringParamProperties()
        paramProps.setLabel(VLabConstants.PARAM_LABEL_ATMOSPHERE_WATER)
        paramProps.setDescription(VLabConstants.PARAM_DESCRIPTION_ATMOSPHERE_WATER)
        paramProps.setDefaultValue(VLabConstants.PARAM_DEFAULT_VALUE_ATMOSPHERE_WATER)
        return paramProps

    def createParamAtmosphereOzone(self):
        paramProps = self._defaultFactory.createStringParamProperties()
        paramProps.setLabel(VLabConstants.PARAM_LABEL_ATMOSPHERE_OZONE)
        paramProps.setDescription(VLabConstants.PARAM_DESCRIPTION_ATMOSPHERE_OZONE)
        paramProps.setDefaultValue(VLabConstants.PARAM_DEFAULT_VALUE_ATMOSPHERE_OZONE)
        return paramProps

    def createParamOutputPrefix(self):
        paramProps = self._defaultFactory.createStringParamProperties()
        paramProps.setLabel(VLabConstants.PARAM_LABEL_OUTPUT_PREFIX)
        paramProps.setDescription(VLabConstants.PARAM_DESCRIPTION_OUTPUT_PREFIX)
        paramProps.setDefaultValue(VLabConstants.PARAM_DEFAULT_VALUE_OUTPUT_PREFIX)
        return paramProps
    
    def createParamDHPOutputPrefix(self):
        paramProps = self._defaultFactory.createStringParamProperties()
        paramProps.setLabel(VLabConstants.PARAM_LABEL_DHP_OUTPUT_PREFIX)
        paramProps.setDescription(VLabConstants.PARAM_DESCRIPTION_DHP_OUTPUT_PREFIX)
        paramProps.setDefaultValue(VLabConstants.PARAM_DEFAULT_VALUE_DHP_OUTPUT_PREFIX)
        return paramProps
    
    def createParamImageFile(self):
        paramProps = self._defaultFactory.createBooleanParamProperties()
        paramProps.setLabel(VLabConstants.PARAM_LABEL_IMAGE_FILE)
        paramProps.setDescription(VLabConstants.PARAM_DESCRIPTION_IMAGE_FILE)
        paramProps.setDefaultValue(VLabConstants.PARAM_DEFAULT_IMAGE_FILE)
        return paramProps
    
    def createParamDHPImageFile(self):
        paramProps = self._defaultFactory.createBooleanParamProperties()
        paramProps.setLabel(VLabConstants.PARAM_LABEL_DHP_IMAGE_FILE)
        paramProps.setDescription(VLabConstants.PARAM_DESCRIPTION_DHP_IMAGE_FILE)
        paramProps.setDefaultValue(VLabConstants.PARAM_DEFAULT_DHP_IMAGE_FILE)
        return paramProps

    def createParamAsciiFile(self):
        paramProps = self._defaultFactory.createBooleanParamProperties()
        paramProps.setLabel(VLabConstants.PARAM_LABEL_ASCII_FILE)
        paramProps.setDescription(VLabConstants.PARAM_DESCRIPTION_ASCII_FILE)
        paramProps.setDefaultValue(VLabConstants.PARAM_DEFAULT_ASCII_FILE)
        return paramProps
    
    def createParamDHPAsciiFile(self):
        paramProps = self._defaultFactory.createBooleanParamProperties()
        paramProps.setLabel(VLabConstants.PARAM_LABEL_DHP_ASCII_FILE)
        paramProps.setDescription(VLabConstants.PARAM_DESCRIPTION_DHP_ASCII_FILE)
        paramProps.setDefaultValue(VLabConstants.PARAM_DEFAULT_DHP_ASCII_FILE)
        return paramProps
    
    
    def createLongitudeProperties(self):
        paramProps = self._defaultFactory.createFloatParamProperties()
        paramProps.setMinValue(-180.0)
        paramProps.setMaxValue(180.0)
        return paramProps
    

    def createLatitudeProperties(self):
        paramProps = self._defaultFactory.createFloatParamProperties()
        paramProps.setMinValue(-90.0)
        paramProps.setMaxValue(90.0)
        return paramProps
    

    def createAngleProperties(self):
        paramProps = self._defaultFactory.createFloatParamProperties()
        paramProps.setMinValue(-360.0)
        paramProps.setMaxValue(360.0)
        return paramProps
    

    
    
    
    
# not sure if this class is needed...

    #public static class PixelSizeValidator extends NumberValidator {
#
#        @Override
#        public void validate(final Parameter parameter, final Object value) throws ParamValidateException {
#            super.validate(parameter, value)
#            if (value instanceof Number) {
#                final Number number = (Number) value
#                final double size = number.doubleValue()
#                if (size <= 0.00) {
#                    throw new ParamValidateException(parameter, "Value must be greater than zero.")
#                }
#            }
#        }
#    }

    def createParamWithDefaultValueSet(self, paramName):
        print paramName
        paramProps = self.getParamInfo(paramName)
        print "paramInfo got called"
        param = Parameter(paramName, paramProps.createCopy())
        print "param Constructor called"
        param.setDefaultValue()
        return param
    


    def getParamInfo(self, parameterName):
        paramProps = self._paramInfoMap.get(parameterName)
        if (paramProps == None):
            if (parameterName.endsWith(VLabConstants.PARAM_SUFFIX_EXPRESSION)):
                print "has to be implemented!!"
   #             paramProps = ParamProperties(String.class, "")
            elif (parameterName.endsWith(VLabConstants.PARAM_SUFFIX_CONDITION)):
                print "has to be implemented!!"
    #            paramProps = ParamProperties(Boolean.class, False)
            elif (parameterName.endsWith(VLabConstants.PARAM_SUFFIX_OUTPUT)):
                print "has to be implemented!!"
     #           paramProps = ParamProperties(Boolean.class, False)

        if (paramProps == None):
            print "invalid parameter name " + parameterName
            raise IllegalArgumentException("Invalid parameter name '" + parameterName + "'.")
        
        return paramProps
    

    def createStringParamProperties(self):
        return self._defaultFactory.createStringParamProperties()
    
    # Initialization on demand holder idiom --> not sure if this is really needed...
    #class Holder:
    #    instance = VLabRequestElementFactory()
    


class VLabConstants:
    
    #def __init__(self):

        PROCESSOR_NAME = "BEAM VLab Processor"
        PROCESSOR_SYMBOLIC_NAME = "beam-vlab"
        VERSION_STRING = "2.2.100"
        COPYRIGHT_INFO = ""
    
        REQUEST_TYPE = "VLAB"
        REQUEST_TYPE_MAP_PROJECTION = "MAP_PROJECTION"
    
        DEFAULT_OUTPUT_PRODUCT_NAME = "vlab_out.dim"
        OUTPUT_PRODUCT_TYPE = "BEAM_VLAB"
        BANDNAME_COUNT = "num_pixels"
    
    ##  ****************************
    ##  *****  User Interface  *****
    ##  ****************************
        UI_TITLE = "VLab - Processor"
    
    ##  *****************************
    ##  *****  Parameter Units  *****
    ##  *****************************
        PARAM_UNIT_DEGREES = "degrees"
        PARAM_UNIT_METERS = "m"
        PARAM_UNIT_PIXELS = "pixels"
        
    ##  *****************************
    ##  *****  Sensor Wavebands  ****
    ##  *****************************
        
        WB_SENTINEL_2 = array('i',[433, 560, 665, 705, 740, 783, 842, 865, 945, 1610, 2190])
        WB_SENTINEL_3 = array('i',[413, 490, 510, 560, 620, 665, 681, 709, 754, 761, 779, 865, 885, 900, 1020])
            
    
    
    ##  ********************************
    ##  *****  Request Parameters  *****
    ##  ********************************
        PARAM_NAME_3D_SCENE = "3d_scene"
        PARAM_LABEL_3D_SCENE = "3D Scene"
        PARAM_DESCRIPTION_3D_SCENE = "Selection of world file"
        PARAM_DEFAULT_VALUE_3D_SCENE = "Default RAMI"
        
        PARAM_NAME_DHP_3D_SCENE = "dhp_3d_scene"
        PARAM_LABEL_DHP_3D_SCENE = "3D Scene"
        PARAM_DESCRIPTION_DHP_3D_SCENE = "Selection of world file"
        PARAM_DEFAULT_VALUE_DHP_3D_SCENE = "Default RAMI"
        
    
        PARAM_NAME_RT_PROCESSOR = "rt_processor"
        PARAM_LABEL_RT_PROCESSOR = "RT Processor"
        PARAM_DESCRIPTION_RT_PROCESSOR = "RT Processor"
        PARAM_DEFAULT_VALUE_RT_PROCESSOR = "librat"
        
        PARAM_NAME_DHP_RT_PROCESSOR = "dhp_rt_processor"
        PARAM_LABEL_DHP_RT_PROCESSOR = "RT Processor"
        PARAM_DESCRIPTION_DHP_RT_PROCESSOR = "RT Processor"
        PARAM_DEFAULT_VALUE_DHP_RT_PROCESSOR = "librat"
        
        #Additional SpectralCharacteristics Panel
        PARAM_NAME_SENSORS = "sensors"
        PARAM_LABEL_SENSORS = "Sensor"
        PARAM_DESCRIPTION_SENSORS = "TODO"
        PARAM_DEFAULT_VALUE_SENSORS = "Sentinel-2"
        
        PARAM_NAME_SPECCHAR_BANDS = "spec_bands"
        PARAM_LABEL_SPECCHAR_BANDS = "Bands"
        PARAM_DESCRIPTION_SPECCHAR_BANDS = "TODO"
        PARAM_DEFAULT_VALUE_SPECCHAR_BANDS = "1, 2, 3"
    
        PARAM_NAME_VIEWING_ZENITH = "viewing_zenith"
        PARAM_LABEL_VIEWING_ZENITH = "Zenith"
        PARAM_DESCRIPTION_VIEWING_ZENITH = "TODO"
        PARAM_DEFAULT_VALUE_VIEWING_ZENITH = 0.0
    
        PARAM_NAME_VIEWING_AZIMUTH = "viewing_azimuth"
        PARAM_LABEL_VIEWING_AZIMUTH = "Azimuth"
        PARAM_DESCRIPTION_VIEWING_AZIMUTH = "TODO"
        PARAM_DEFAULT_VALUE_VIEWING_AZIMUTH = 0.0
    
        PARAM_NAME_ILLUMINATION_ZENITH = "illumination_zenith"
        PARAM_LABEL_ILLUMINATION_ZENITH = "Zenith"
        PARAM_DESCRIPTION_ILLUMINATION_ZENITH = "TODO"
        PARAM_DEFAULT_VALUE_ILLUMINATION_ZENITH = 0.0
    
        PARAM_NAME_ILLUMINATION_AZIMUTH = "illumination_azimuth"
        PARAM_LABEL_ILLUMINATION_AZIMUTH = "Azimuth"
        PARAM_DESCRIPTION_ILLUMINATION_AZIMUTH = "TODO"
        PARAM_DEFAULT_VALUE_ILLUMINATION_AZIMUTH = 0.0
    
        PARAM_NAME_SCENE_PIXEL = "scene_pixel"
        PARAM_LABEL_SCENE_PIXEL = "Pixel Size"
        PARAM_DESCRIPTION_SCENE_PIXEL = "TODO"
        PARAM_DEFAULT_VALUE_SCENE_PIXEL = 100
    
        PARAM_NAME_SCENE_XC = "scene_xc"
        PARAM_LABEL_SCENE_XC = "XC"
        PARAM_DESCRIPTION_SCENE_XC = "TODO"
        PARAM_DEFAULT_VALUE_SCENE_XC = 0.0
    
        PARAM_NAME_SCENE_YC = "scene_yc"
        PARAM_LABEL_SCENE_YC = "YC"
        PARAM_DESCRIPTION_SCENE_YC = "TODO"
        PARAM_DEFAULT_VALUE_SCENE_YC = 0.0
    
        PARAM_NAME_SCENE_XW = "scene_xw"
        PARAM_LABEL_SCENE_XW = "XW"
        PARAM_DESCRIPTION_SCENE_XW = "TODO"
        PARAM_DEFAULT_VALUE_SCENE_XW = 100.0
    
        PARAM_NAME_SCENE_YW = "scene_yw"
        PARAM_LABEL_SCENE_YW = "YW"
        PARAM_DESCRIPTION_SCENE_YW = "TODO"
        PARAM_DEFAULT_VALUE_SCENE_YW = 100.0
    
        PARAM_NAME_ATMOSPHERE_DAY = "atmosphere_day"
        PARAM_LABEL_ATMOSPHERE_DAY = "Day of Year"
        PARAM_DESCRIPTION_ATMOSPHERE_DAY = "TODO"
        PARAM_DEFAULT_VALUE_ATMOSPHERE_DAY = 1
    
        PARAM_NAME_ATMOSPHERE_LAT = "atmosphere_lat"
        PARAM_LABEL_ATMOSPHERE_LAT = "Lat"
        PARAM_DESCRIPTION_ATMOSPHERE_LAT = "TODO"
        PARAM_DEFAULT_VALUE_ATMOSPHERE_LAT = 0.0
        
        PARAM_NAME_ATMOSPHERE_LONG = "atmosphere_long"
        PARAM_LABEL_ATMOSPHERE_LONG = "Long"
        PARAM_DESCRIPTION_ATMOSPHERE_LONG = "TODO"
        PARAM_DEFAULT_VALUE_ATMOSPHERE_LONG = 0.0
        
        PARAM_NAME_ATMOSPHERE_CO2 = "atmosphere_co2"
        PARAM_LABEL_ATMOSPHERE_CO2 = "CO2 Profile"
        PARAM_DESCRIPTION_ATMOSPHERE_CO2 = "TODO"
        PARAM_DEFAULT_VALUE_ATMOSPHERE_CO2 = "standard"
    
        PARAM_NAME_ATMOSPHERE_AEROSOL = "atmosphere_aerosol"
        PARAM_LABEL_ATMOSPHERE_AEROSOL = "Aerosol Profile"
        PARAM_DESCRIPTION_ATMOSPHERE_AEROSOL = "TODO"
        PARAM_DEFAULT_VALUE_ATMOSPHERE_AEROSOL = "standard"
    
        PARAM_NAME_ATMOSPHERE_WATER = "atmosphere_water"
        PARAM_LABEL_ATMOSPHERE_WATER = "Water Vapor"
        PARAM_DESCRIPTION_ATMOSPHERE_WATER = "TODO"
        PARAM_DEFAULT_VALUE_ATMOSPHERE_WATER = "standard"
    
        PARAM_NAME_ATMOSPHERE_OZONE = "atmosphere_ozone"
        PARAM_LABEL_ATMOSPHERE_OZONE = "Ozone"
        PARAM_DESCRIPTION_ATMOSPHERE_OZONE = "TODO"
        PARAM_DEFAULT_VALUE_ATMOSPHERE_OZONE = "standard"
    
        PARAM_NAME_OUTPUT_PREFIX = "output_prefix"
        PARAM_LABEL_OUTPUT_PREFIX = "Output file prefix"
        PARAM_DESCRIPTION_OUTPUT_PREFIX = "TODO"
        PARAM_DEFAULT_VALUE_OUTPUT_PREFIX = ""
        
        PARAM_NAME_DHP_OUTPUT_PREFIX = "dhp_output_prefix"
        PARAM_LABEL_DHP_OUTPUT_PREFIX = "Output file prefix"
        PARAM_DESCRIPTION_DHP_OUTPUT_PREFIX = "TODO"
        PARAM_DEFAULT_VALUE_DHP_OUTPUT_PREFIX = ""
        
        PARAM_NAME_OUTPUT_FOLDER = "output_folder"
        PARAM_LABEL_OUTPUT_FOLDER = "Output folder"
        PARAM_DESCRIPTION_OUTPUT_FOLDER = "Folder for all output files"
        PARAM_DEFAULT_VALUE_OUTPUT_FOLDER = ""
        
        PARAM_NAME_DHP_OUTPUT_FOLDER = "dhp_output_folder"
        PARAM_LABEL_DHP_OUTPUT_FOLDER = "Output folder"
        PARAM_DESCRIPTION_DHP_OUTPUT_FOLDER = "Folder for all output files"
        PARAM_DEFAULT_VALUE_DHP_OUTPUT_FOLDER = ""
    
        PARAM_NAME_IMAGE_FILE = "image_file"
        PARAM_LABEL_IMAGE_FILE = "Image file"
        PARAM_DESCRIPTION_IMAGE_FILE = "TODO"
        PARAM_DEFAULT_IMAGE_FILE = False
        
        PARAM_NAME_DHP_IMAGE_FILE = "dhp_image_file"
        PARAM_LABEL_DHP_IMAGE_FILE = "Image file"
        PARAM_DESCRIPTION_DHP_IMAGE_FILE = "TODO"
        PARAM_DEFAULT_DHP_IMAGE_FILE = False
    
        PARAM_NAME_ASCII_FILE = "ascii_file"
        PARAM_LABEL_ASCII_FILE = "Ascii file"
        PARAM_DESCRIPTION_ASCII_FILE = "TODO"
        PARAM_DEFAULT_ASCII_FILE = False
        
        PARAM_NAME_DHP_ASCII_FILE = "dhp_ascii_file"
        PARAM_LABEL_DHP_ASCII_FILE = "Ascii file"
        PARAM_DESCRIPTION_DHP_ASCII_FILE = "TODO"
        PARAM_DEFAULT_DHP_ASCII_FILE = False
    
        
        ## Constants for DHP Simulation Panel
        PARAM_NAME_RESOLUTION = "resolution"
        PARAM_LABEL_RESOLUTION = "Resolution"
        PARAM_DESCRIPTION_RESOLUTION = "Resolution"
        PARAM_DEFAULT_VALUE_RESOLUTION = "100x100"
        
        PARAM_NAME_LOCATION_X = "location_x"
        PARAM_LABEL_LOCATION_X = "X"
        PARAM_DESCRIPTION_LOCATION_X = "Location X"
        PARAM_DEFAULT_VALUE_LOCATION_X = 0.0
        
        PARAM_NAME_LOCATION_Y = "location_y"
        PARAM_LABEL_LOCATION_Y = "Y"
        PARAM_DESCRIPTION_LOCATION_Y = "Location Y"
        PARAM_DEFAULT_VALUE_LOCATION_Y = 0.0
        
        PARAM_NAME_DHP_PROP_ZENITH = "zenith_angle"
        PARAM_LABEL_DHP_PROP_ZENITH = "Zenith angle"
        PARAM_DESCRIPTION_DHP_PROP_ZENITH = "Zenith angle"
        PARAM_DEFAULT_VALUE_DHP_PROP_ZENITH = 0.0
        
        PARAM_NAME_DHP_PROP_AZIMUTH = "azimuth_angle"
        PARAM_LABEL_DHP_PROP_AZIMUTH = "Azimuth angle"
        PARAM_DESCRIPTION_DHP_PROP_AZIMUTH = "Azimuth angle"
        PARAM_DEFAULT_VALUE_DHP_PROP_AZIMUTH = 0.0
        
        PARAM_NAME_IMAGING_PLANE_ORIENTATION = "orientation"
        PARAM_LABEL_IMAGING_PLANE_ORIENTATION = "Orientation"
        PARAM_DESCRIPTION_IMAGING_PLANE_ORIENTATION = "Orientation"
        PARAM_DEFAULT_VALUE_IMAGING_PLANE_ORIENTATION = 0.0
        
        PARAM_NAME_IMAGING_PLANE_HEIGHT = "height"
        PARAM_LABEL_IMAGING_PLANE_HEIGHT = "Height (z)"
        PARAM_DESCRIPTION_IMAGING_PLANE_HEIGHT = "Height (z)"
        PARAM_DEFAULT_VALUE_IMAGING_PLANE_HEIGHT = 0.0
        
    
    ##    Processing Parameter
        PARAM_SUFFIX_EXPRESSION = ".expression"
        PARAM_SUFFIX_CONDITION = ".condition"
        PARAM_SUFFIX_OUTPUT = ".output"
    
    ##  *********************
    ##  *****  Logging  *****
    ##  *********************
        LOGGER_NAME = "beam.processor.vlab"
        DEFAULT_LOG_PREFIX = "vlab"
    #3    ProcessorConstants.LOG_TO_OUTPUT_PARAM_NAME
    ##    ProcessorConstants.LOG_PREFIX_PARAM_NAME
    
        ## Support for PixelGeoCoding
        PARAM_NAME_GEOCODING_LATITUDES = "geocoding_latitudes"
        PARAM_NAME_GEOCODING_LONGITUDES = "geocoding_longitudes"
        PARAM_NAME_GEOCODING_VALID_MASK = "geocoding_valid_mask"
        PARAM_NAME_GEOCODING_SEARCH_RADIUS = "geocoding_search_radius"
        DEFAULT_GEOCODING_SEARCH_RADIUS = 7
