#
# Copyright (C) 2010-2013 Netcetera Switzerland (info@netcetera.com)
# 
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program; if not, see http://www.gnu.org/licenses/
# 
# @(#) $Id: $
#
# Authors: Cyril Schenkel, Daniel Kueckenbrink, Joshy Cyriac, Marcel Kessler, Jason Brazile
#
import sys

from java              import awt
from java              import io
from java              import lang
from java.io           import BufferedReader
from java.io           import BufferedWriter
from java.io           import File
from java.io           import FileInputStream
from java.io           import FileOutputStream
from java.io           import FileReader
from java.io           import FileWriter
from java.io           import InputStreamReader
from java.io           import IOException
from java.io           import OutputStreamWriter
from java.lang         import Exception as JException
from java.lang         import IllegalArgumentException
from java.lang         import Integer
from java.lang         import ProcessBuilder
from java.lang         import RuntimeException
from java.lang         import System
from java.lang         import Thread
from java.util         import ArrayList
from java.util         import Arrays
from java.util         import HashMap
from java.util         import Map
from java.util         import Vector
from java.util.logging import Logger
from javax             import swing

##
## Vegetation Lab constants, "data model", utilities etc
##
class VLAB:
  COPYRIGHT_INFO     = 'Copyright (C) 2010-2013 Netcetera Switzerland (info@netcetera.com)'
  PROCESSOR_NAME     = 'BEAM VLab Processor'
  PROCESSOR_SNAME    = 'beam-vlab'
  REQUEST_TYPE       = 'VLAB'
  UI_TITLE           = 'VLab - Processor'
  VERSION_STRING     = '1.0 (2013-10-18)'
  DEFAULT_LOG_PREFIX = 'vlab'
  LOGGER_NAME        = 'beam.processor.vlab'

  D_PRODNAME         = 'vlab_out.dim'
  P_CONDITION        = '.condition'
  P_EXPRESSION       = '.expression'
  P_OUTPUT           = '.output'

  JCB                = 'JComboBox'
  JTF                = 'JTextField'

  K_LIBRAT           = 'librat'
  K_DART             = 'dart'
  K_DUMMY            = 'dummy'

  K_LAEGEREN         = 'Laegeren'
  K_RAMI             = 'Default RAMI'

  K_YES              = 'Yes'
  K_NO               = 'No'

  K_SENTINEL2        = 'MSI (Sentinel 2)'
  K_SENTINEL3        = 'OLCI (Sentinel 3)'
  K_MODIS            = 'MODIS'
  K_MERIS            = 'MERIS'
  K_LANDSAT          = 'Landsat'

  K_RURAL            = 'Rural'
  K_MARITIME         = 'Maritime'
  K_URBAN            = 'Urban'
  K_TROPOSPHERIC     = 'Tropospheric'

  ERR                = 'error'
  DBG                = 'debug'
  INF                = 'info'

  if sys.platform.startswith('java'):
    from java.util.logging import Logger
    logger = Logger.getLogger(LOGGER_NAME)
  else:
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)
    # logfh = logging.FileHandler('%s.log' % VLAB.LOGGER_NAME)
    # logfh.setLevel(logging.DEBUG)
    # VLAB.logger.addHandler(logfh)
    logch = logging.StreamHandler()
    logch.setLevel(logging.DEBUG)
    logger.addHandler(logch)

  plst = []

  model = (
{'Forward Modeling': (
{'Model Selection': (
 ('3D Scene',          '3dScene',             JCB, (K_RAMI, K_LAEGEREN)),
 ('RT Processor',      'RTProcessor',         JCB, (K_DUMMY, K_LIBRAT, K_DART)))},
{'Spectral Characteristics': (
 ('Sensor',            'Sensor',              JCB, (K_SENTINEL2, K_SENTINEL3, K_MODIS, K_MERIS, K_LANDSAT)),
 ('Bands',             'Bands',               JTF, '1, 2, 3, 4, 5, 6, 7, 8, 9, 10'))},
{'Viewing Characteristics': (
 ('Zenith',            'ViewingZenith',       JTF, '20.0'),
 ('Azimuth',           'ViewingAzimuth',      JTF, '0.0'))},
{'Illumination Characteristics':(
 ('Zenith',            'IlluminationZenith',  JTF, '20.0'),
 ('Azimuth',           'IlluminationAzimuth', JTF, '0.0'))},
{'Scene Parameters': (
 ('Pixel Size',        'ScenePixel',          JTF, '8'),
 ('(Alt A) Filename',  'SceneLocFile',        JTF, ''),
 ('(Alt B) XC',        'SceneXC',             JTF, '-50'),
 ('(Alt B) XW',        'SceneXW',             JTF, '50'),
 ('(Alt B) YC',        'SceneYC',             JTF, '100'),
 ('(Alt B) YW',        'SceneYW',             JTF, '100'))},
{'Atmospheric Parameters': (
 ('Day of Year',       'AtmosphereDay',       JTF, '214'),
 (),
 ('Lat',               'AtmosphereLat',       JTF, '47.4781'),
 ('Long',              'AtmosphereLong',      JTF, '8.3650'),
 ('CO2 Mixing Ratio',  'AtmosphereCO2',       JTF, '1.6'),
 ('Aerosol Profile',   'AtmosphereAerosol',   JCB, (K_RURAL, K_MARITIME, K_URBAN, K_TROPOSPHERIC)),
 ('Water Vapor',       'AtmosphereWater',     JTF, '0.0'),
 ('Ozone Column',      'AtmosphereOzone',     JTF, '300'))},
{'Output Parameters': (
 ('Result file prefix','OutputPrefix',        JTF, 'RAMI_'),
 ('Result Directory',  'OutputDirectory',     JTF, ''),
 ('Image file',        'ImageFile',           JCB, (K_YES, K_NO)),
 ('Ascii file',        'AsciiFile',           JCB, (K_YES, K_NO)))}
)},
{'DHP Simulation': (
{'Model Selection': (
 ('3D Scene',          'DHP_3dScene',         JCB, (K_RAMI, K_LAEGEREN)),
 (),
 ('RT Processor',      'DHP_RTProcessor',     JCB, (K_LIBRAT, K_DART, K_DUMMY)),
 (),
 ('Resolution',        'DHP_Resolution',      JTF, '100x100'),
 ())},
{'DHP Location': (
 ('X',                 'DHP_X',               JTF, '0'),
 ('Y',                 'DHP_Y',               JTF, '0'))},
{'DHP Properties': (
 ('Zenith',            'DHP_Zenith',          JTF, '20.0'),
 ('Azimuth',           'DHP_Azimuth',         JTF, '0.0'))},
{'DHP Imaging Plane': (
 ('Orientation',       'DHP_Orientation',     JTF, '0'),
 ('Height(z)',         'DHP_Height',          JTF, '0'))},
{'Output Parameters': (
 ('Result file prefix','DHP_OutputPrefix',    JTF, 'RAMI00_'),
 ('Result Directory',  'DHP_OutputDirectory', JTF, ''),
 ('Image file',        'DHP_ImageFile',       JCB, (K_YES, K_NO)),
 ('Ascii file',        'DHP_AsciiFile',       JCB, (K_YES, K_NO)))}
)},
)
  # set parameter names
  for tabGroups in model:
    for tabName in tabGroups:
      for group in tabGroups[tabName]:
        for groupName in group:
          for groupTuple in group[groupName]:
            if len(groupTuple) == 4:
              (lbl, nm, typ, vals) = groupTuple
              exec('P_' + nm + ' = nm')
              exec('L_' + nm + ' = lbl')
              plst.append(nm)
  def me():
    nm = ''
    try:
      raise ZeroDivisionError
    except ZeroDivisionError:
      nm = sys.exc_info()[2].tb_frame.f_back.f_code.co_name
    return nm+'()'
  me = staticmethod(me)
  class StreamSync(Thread):
    def __init__(self, istr, logFileName, stype):
      self.istr  = istr; self.stype = stype
      if logFileName != None:
        logFile = File(logFileName)
        logFile.createNewFile()
        if (not logFile.canWrite()):
          raise RuntimeException("can't write to " + logFile.getAbsolutePath())
        self.writer = BufferedWriter(FileWriter(logFile, True))
      else:
        self.writer = None
    def run(self):
      try:
        line = None; br = BufferedReader(InputStreamReader(self.istr))
        line = br.readLine()
        while (line != None):
          if self.writer != None:
            self.writer.write(line + System.getProperty('line.separator'))
            self.writer.flush()
          else:
            VLAB.logger.info(self.stype + ": " + line)
          line = br.readLine()
        if self.writer != None:
          self.writer.close()
      except IOException, e:
        e.printStackTrace()

  def expandEnv(instr):
    outstr = instr
    m = {'$HOME':'HOME','%HOMEDRIVE%':'HOMEDRIVE','%HOMEPATH%':'HOMEPATH'}
    for e in m:
      if outstr.find(e) != -1:
        repl = System.getenv(m[e])
        if repl != None:
          outstr = outstr.replace(e, repl)
    return outstr
  expandEnv = staticmethod(expandEnv)

  def doExec(cmdrec):
    exitStatus = 0
    osName = System.getProperty('os.name')
    cmdLine = []
    if osName.startswith('Windows'):
      cmd=cmdrec['windows']
      cmdLine = ['cmd', '/c']
    elif (osName == 'Linux'):
      cmd=cmdrec['linux']
    else:
      raise RuntimeException('Unsupported OS ' + osName)
    exe = File(VLAB.expandEnv(cmd['exe']))
    if not exe.canExecute():
      raise RuntimeException("Can't find executable: " + exe.getAbsolutePath())
    cmdLine.append(exe.getAbsolutePath())

    for i in cmd['cmdline']:
      cmdLine.append(VLAB.expandEnv(i))
