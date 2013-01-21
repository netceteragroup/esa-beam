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
# Authors: Daniel Kueckenbrink, Joshy Cyriac, Marcel Kessler, Jason Brazile
#
import sys

from array import *
from java import io
from java import lang
from java.io import BufferedReader
from java.io import BufferedWriter
from java.io import File
from java.io import FileReader
from java.io import FileWriter
from java.io import FileInputStream
from java.io import FileOutputStream
from java.io import InputStreamReader
from java.io import OutputStreamWriter
from java.io import IOException
from java.lang import IllegalArgumentException
from java.lang import Integer
from java.lang import ProcessBuilder
from java.lang import Exception as JException
from java.lang import RuntimeException
from java.lang import String as JString
from java.lang import System
from java.lang import Thread
from java.lang import ProcessBuilder
from java.nio.channels import FileChannel
from java.util import HashMap
from java.util import Map
from java.util.logging import Logger

import javax.swing as swing
import java.awt as awt

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

##
## Vegetation Lab constants, "data model", utilities etc
##
class VLAB:
  COPYRIGHT_INFO     = ''
  PROCESSOR_NAME     = 'BEAM VLab Processor'
  PROCESSOR_SNAME    = 'beam-vlab'
  REQUEST_TYPE       = 'VLAB'
  UI_TITLE           = 'VLab - Processor'
  VERSION_STRING     = '0.1'
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

  K_SENTINEL2        = 'Sentinel-2'
  K_SENTINEL3        = 'Sentinel-3'
  K_MODIS            = 'Modis'
  K_MERIS            = 'Meris'
  K_LANDSAT          = 'Landsat'

  K_RURAL            = 'Rural'
  K_MARITIME         = 'Maritime'
  K_URBAN            = 'Urban'
  K_TROPOSPHERIC     = 'Tropospheric'
  plst = []

  model = (
{'Forward Modeling': (
{'Model Selection': (
 ('3D Scene',          '3dScene',             JCB, (K_RAMI, K_LAEGEREN)),
 ('RT Processor',      'RTProcessor',         JCB, (K_LIBRAT, K_DART, K_DUMMY)))},
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
 (),
 ('XC',                'SceneXC',             JTF, '-50'),
 ('XW',                'SceneXW',             JTF, '50'),
 ('YC',                'SceneYC',             JTF, '100'),
 ('YW',                'SceneYW',             JTF, '100'))},
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
 ('Result file prefix','OutputPrefix',        JTF, 'RAMI00_'),
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
 ('Azimuth',           'DHP_Azaimuth',        JTF, '0.0'))},
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

  def dependsOn(who,what):
    if (not (File(what)).exists()):
      (Logger.getLogger(VLAB.LOGGER_NAME)).info(JString.format ("Error: \"%s\" expected \"%s\" to exist", [who, what]))
  dependsOn = staticmethod(dependsOn)
  def created(who,what):
    if (not (File(what)).exists()):
      (Logger.getLogger(VLAB.LOGGER_NAME)).info(JString.format ("Error: \"%s\" failed to generate \"%s\"", [who, what]))
  created = staticmethod(created)
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
            self.writer.write(line + System.lineSeparator())
            self.writer.flush()
          else:
            (Logger.getLogger(VLAB.LOGGER_NAME)).info(
              self.stype + ": " + line + System.lineSeparator())
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
    
    for cml in cmdLine:
      (Logger.getLogger(VLAB.LOGGER_NAME)).info('cmdLine: ' + cml)
   
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
      inFile = File(cmd['stdin'])
      if cmd['cwd'] != None:
        inFile = File(VLAB.expandEnv(cmd['cwd']), cmd['stdin'])
      br = BufferedReader(FileReader(inFile))
      bw = BufferedWriter(OutputStreamWriter(proc.getOutputStream()))
      line = br.readLine()
      while (line != None):
        #print 'writing ', line
        bw.write(line)
        line = br.readLine()
      br.close()
      bw.close()
    exitStatus = proc.waitFor()
    errs.join(); outs.join()
    (Logger.getLogger(VLAB.LOGGER_NAME)).info('returning exitStatus: ' + JString.format("%d", [exitStatus]))
    return exitStatus
  doExec = staticmethod(doExec)