#    if osName.startswith('Windows'):
#      cmdLine.append(' <nul')
    
#    for cml in cmdLine:
#      (Logger.getLogger(VLAB.LOGGER_NAME)).info('cmdLine: ' + cml)
   
    #print 'cmdLine is ', cmdLine
    pb = ProcessBuilder(cmdLine)
    if cmd['cwd'] != None:
      pb.directory(File(VLAB.expandEnv(cmd['cwd'])))
    if cmd['env'] != None:
      env = pb.environment()
      cmdenv = cmd['env']
      for e in cmdenv:
        env[e] = VLAB.expandEnv(cmdenv[e])
    proc = pb.start()
    stdoutfName = None
    if cmd['stdout'] != None:
      stdoutfName = VLAB.expandEnv(cmd['stdout'])
    stderrfName = None
    if cmd['stderr'] != None:
      stderrfName = VLAB.expandEnv(cmd['stderr'])
    outs = VLAB.StreamSync(proc.getInputStream(), stdoutfName, 'out')
    errs = VLAB.StreamSync(proc.getErrorStream(), stderrfName, 'err')
    outs.start(); errs.start()
    if cmd['stdin'] != None:
      inFile = File(VLAB.expandEnv(cmd['stdin']))
      br = BufferedReader(FileReader(inFile))
      bw = BufferedWriter(OutputStreamWriter(proc.getOutputStream()))
      line = br.readLine()
      while (line != None):
        #print 'writing ', line
        bw.write(line + System.getProperty('line.separator'))
        line = br.readLine()
      br.close()
      bw.close()
    exitStatus = proc.waitFor()
    errs.join(); outs.join()
    (Logger.getLogger(VLAB.LOGGER_NAME)).info('returning exitStatus: %d' % exitStatus)
    return exitStatus
  doExec = staticmethod(doExec)

##
## Dummy implementation
##
class DUMMY:
  def __init__(self):
    me=self.__class__.__name__ +'::'+VLAB.me()
    VLAB.logger.info('VLAB %s: constructor completed' % me)

  def doProcessing(self, params):
    me=self.__class__.__name__ +'::'+VLAB.me()
    VLAB.logger.info('VLAB %s' % me)

    cmd = {
    'linux' : {
      'cwd'     : '$HOME/.beam/beam-vlab/auxdata/dummy_lin64/',
      'exe'     : '$HOME/.beam/beam-vlab/auxdata/dummy_lin64/dummy',
      'cmdline' : [ '-e', '1', '-r', '5' ],
      'stdin'   : None,
      'stdout'  : None,
      'stderr'  : None,
      'env'     : None
    },
    'windows' : {
      'cwd'     : '%HOMEDRIVE%%HOMEPATH%\\.beam\\beam-vlab\\auxdata\\dummy_win32',
      'exe'     : '%HOMEDRIVE%%HOMEPATH%\\.beam\\beam-vlab\\auxdata\\dummy_win32\\dummy.exe',
      'cmdline' : [ '-e', '1', '-r', '5' ],
      'stdin'   : None,
      'stdout'  : None,
      'stderr'  : None,
      'env'     : None
    }
    }
    VLAB.doExec(cmd)