##
## BEAM-defined Processor implementation
##
class VLabImpl(IVLabProcessor):

  def __init__(self):
    self._log = Logger.getLogger(VLAB.LOGGER_NAME)
    me=self.__class__.__name__ +'::'+VLAB.me()
    self._log.info(me + ": constructor completed...")

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

  def _doBRF(self, pm, req):
    me=self.__class__.__name__ +'::'+VLAB.me()
    processor = self._getP(req, VLAB.P_RTProcessor)
    self._log.info(me + ": processor is <" + processor + ">")
    if processor == VLAB.K_DART:
      rtProcessor = DART()
    elif processor == VLAB.K_LIBRAT:
      rtProcessor = LIBRAT()
    elif processor == VLAB.K_DUMMY:
      rtProcessor = DUMMY()
    else:
      raise RuntimeException('unknown processor: <' + processor + '>')

    rtProcessor.doTopOfCanopyBRF()
    radProcessor = RADTRAN()
    radProcessor.doTopOfAtmosphereBRF()

  def process(self, pm, req):
    self._log.info("inside process...")
    me=self.__class__.__name__ +'::'+VLAB.me()
    ProcessorUtils.setProcessorLoggingHandler(VLAB.DEFAULT_LOG_PREFIX, 
      req, self.getName(), self.getVersion(), self.getCopyrightInformation())

    #self._log.info("Parameter list:")
    #for i in range(req.getNumParameters()):
    #  self._log.info(req.getParameterAt(i).getName() + " = " + req.getParameterAt(i).getValueAsText())

    self._log.info(me + ': ' + ProcessorConstants.LOG_MSG_START_REQUEST)
    pm.beginTask("Running 3D Vegetation Lab Processor...", 10)

    # ensure at least 1 second to ensure progress popup feedback
    try:
      Thread.sleep(1000); 
    except JException, e:
      raise RuntimeException(e.getMessage())

    self._doBRF(pm, req)

    self._log.info(me + ': ' + ProcessorConstants.LOG_MSG_FINISHED_REQUEST)
    pm.done()

##
## BEAM-defined UI Implementation
##
class VLabUiImpl(IVLabProcessorUi):
  def __init__(self):
    self._log            = Logger.getLogger(VLAB.LOGGER_NAME)
    self._reqElemFac     = VLabRequestElementFactory() 
    self._defaultFactory = DefaultRequestElementFactory.getInstance()
    self._requestFile    = File('')
    self.pmap            = {} 

    me=self.__class__.__name__ +'::'+VLAB.me()
    self._log.info(me + ": constructor completed...")

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
    self._log            = Logger.getLogger(VLAB.LOGGER_NAME)
    self._defaultFactory = DefaultRequestElementFactory.getInstance()
    self.pMap = {}
    me=self.__class__.__name__ +'::'+VLAB.me()
    self._log.info(me + ": constructor completed...")
    
  def getInstance(self):
    return VLabRequestElementFactory()

  def createParameter(self, name, value):
    Guardian.assertNotNullOrEmpty("name", name)
    try:
      param = self.createParamWithDefaultValueSet(name)
      if (value != None):
        param.setValueAsText(value, None)
    except IllegalArgumentException, e:
      self._log.info(e.getMessage)
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
        self._log.info("has to be implemented!!")
      elif (parameterName.endsWith(VLAB.P_CONDITION)):
        ''
        self._log.info("has to be implemented!!")
      elif (parameterName.endsWith(VLAB.P_OUTPUT)):
        ''
        self._log.info( "has to be implemented!!")

    if (paramProps == None):
      raise IllegalArgumentException("Invalid parameter name '" + parameterName + "'.")
    return paramProps

  def createStringParamProperties(self):
    return self._defaultFactory.createStringParamProperties()