##
## DART-specific integration glue
##
class DART:
  def __init__(self):
    me=self.__class__.__name__ +'::'+VLAB.me()
    VLAB.logger.info('VLAB %s: constructor completed...' % me)

  def doProcessing(self):
    me=self.__class__.__name__ +'::'+VLAB.me()

    VLAB.logger.info('VLAB %s: executing...' % me)
    cmd = {
    'linux' : {
      'cwd'     : '$HOME/.beam/beam-vlab/auxdata/dart_lin64/tools/lignes_commande/linux',
      'exe'     : '/bin/sh',
      'cmdline' : ['LancementDART_complet.sh', 'Laegeren'],
      'stdin'   : None,
      'stdout'  : None,
      'stderr'  : None,
      'env'     : None,
      },
    'windows'   : {
      'cwd'     : '%HOMEDRIVE%%HOMEPATH%\\.beam\\beam-vlab\\auxdata\\dart_win32\\tools\\lignes_commande',
      'exe'     : 'cmd.exe',
      'cmdline' : ['/c', 'echo', 'hello'],
      'stdin'   : None,
      'stdout'  : None,
      'stderr'  : None,
      'env'     : None,
     }
    }
    VLAB.doExec(cmd)

    VLAB.logger.info('VLAB %s: executing...' % me)
    cmd = {
    'linux' : {
      'cwd'     : '$HOME/.beam/beam-vlab/auxdata/dart_lin64/dart_local/simulations/Laegeren/output',
      'exe'     : '/bin/sh',
      'cmdline' : ['-c',
'for f in `find . -name *.mpr`; do gdal_translate -q -of netCDF $f `echo $f | sed -e \'s,mpr,nc,g\'`; done'],
      'stdin'   : None,
      'stdout'  : None,
      'stderr'  : None,
      'env'     : None,
      },
    'windows'   : {
      'cwd'     : '%HOMEDRIVE%%HOMEPATH%\\.beam\\beam-vlab\\auxdata\\dart_win32\\tools\\lignes_commande',
      'exe'     : 'cmd.exe',
      'cmdline' : ['/c', 'echo', 'hello'],
      'stdin'   : None,
      'stdout'  : None,
      'stderr'  : None,
      'env'     : None,
     }
    }
    VLAB.doExec(cmd)