##
## Dummy implementation
##
class DUMMY:
  def __init__(self):
    self._log = Logger.getLogger(VLAB.LOGGER_NAME)
    me=self.__class__.__name__ +'::'+VLAB.me()
    self._log.info(me + ": constructor completed...")
  
  def doTopOfCanopyBRF(self):
    me=self.__class__.__name__ +'::'+VLAB.me()
    self._log.info(me)
    cmd = {
    'linux' : {
      'cwd'     : '$HOME/.beam/beam-vlab/auxdata/dummy_linux/',
      'exe'     : '$HOME/.beam/beam-vlab/auxdata/dummy_linux/dummy',
      'cmdline' : [ '-e', '1', '-r', '5' ],
      'stdin'   : None,
      'stdout'  : None,
      'stderr'  : None,
      'env'     : None
    },
    'windows' : {
      'cwd'     : '%HOMEDRIVE%%HOMEPATH%\\.beam\\beam-vlab\\auxdata\\dummy_windows',
      'exe'     : '%HOMEDRIVE%%HOMEPATH%\\.beam\\beam-vlab\\auxdata\\dummy_windows\\dummy.exe',
      'cmdline' : [ '-e', '1', '-r', '5' ],
      'stdin'   : None,
      'stdout'  : 'dummyout.txt',
      'stderr'  : 'dummyerr.txt',
      'env'     : None
    }
    }
    # NOT YET - hangs on XP for some reason
    #VLAB.doExec(cmd)


##
## DART-specific integration glue
##
class DART:
  def __init__(self):
    self._log = Logger.getLogger(VLAB.LOGGER_NAME)
    me=self.__class__.__name__ +'::'+VLAB.me()
    self._log.info(me + ": constructor completed...")
  
  def _createScene(self):
    me=self.__class__.__name__ +'::'+VLAB.me()
    self._log.info(me)
    VLAB.dependsOn(me, "locations.dat")
    VLAB.dependsOn(me, "soil.dat")
    self._log.info(me + ": executing...")
    #
    # [more would happen here]
    #
    VLAB.created(me,   "object_3d.obj")

  def _runSimulation(self):
    me=self.__class__.__name__ +'::'+VLAB.me()
    self._log.info(me)
    VLAB.dependsOn(me, "atmosphere.xml")
    VLAB.dependsOn(me, "coef_diff.xml")
    VLAB.dependsOn(me, "directions.xml")
    VLAB.dependsOn(me, "inversion.xml")
    VLAB.dependsOn(me, "maket.xml")
    VLAB.dependsOn(me, "object_3d.xml")
    VLAB.dependsOn(me, "phase.xml")
    VLAB.dependsOn(me, "plots.xml")
    VLAB.dependsOn(me, "trees.xml")
    VLAB.dependsOn(me, "triangleFile.xml")
    VLAB.dependsOn(me, "urban.xml")
    VLAB.dependsOn(me, "water.xml")
    self._log.info(me + ": executing...")
    #
    # [more would happen here]
    #
    VLAB.created(me, "BAND0")
    VLAB.created(me, "dart.txt")
    VLAB.created(me, "directions.txt")
    VLAB.created(me, "lib_phase")
    VLAB.created(me, "Maket_trees_result.txt")
    VLAB.created(me, "maket.txt")
    VLAB.created(me, "output_console_dart.txt")
    VLAB.created(me, "output_console_directions.txt")
    VLAB.created(me, "output_console_maket.txt")
    VLAB.created(me, "output_console_phase.txt")
    VLAB.created(me, "simulation_properties.txt")
    VLAB.created(me, "triangles.txt")

  def doTopOfCanopyBRF(self):
    me=self.__class__.__name__ +'::'+VLAB.me()
    self._log.info(me)
    self._createScene()
    self._runSimulation()