##
## librat-specific integration glue
##
class LIBRAT:
  def __init__(self):
    me=self.__class__.__name__ +'::'+VLAB.me()
    VLAB.logger.info('VLAB %s: constructor completed...' % me)

  def _cmdHelper(self, cmdLine):
    VLAB.logger.info('VLAB commandLine is %s ' % ' '.join(cmdLine))
    cmd = {
    'linux' : {
      'cwd'     : '$HOME/.beam/beam-vlab/auxdata/librat_scenes',
      'exe'     : '/usr/bin/python',
      'cmdline' : cmdLine,
      'stdin'   : None,
      'stdout'  : None,
      'stderr'  : None,
      'env'     : {
        'BPMS'  : '$HOME/.beam/beam-vlab/auxdata/librat_lin64/'
      }},
    'windows'   : {
      'cwd'     : '%HOMEDRIVE%%HOMEPATH%\\.beam\\beam-vlab\\auxdata\\librat_scenes',
      'exe'     : 'python',
      'cmdline' : cmdLine,
      'stdin'   : None,
      'stdout'  : None,
      'stderr'  : None,
      'env'     : {
        'BPMS'  : '%HOMEDRIVE%%HOMEPATH%\\.beam\\beam-vlab\\auxdata\\librat_win32'
     }}
    }
    VLAB.doExec(cmd)

  def doProcessing(self, params):
    me=self.__class__.__name__ +'::'+VLAB.me()
    VLAB.logger.info('VLAB %s' % me)

    if params[VLAB.P_3dScene] == VLAB.K_RAMI:
      doRami = True
    else:
      doRami = False

    VLAB.logger.info('VLAB %s: scene is %s' % (me, params[VLAB.P_3dScene]))

    # 1. generate cosine-weighted angular samplines of view/illum hemisphere
    cmdline = ['./drivers.py', '-random', '-n', '1000', '-angles', 'angles.rpv.2.dat']
    self._cmdHelper(cmdline)

    # 2. simulate BRDF 
    if doRami:
      cmdline = ['./dobrdf.py', '-v', '-obj', 'HET01_DIS_UNI_NIR_20.obj', '-hips', '-wb', 'wb.MSI.dat', '-ideal', '80', '80', '-look',  '0', '0', '0', '-rpp', '1', '-npixels', '10000', '-boom', '786000', '-angles', 'angles.rpv.2.dat', '-opdir', 'rpv.rami']
    else:
      cmdline = ['./dobrdf.py', '-v', '-obj', 'laegeren.obj.lai.1', '-hips', '-wb', 'wb.MSI.dat', '-ideal', '300', '300', '-look', '150', '150', '710', '-rpp', '1', '-npixels', '10000', '-boom', '786000', '-angles', 'angles.rpv.2.dat', '-opdir', 'rpv.laegeren']

    self._cmdHelper(cmdline)

    # 3. collect BRDF simulations into a single file
    if doRami:
      cmdline = ['./plot.py', '-brdf', '-angles', 'angles.rpv.2.dat', '-root', 'rpv.rami.2/result.HET01_DIS_UNI_NIR_20.obj']
    else:
      cmdline = ['./plot.py', '-brdf', '-angles', 'angles.rpv.2.dat', '-root', 'rpv.laegeren/result.laegeren.obj.lai.1']
    self._cmdHelper(cmdline)

    # 4. invert the 3 parameter RPV model 
    if doRami:
      cmdline = ['./rpv_invert.py', '-three', '-v', '-plot', '-data', 'rpv.rami.2/result.HET01_DIS_UNI_NIR_20.obj.brdf.dat', '-paramfile', 'rpv.rami.2/result.HET01_DIS_UNI_NIR_20.obj.brdf.dat.3params.dat', '-plotfile', 'rpv.rami.2/result.HET01_DIS_UNI_NIR_20.obj.brdf.3params']
    else:
      cmdline = ['./rpv_invert.py', '-three', '-v', '-plot', '-data', 'rpv.laegeren/result.laegeren.obj.lai.1.brdf.dat', '-paramfile', 'rpv.laegeren/result.laegeren.obj.lai.1.brdf.dat.3params.dat', '-plotfile', 'rpv.laegeren/result.laegeren.obj.lai.1.brdf.3params']
    self._cmdHelper(cmdline)

    # 5. use the RPV paramaters to simulate TOA radiance
    if doRami:
      cmdline = ['./dolibradtran.py', '-opdir', 'rami.TOA', '-v', '-rpv', 'rpv.rami.2/result.HET01_DIS_UNI_NIR_20.obj.brdf.dat.3params.dat', '-plot', 'rami.TOA/rpv.rami.libradtran.dat.all', '-lat', '50', '-lon', '0', '-time', '2013 06 01 12 00 00']
    else:
      cmdline = ['./dolibradtran.py', '-opdir', 'laegeren.TOA', '-v', '-rpv', 'rpv.laegeren/result.laegeren.obj.lai.1.brdf.dat.3params.dat', '-plot', 'laegeren.TOA/rpv.laegeren.libradtran.dat.all', '-lat', '50', '-lon', '0', '-time', '2013 06 01 12 00 00']
    self._cmdHelper(cmdline)

# allow testing outside of beam
if System.getProperty("beam.version") == None:

  VLAB.logger.info("Running doExec() test...")
  cmd = {
  'linux' : {
    'cwd'     : '$HOME',
    'exe'     : '/bin/echo',
    'cmdline' : ['my', 'home', 'is', '$HOME'],
    'stdin'   : None,
    'stdout'  : None,
    'stderr'  : None,
    'env'     : None,
    },
  'windows'   : {
    'cwd'     : '%HOMEDRIVE%%HOMEPATH%',
    'exe'     : 'cmd.exe',
    'cmdline' : ['/c', 'echo', 'my', 'home', 'is', '%HOMEDRIVE%%HOMEPATH%'],
    'stdin'   : None,
    'stdout'  : None,
    'stderr'  : None,
    'env'     : None,
   }
  }
  #VLAB.doExec(cmd)

  params = {}
  params[VLAB.P_3dScene] = VLAB.K_RAMI

  #VLAB.logger.info("Running DUMMY.doProcessing() test...")
  #rtProcessor = DUMMY()
  #rtProcessor.doProcessing(params)

  VLAB.logger.info("Running LIBRAT.doProcessing() test...")
  rtProcessor = LIBRAT()
  rtProcessor.doProcessing(params)

else:

#
# BEAM-specific code from here to the end...
#

  from com.bc.ceres.core                       import ProgressMonitor
  from com.netcetera.vlab                      import IVLabProcessor
  from com.netcetera.vlab                      import IVLabProcessorUi
  from com.netcetera.vlab                      import VLabProcessor
  from com.netcetera.vlab                      import VLabUi

  from org.esa.beam.dataio.dimap               import DimapProductConstants;
  from org.esa.beam.framework.dataio           import ProductSubsetDef
  from org.esa.beam.framework.dataio           import ProductWriter
  from org.esa.beam.framework.datamodel        import PixelPos
  from org.esa.beam.framework.datamodel        import Product
  from org.esa.beam.framework.datamodel        import RasterDataNode
  from org.esa.beam.framework.dataop.dem       import ElevationModelDescriptor
  from org.esa.beam.framework.dataop.dem       import ElevationModelRegistry
  from org.esa.beam.framework.dataop.maptransf import MapInfo
  from org.esa.beam.framework.dataop.resamp    import ResamplingFactory
  from org.esa.beam.framework.param            import Parameter
  from org.esa.beam.framework.param            import ParamProperties
  from org.esa.beam.framework.param            import ParamValidateException
  from org.esa.beam.framework.param.validators import NumberValidator
  from org.esa.beam.framework.processor        import DefaultRequestElementFactory
  from org.esa.beam.framework.processor        import Processor
  from org.esa.beam.framework.processor        import ProcessorConstants
  from org.esa.beam.framework.processor        import ProcessorException
  from org.esa.beam.framework.processor        import ProcessorUtils
  from org.esa.beam.framework.processor        import ProductRef
  from org.esa.beam.framework.processor        import Request
  from org.esa.beam.framework.processor        import RequestElementFactory
  from org.esa.beam.framework.processor        import RequestElementFactoryException
  from org.esa.beam.framework.processor.ui     import ProcessorUI
  from org.esa.beam.framework.ui               import GridBagUtils
  from org.esa.beam.framework.ui               import UIUtils
  from org.esa.beam.util                       import Guardian

  ##
  ## BEAM-defined Processor implementation
  ##
  class VLabImpl(IVLabProcessor):

    def __init__(self):
      me=self.__class__.__name__ +'::'+VLAB.me()
      VLAB.logger.info('VLAB %s: VLabImpl constructor' % me)

    def getName(self):
      return VLAB.PROCESSOR_NAME

    def getSymbolicName(self):
      return VLAB.PROCESSOR_SNAME

    def getVersion(self):
      return VLAB.VERSION_STRING

    def getCopyrightInformation(self):
      return VLAB.COPYRIGHT_INFO

    def getUITitle(self):
      return VLAB.UI_TITLE

    def _getP(self, r, k):
      me=self.__class__.__name__ +'::'+VLAB.me()
      return r.getParameter(k).getValueAsText()

    def _doProcessing(self, pm, req):
      me=self.__class__.__name__ +'::'+VLAB.me()
      params = {}
      params[VLAB.P_3dScene] = self._getP(req, VLAB.P_3dScene)
      processor = self._getP(req, VLAB.P_RTProcessor)
      VLAB.logger.info('VLAB %s: processor is <%s' % (me, processor))
      if processor == VLAB.K_DART:
        rtProcessor = DART()
      elif processor == VLAB.K_LIBRAT:
        rtProcessor = LIBRAT()
      elif processor == VLAB.K_DUMMY:
        rtProcessor = DUMMY()
      else:
        raise RuntimeException('unknown processor: <' + processor + '>')

      pm.beginTask("Computing BRF...", 10)
      rtProcessor.doProcessing(params)
      # ensure at least 1 second to ensure progress popup feedback
      try:
        Thread.sleep(1000); 
      except JException, e:
        raise RuntimeException(e.getMessage())

    def process(self, pm, req):
      VLAB.logger.info('VLAB inside process...')
      me=self.__class__.__name__ +'::'+VLAB.me()
      ProcessorUtils.setProcessorLoggingHandler(VLAB.DEFAULT_LOG_PREFIX, 
        req, self.getName(), self.getVersion(), self.getCopyrightInformation())

      #for i in range(req.getNumParameters()):
      #  VLAB.logger.info(req.getParameterAt(i).getName() + " = " + req.getParameterAt(i).getValueAsText())

      #VLAB.logger.info(me + ': ' + ProcessorConstants.LOG_MSG_START_REQUEST)
      VLAB.logger.info('VLAB %s: %s' %(me, ProcessorConstants.LOG_MSG_START_REQUEST))
      pm.beginTask("Running 3D Vegetation Lab Processor...", 10)

      # ensure at least 1 second to ensure progress popup feedback
      try:
        Thread.sleep(1000); 
      except JException, e:
        raise RuntimeException(e.getMessage())

      self._doProcessing(pm, req)

      #VLAB.logger.info(me + ': ' + ProcessorConstants.LOG_MSG_FINISHED_REQUEST)
      VLAB.logger.info('VLAB %s : %s' % (me, ProcessorConstants.LOG_MSG_FINISHED_REQUEST))
      pm.done()

  ##
  ## BEAM-defined UI Implementation
  ##
  class VLabUiImpl(IVLabProcessorUi):
    def __init__(self):
      self._reqElemFac     = VLabRequestElementFactory() 
      self._defaultFactory = DefaultRequestElementFactory.getInstance()
      self._requestFile    = File('')
      self.pmap            = {} 

      me=self.__class__.__name__ +'::'+VLAB.me()
      VLAB.logger.info('VLAB %s: VLabUiImpl constructor' % me)

    def getGuiComponent(self):
      self._paramOutputProduct = self._reqElemFac.createDefaultOutputProductParameter()
      v = 2; h = 2;
      guiComponent = swing.JPanel(awt.BorderLayout())
      tabbedPane = swing.JTabbedPane()
      for tabGroups in VLAB.model:
        for tabName in tabGroups:
          tab = swing.JPanel()
          tab.layout = swing.BoxLayout(tab, swing.BoxLayout.PAGE_AXIS)
          tabbedPane.addTab(tabName, tab)
          for group in tabGroups[tabName]:
            tab.add(swing.JLabel(''))
            p = swing.JPanel()
            p.layout = awt.GridLayout(0, 4)
            p.layout.vgap = v; p.layout.hgap = h
            for groupName in group:
              p.border = swing.BorderFactory.createTitledBorder(groupName)
              for groupTuple in group[groupName]:
                if len(groupTuple) == 4:
                  (lbl, nm, typ, vals) = groupTuple
                  if type(vals) == tuple:
                    dflt = vals[0]
                  else:
                    dflt = vals
                  props = self._defaultFactory.createStringParamProperties()
                  props.setLabel(lbl)
                  props.setDefaultValue(dflt)
                  self._reqElemFac.pMap[nm] = props
                  if type(vals) == tuple:
                    self.pmap[nm] = Parameter(nm, dflt)
                    (self.pmap[nm]).getProperties().setValueSet(vals)
                    (self.pmap[nm]).getProperties().setValueSetBound(True)
                    (self.pmap[nm]).getProperties().setDefaultValue(dflt)
                    (self.pmap[nm]).getProperties().setLabel(lbl)
                  else:
                    self.pmap[nm] = self._reqElemFac.createParameter(nm, dflt)
                  #p.add((self.pmap[nm]).getEditor().getLabelComponent())
                  p.add(swing.JLabel(lbl+':', swing.SwingConstants.RIGHT))
                  p.add((self.pmap[nm]).getEditor().getComponent())
                else:
                  p.add(swing.JLabel(''))
                  p.add(swing.JLabel(''))
            tab.add(p)
          # hack
          for i in range(50):
            tab.add(swing.Box.createVerticalGlue())
      guiComponent.add(tabbedPane, awt.BorderLayout.NORTH)
      guiComponent.add(swing.JLabel(''), awt.BorderLayout.CENTER)
      VLabUi.setWindowSize(800, 800)
      return guiComponent

    def setRequests(self, requests):
      if (not requests.isEmpty()):
        for i in range(requests.size()):
          request = requests.elementAt(i)
          if (request == None):
            continue;
          if (str(VLAB.REQUEST_TYPE) == request.getType()):
            self._requestFile = request.getFile()
            outputProductAt = request.getOutputProductAt(0)
            if (outputProductAt != None):
              self._paramOutputProduct.setValueAsText(outputProductAt.getFilePath(), None)
            # update parameters
            for nm in VLAB.plst:
              (self.pmap[nm]).setValue(request.getParameter(nm).getValue())

  #          prefixParam = request.getParameter(ProcessorConstants.LOG_PREFIX_PARAM_NAME)
  #          if (prefixParam != None):
  #            self._logPrefixParameter.setValue(prefixParam.getValue(), None)
  #          logOutputParam = request.getParameter(ProcessorConstants.LOG_TO_OUTPUT_PARAM_NAME)
  #          if (logOutputParam != None):
  #            self._logToOutputParameter.setValue(logOutputParam.getValue(), None)
            break;
      else:
        self.setDefaultRequests()

    def setDefaultRequests(self):
      self.setDefaultRequest()

    def getRequests(self):
      requests = Vector()
      request = Request()
      request.setFile(self._requestFile)
      request.setType(VLAB.REQUEST_TYPE)
      outputFile = self._paramOutputProduct.getValueAsText()
      request.addOutputProduct(ProcessorUtils.createProductRef(outputFile, DimapProductConstants.DIMAP_FORMAT_NAME));
      for nm in VLAB.plst:
        request.addParameter(self._reqElemFac.createParameter(nm, (self.pmap[nm]).getValueAsText()))
      requests.add(request)
      return requests

    def setDefaultRequest(self):
      self._requestFile = None
      outputProductFile = self._paramOutputProduct.getValue()
      if (outputProductFile != None and outputProductFile.getParentFile() != None):
        parentFile = outputProductFile.getParentFile()
        self._paramOutputProduct.setValue(File(parentFile, VLAB.D_PRODNAME), None)
      else:
        self._paramOutputProduct.setDefaultValue()
      (self.pmap[VLAB.P_3dScene]).setDefaultValue()

  ##
  ## BEAM-defined mangement of processing parameters (aka request element)
  ##
  class VLabRequestElementFactory(RequestElementFactory):
    def __init__(self):
      self._defaultFactory = DefaultRequestElementFactory.getInstance()
      self.pMap = {}
      me=self.__class__.__name__ +'::'+VLAB.me()
      VLAB.logger.info('VLAB %s: VLabRequestElementFactory constructor' % me)
      
    def getInstance(self):
      return VLabRequestElementFactory()

    def createParameter(self, name, value):
      Guardian.assertNotNullOrEmpty("name", name)
      try:
        param = self.createParamWithDefaultValueSet(name)
        if (value != None):
          param.setValueAsText(value, None)
      except IllegalArgumentException, e:
        VLAB.logger.info('VLAB %s' % e.getMessage)
        raise RequestElementFactoryException(e.getMessage())
      return param
      
    def createDefaultInputProductParameter(self):
      return self._defaultFactory.createDefaultInputProductParameter()
     
    def createDefaultLogPatternParameter(self, prefix):
      return self._defaultFactory.createDefaultLogPatternParameter(prefix)
      
    def createDefaultOutputProductParameter(self):
      defaultOutputProductParameter = self._defaultFactory.createDefaultOutputProductParameter()
      properties = defaultOutputProductParameter.getProperties()
      defaultValue = properties.getDefaultValue()
      if (isinstance(defaultValue, File)):
        properties.setDefaultValue(File(defaultValue, VLAB.D_PRODNAME))
      defaultOutputProductParameter.setDefaultValue()
      return defaultOutputProductParameter
      
    def createInputProductRef(self, fileN, fileFmt, typeId):
      try:
        return self._defaultFactory.createInputProductRef(fileN, fileFmt, typeId)
      except RequestElementFactoryException, e:
        raise RequestElementFactoryException(e.getMessage())
      
    def createLogToOutputParameter(self, value):
      try:
        return self._defaultFactory.createLogToOutputParameter(value)
      except ParamValidateException, e:
        raise ParamValidateException(e.getMessage())
              
    def createOutputProductRef(self, fileN, fileFmt, typeId):
      try:
        return self._defaultFactory.createOutputProductRef(fileN, fileFmt, typeId)
      except RequestElementFactoryException, e:
        raise RequestElementFactoryException(e.getMessage())
      
    def createParamWithDefaultValueSet(self, paramName):
      paramProps = self.getParamInfo(paramName)
      param = Parameter(paramName, paramProps.createCopy())
      param.setDefaultValue()
      return param
      
    def getParamInfo(self, parameterName):
      paramProps = self.pMap[parameterName]
      if (paramProps == None):
        if (parameterName.endsWith(VLAB.P_EXPRESSION)):
          ''
          VLAB.logger.info('%s: to be implemented' % VLAB.P_EXPRESSION)
        elif (parameterName.endsWith(VLAB.P_CONDITION)):
          ''
          VLAB.logger.info('%s: to be implemented' % VLAB.P_CONDITION)
        elif (parameterName.endsWith(VLAB.P_OUTPUT)):
          ''
          VLAB.logger.info('%s: to be implemented' & VLAB.P_OUTPUT)

      if (paramProps == None):
        raise IllegalArgumentException("Invalid parameter name '" + parameterName + "'.")
      return paramProps

    def createStringParamProperties(self):
      return self._defaultFactory.createStringParamProperties()