##
## librat-specific integration glue
##
class LIBRAT:
  def __init__(self):
    self._log = Logger.getLogger(VLAB.LOGGER_NAME)
    me=self.__class__.__name__ +'::'+VLAB.me()
    self._log.info(me + ": constructor completed...")

  def _createScene(self):
    me=self.__class__.__name__ +'::'+VLAB.me()
    self._log.info(me)
    VLAB.dependsOn(me, "locations.dat")
    VLAB.dependsOn(me, "soil.dat")
    self._log.info(me + ": executing...")
    #
    # more would happen here
    #
    VLAB.created(me,   "vlab-librat.obj")

  def _runSimulation(self):
    me=self.__class__.__name__ +'::'+VLAB.me()
    self._log.info(me)
    VLAB.dependsOn(me, "camera_field.dat")
    VLAB.dependsOn(me, "light_file.dat")
    VLAB.dependsOn(me, "plants.matlib")
    VLAB.dependsOn(me, "sphere.dat")
    VLAB.dependsOn(me, "wavebands_file.dat")
    self._log.info(me + ": executing...")

    cmd = {
    'linux' : {
      'cwd'     : '$HOME/.beam/beam-vlab/auxdata/librat_linux/src/start',
      'exe'     : '$HOME/.beam/beam-vlab/auxdata/librat_linux/src/start/start',
      'cmdline' : [
        '-sensor_wavebands', 'wavebands.dat', '-m', '100',
        '-sun_position', '0', '0', '10', 'test.obj'],
      'stdin'   : 'starttest.ip',
      'stdout'  : None,
      'stderr'  : None,
      'env'     : {
        'LD_LIBRARY_PATH' : '$HOME/.beam/beam-vlab/auxdata/librat_linux/src/lib/',
        'BPMS'  : '$HOME/.beam/beam-vlab/auxdata/librat_linux/'
      }},
    'windows'   : {
      'cwd'     : '%HOMEDRIVE%%HOMEPATH%\\.beam\\beam-vlab\\auxdata\\librat_windows\\src\\start',
      'exe'     : '%HOMEDRIVE%%HOMEPATH%\\.beam\\beam-vlab\\auxdata\\librat_windows\\src\\start\\ratstart.exe',
      'cmdline' : [
        '-sensor_wavebands', 'wavebands.dat', '-m', '100',
        '-sun_position', '0', '0', '10', 'test.obj'],
      'stdin'   : 'starttest.ip',
      'stdout'  : None,
      'stderr'  : None,
      'env'     : {
        'BPMS'  : '%HOMEPATH%\\.beam\\beam-vlab\\auxdata\\librat_windows'
     }}
    }
    # NOT YET - hangs on XP for some reason
    # VLAB.doExec(cmd)

    #
    # [more would happen here]
    #
    VLAB.created(me, "result.dat")
    VLAB.created(me, "result.dat.diffuse")
    VLAB.created(me, "result.dat.direct")
    VLAB.created(me, "result.dat.hips")

  def doTopOfCanopyBRF(self):
    me=self.__class__.__name__ +'::'+VLAB.me()
    self._log.info(me)
    self._createScene()
    self._runSimulation()

##
## libradtran-specific integration glue
##
class RADTRAN:
  def __init__(self):
    self._log = Logger.getLogger(VLAB.LOGGER_NAME)
    me=self.__class__.__name__ +'::'+VLAB.me()
    self._log.info(me + ": constructor completed...")
    self._log.info(me + ": returning...")

  def doTopOfAtmosphereBRF(self):
    me=self.__class__.__name__ +'::'+VLAB.me()
    VLAB.dependsOn(me, "input.dat");
    self._log.info(me + ": executing...")
    #
    # [more would happn here]
    #
    VLAB.created(me,  "output.dat")

