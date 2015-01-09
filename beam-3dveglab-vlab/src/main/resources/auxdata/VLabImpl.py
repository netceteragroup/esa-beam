#
# Copyright (C) 2010-2014 Netcetera Switzerland (info@netcetera.com)
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
# Authors: Mat Disney, Cyrill Schenkel, Fabian Schneider, Nicolas Lauret, Tristan Gregoire, Daniel Kueckenbrink, Joshy Cyriac, Marcel Kessler, Jason Brazile
#

##############################################################################
# Two ways to run:
#
# 1. Embedded within BEAM's 3DVegLab processor (normal case)
# 2. Stand-alone with a "fake beam" swig-based GUI
#
# windows:
# set BEAMDIR="C:\data\Program Files (x86)\beam-4.11"
# %BEAMDIR%\jre\bin\java -jar %BEAMDIR%\lib\jython-2.5.2.jar -Dvlab.fakebeam=1 -Dpython.path=%BEAMDIR%\lib\jcommon-1.0.16.jar;%BEAMDIR%\lib\jfreechart-1.0.13.jar;%BEAMDIR%\lib\lbfgsb_wrapper-1.1.3.jar %HOMEDRIVE%%HOMEPATH%\.beam\beam-vlab\auxdata\VLabImpl.py
#
# linux:
# ${HOME}/beam-4.11/jre/bin/java -jar ${HOME}/beam-4.11/lib/jython-2.5.2.jar -Dvlab.fakebeam=1 -Dpython.path=${HOME}/beam-4.11/lib/jcommon-1.0.16.jar:${HOME}/beam-4.11/lib/jfreechart-1.0.13.jar:${HOME}/beam-4.11/lib/lbfgsb_wrapper-1.1.3.jar ${HOME}/.beam/beam-vlab/auxdata/VLabImpl.py
#
# Note: those BEAM-supplied jars can also be obtained like this:
#    wget -U "Mozilla/5.0" http://repo1.maven.org/maven2/jfree/jfreechart/1.0.13/jfreechart-1.0.13.jar
#    wget -U "Mozilla/5.0" http://repo1.maven.org/maven2/jfree/jcommon/1.0.16/jcommon-1.0.16.jar
#
#

import sys, math, operator, array, time, struct
from array import array

class VLAB:
  """VLAB contains conf. constants, static utility methods, and test methods"""

  COPYRIGHT_INFO     = 'Copyright (C) 2010-2014 Netcetera Switzerland (info@netcetera.com)'
  PROCESSOR_NAME     = 'BEAM VLab Processor'
  PROCESSOR_SNAME    = 'beam-vlab'
  REQUEST_TYPE       = 'VLAB'
  UI_TITLE           = 'VLab - Processor'
  VERSION_STRING     = '1.0 (09 Jan 2014)'
  DEFAULT_LOG_PREFIX = 'vlab'
  LOGGER_NAME        = 'beam.processor.vlab'

  D_PRODNAME         = 'vlab_out.dim'
  P_CONDITION        = '.condition'
  P_EXPRESSION       = '.expression'
  P_OUTPUT           = '.output'

  # NOTE: Once released, random number generation should NOT be reproducible
  CONF_RND_REPRODUCE = True

  # NOTE: # of threads DART will use - should be <= your total CPU cores
  CONF_DART_N_THREAD = 4

  JCB                = 'JComboBox'
  JTF                = 'JTextField'
  JTD                = (JTF, False)

  K_LIBRAT           = 'librat'
  K_DART             = 'DART'
  K_DUMMY            = 'dummy'

  K_LAEGERN          = 'Laegern'
  K_THARANDT         = 'Tharandt'
  K_RAMI             = 'RAMI'
  K_USER_DEFINED     = '(UserDefined.obj)'

  K_YES              = 'Yes'
  K_NO               = 'No'

  K_SENTINEL2        = 'MSI (Sentinel 2)'
  K_SENTINEL3        = 'OLCI (Sentinel 3)'
  K_MODIS            = 'MODIS'
  K_MERIS            = 'MERIS'
  K_LANDSAT_OLI      = 'Landsat (OLI)'
  K_LANDSAT_ETM      = 'Landsat (ETM)'

  K_RURAL            = 'Rural'
  K_MARITIME         = 'Maritime'
  K_URBAN            = 'Urban'
  K_TROPOSPHERIC     = 'Tropospheric'

  DBG                = 'debug'
  INF                = 'info'
  ERR                = 'error'

  plst               = []

  if sys.platform.startswith('java'):
    from java.util.logging import Logger
    from java.util.logging import FileHandler
    from java.util.logging import Level
    logger = Logger.getLogger(LOGGER_NAME)
    # comment these out
    # logfh = FileHandler('%s.log' % LOGGER_NAME)
    # logfh.setLevel(Level.FINEST)
    # logger.addHandler(logfh)
  else:
    import logging
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)
    logch = logging.StreamHandler()
    logch.setLevel(logging.DEBUG)
    logger.addHandler(logch)
    # comment these out
    # logfh = logging.FileHandler('%s.log' % LOGGER_NAME)
    # logfh.setLevel(logging.DEBUG)
    # logger.addHander(logfh)

  model = (
{'Forward Modeling': (
{'Model Selection': (
 ('3D Scene',          '3dScene',             JCB, (K_RAMI, K_LAEGERN, K_THARANDT, K_USER_DEFINED)),
 ('RT Processor',      'RTProcessor',         JCB, (K_DUMMY, K_LIBRAT, K_DART)))},
{'Spectral Characteristics': (
 ('Sensor',            'Sensor',              JCB, (K_SENTINEL2, K_SENTINEL3, K_MODIS, K_MERIS, K_LANDSAT_OLI, K_LANDSAT_ETM)),
 ('Bands',             'Bands',               JTD, 'full set for sensor'))},
{'Viewing Characteristics': (
 ('Zenith',            'ViewingZenith',       JTF, '20.0'),
 ('Azimuth',           'ViewingAzimuth',      JTF, '0.0'))},
{'Illumination Characteristics':(
 ('Zenith',            'IlluminationZenith',  JTF, '20.0'),
 ('Azimuth',           'IlluminationAzimuth', JTF, '0.0'))},
{'Scene Parameters': (
 ('Pixel Size',        'ScenePixel',          JTD, 'not available yet'),
 ('(Alt A) Filename',  'SceneLocFile',        JTD, 'not available yet'),
 ('(Alt B) XC',        'SceneXC',             JTD, 'not available yet'),
 ('(Alt B) XW',        'SceneXW',             JTD, 'not available yet'),
 ('(Alt B) YC',        'SceneYC',             JTD, 'not available yet'),
 ('(Alt B) YW',        'SceneYW',             JTD, 'not available yet'))},
{'Atmospheric Parameters': (
 ('CO2 Mixing Ratio',  'AtmosphereCO2',       JTF, '1.6'),
 ('Aerosol Profile',   'AtmosphereAerosol',   JCB, (K_RURAL, K_MARITIME, K_URBAN, K_TROPOSPHERIC)),
 ('Water Vapor',       'AtmosphereWater',     JTF, '0.0'),
 ('Ozone Column',      'AtmosphereOzone',     JTF, '300'))},
{'Output Parameters': (
 ('Result file prefix','OutputPrefix',        JTF, 'HET01_DIS_UNI_NIR_20.obj'),
 ('Result Directory',  'OutputDirectory',     JTF, 'dart.rpv.rami.2'),
 ('Image file',        'ImageFile',           JCB, (K_YES, K_NO)),
 ('Ascii file',        'AsciiFile',           JCB, (K_YES, K_NO)))}
)},
{'DHP Simulation': (
{'Model Selection': (
 ('3D Scene',          'DHP_3dScene',         JCB, (K_RAMI, K_LAEGERN, K_THARANDT)),
 (),
 ('Resolution',        'DHP_Resolution',      JTF, '4000000'),
 ())},
{'DHP Location': (
 ('X',                 'DHP_X',               JTD, 'not available yet'),
 ('Y',                 'DHP_Y',               JTD, 'not available yet'))},
{'DHP Properties': (
 ('Zenith',            'DHP_Zenith',          JTF, '0.0'),
 ('Azimuth',           'DHP_Azimuth',         JTF, '0.0'))},
{'DHP Imaging Plane': (
 ('Orientation',       'DHP_Orientation',     JTD, 'not available yet'),
 ('Height(z)',         'DHP_Height',          JTD, 'not available yet'))},
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

  def __init__(self):
    self.cmap = {}
    self.vmap = {}

  def me():
    """Returns name of currently executing method"""
    nm = ''
    try:
      raise ZeroDivisionError
    except ZeroDivisionError:
      nm = sys.exc_info()[2].tb_frame.f_back.f_code.co_name
    return nm+'()'
  me = staticmethod(me)
  def lineSeparator():
    """Return the OS line separator"""
    if sys.platform.startswith('java'):
      from java.lang import System
      if sys.platform.startswith('java1.6'):
        return System.getProperty('line.separator')
      elif sys.platform.startswith('java1.7'):
        return System.lineSeparator()
    else:
      import os
      os.linesep
  lineSeparator = staticmethod(lineSeparator)
  def listdir(path):
    """list files in the directory given by path"""
    if sys.platform.startswith('java'):
      from java.io import File
      array = File(path).list()
      listFile = []
      if array != None:
        for i in xrange(len(array)):
          listFile.append(array[i])
      return listFile
    else:
      import os
      return os.listdir(path)
  listdir = staticmethod(listdir)
  def renameFile(src,dst):
    VLAB.logger.info("renaming " + src + " to " + dst)
    if sys.platform.startswith('java'):
      from java.io import File
      srcf = File(src)
      if not srcf.exists():
        VLAB.logger.info("source file: " + srcf.toString() + " does not exist")
      dstf = File(dst)
      if dstf.exists():
        VLAB.logger.info("dest file: " + dstf.toString() + " already exists")
      if not srcf.renameTo(dstf):
        VLAB.logger.info("rename to " + dstf.toString() + " failed")
    else:
      import os
      os.rename(src, dst)
  renameFile = staticmethod(renameFile)
  def getenv(key, default=None):
    if sys.platform.startswith('java'):
      from java.lang.System import getenv
      return getenv(key)
    else:
      import os
      return os.getenv(key)
  getenv = staticmethod(getenv)
  def checkFile(fname):
    """open a file if it exists, otherwise die"""
    try:
      fp = open(fname, 'r+')
      return fp
    except IOError, e:
      raise RuntimeError(e)
  checkFile = staticmethod(checkFile)
  def fileExists(fname):
    """check if fname exists as a file"""
    if sys.platform.startswith('java'):
      from java.io import File
      return File(fname).exists()
    else:
      import os
      return os.path.exists(fname)
  fileExists = staticmethod(fileExists)
  def getFullPath(fname):
    """return canonical/absolute path of given fname"""
    if sys.platform.startswith('java'):
      from java.io import File
      return File(fname).getCanonicalPath()
    else:
      import os
      return os.path.abspath(fname)
  getFullPath = staticmethod(getFullPath)
  def copyDir(dname, target):
    """Recursively copy 'dname' directory to 'target'.
       /!\If 'target' already exists it will be removed or overwrited.
    """
    if sys.platform.startswith('java'):
      # import java module
      from java.io import File
      from java.io import FileInputStream
      from java.io import FileOutputStream
      from java.util import Scanner
      from java.lang import String
      dnameFile = File(dname)
      targetFile = File(target)
      # recursive copy
      if dnameFile.isDirectory():
        # Create folder if not exists
        if not targetFile.exists():
          targetFile.mkdir()
        # Copy all content recursively
        for fname in dnameFile.list().tolist():
          VLAB.copyDir(dname + File.separator + fname, target + File.separator + fname)
      else:
        # Read dname file
        istream = FileInputStream(dname)
        scan = Scanner(istream).useDelimiter("\\Z")
        # Test if file is empty
        if scan.hasNextLine():
          content = String(scan.next())
        else:
          content = String("")
        scan.close()
        # Create and write target
        if not targetFile.exists():
          targetFile.createNewFile()
        ostream = FileOutputStream(target)
        ostream.write(content.getBytes())
        ostream.flush()
        ostream.close()
    else:
      import shutil, os
      # remove exisiting target
      if os.path.isdir(target) or os.path.isfile(target):
        shutil.rmtree(target)
      # recursive copy of dnma to target
      shutil.copytree(dname, target)
  copyDir = staticmethod(copyDir)
  def getAvailProcessors():
    # most modern machines have >= 2 CPUs with hyperthreading
    nAvailableProcessors = 4
    if sys.platform.startswith('java'):
      from java.lang import Runtime
      nAvailableProcessors = Runtime.getRuntime().availableProcessors()
    return nAvailableProcessors
  getAvailProcessors = staticmethod(getAvailProcessors)
  def XMLEditNode(fname, nodeName, attributName, value, multiple=False):
    """ Edit a given node (nodeName) in a given XML file (fname)
    attributName and value could be either a list of string or a string
    """
    if sys.platform.startswith('java'):
      from javax.xml.parsers import DocumentBuilderFactory
      from javax.xml.transform import TransformerFactory
      from javax.xml.transform import OutputKeys
      from javax.xml.transform.dom import DOMSource
      from javax.xml.transform.stream import StreamResult
      from java.io import File
      # Get whole tree
      tree = DocumentBuilderFactory.newInstance().newDocumentBuilder().parse(fname)
      # Get nodeName
      node = tree.getElementsByTagName(nodeName)
      # Check if we get only one node (as expected)
      if node.getLength() == 0:
        raise IOError("Cannot find '%s' in file '%s'" % (nodeName, fname))
      elif node.getLength() == 1:
        nodes = [node.item(0)]
      else:
        if not multiple:
          raise IOError("Get multiple nodes for '%s' in file '%s'" % (nodeName, fname))
        else:
          nodes = [ node.item(i) for i in xrange(node.getLength()) ]
      for node in nodes:
        # Modify the node attribute
        if isinstance(attributName, list) and isinstance(value, list):
          for att, val in zip(attributName, value):
            node.setAttribute(att, val)
        elif isinstance(attributName, str) and isinstance(value, str):
          node.setAttribute(attributName, value)
        else:
          raise ValueError("Wrong parameter used: attributName and value should be both either a list of string or a string")
      # Write new XML tree in fname
      transformer = TransformerFactory.newInstance().newTransformer()
      transformer.setOutputProperty(OutputKeys.INDENT, "yes")
      source = DOMSource(tree)
      result = StreamResult(File(fname))
      transformer.transform(source, result)
    else:
      import xml.etree.ElementTree as ET
      # Get whole tree from xml
      tree = ET.parse(fname)
      # Get nodeName
      #nodes = tree.findall(".//*%s" % nodeName) # This line seems to not work for root child node!! Bug?
      nodes = tree.findall(".//*../%s" % nodeName)
      # Check if we get only one node (as expected)
      if len(nodes) == 0:
        raise IOError("Cannot find '%s' in file '%s'" % (nodeName, fname))
      elif len(nodes) > 1 and not multiple:
        raise IOError("Get multiple nodes for '%s' in file '%s'" % (nodeName, fname))
      for node in nodes:
        # Modify the node attribute
        if isinstance(attributName, list) and isinstance(value, list):
          for att, val in zip(attributName, value):
            node.set(att, val)
        elif isinstance(attributName, str) and isinstance(value, str):
          node.set(attributName, value)
        else:
          raise ValueError("Wrong parameter used: attributName and value should be both either a list of string or a string")
      # Write new XML tree in fname
      tree.write(fname)
  XMLEditNode = staticmethod(XMLEditNode)
  def XMLReplaceNodeContent(fname, parent, subnode, attributName, value, spectralBands=False):
    """ Edit an XML file (fname) and replace the content of a node with subnode(s) (subnode) within attribute(s) and value(s).
    attributName and value could be either a list of string or a string
    """
    if sys.platform.startswith('java'):
      from javax.xml.parsers import DocumentBuilderFactory
      from javax.xml.transform import TransformerFactory
      from javax.xml.transform import OutputKeys
      from javax.xml.transform.dom import DOMSource
      from javax.xml.transform.stream import StreamResult
      from java.io import File
      # Get whole tree
      tree = DocumentBuilderFactory.newInstance().newDocumentBuilder().parse(fname)
      # Get nodeName
      node = tree.getElementsByTagName(parent)
      # Check if we get only one node (as expected)
      if node.getLength() > 1:
        raise IOError("Get multiple nodes for '%s' in file '%s'" % (parent, fname))
      elif node.getLength() == 0:
        raise IOError("Cannot find '%s' in file '%s'" % (parent, fname))
      else:
        node = node.item(0)
      # Remove content node
      while node.hasChildNodes():
        node.removeChild(node.getFirstChild())
      # Modify the node attribute
      elem = tree.createElement(subnode)
      if spectralBands:
        elem.setAttribute("bandNumber", "0")
        elem.setAttribute("spectralDartMode", "0")
      if isinstance(attributName, list) and isinstance(value, list):
        if isinstance(value[0], list):
          for bandNumber, val in enumerate(value):
            if spectralBands:
              elem.setAttribute("bandNumber", str(bandNumber))
            for atr, v in zip(attributName, val):
              elem.setAttribute(atr, v)
            node.appendChild(elem.cloneNode(True))
        else:
          elem = tree.createElement(subnode)
          for atr, v in zip(attributName, value):
            elem.setAttribute(atr, v)
          node.appendChild(elem)
      elif isinstance(attributName, str) and isinstance(value, str):
        elem = tree.createElement(subnode)
        elem.setAttribute(attributName, value)
        node.appendChild(elem)
      else:
        raise ValueError("Wrong parameter used: attributName and value should be either a list of string or a string")
      # Write new XML tree in fname
      transformer = TransformerFactory.newInstance().newTransformer()
      transformer.setOutputProperty(OutputKeys.INDENT, "yes")
      source = DOMSource(tree)
      result = StreamResult(File(fname))
      transformer.transform(source, result)
    else:
      import xml.etree.ElementTree as ET
      # Get whole tree from xml
      tree = ET.parse(fname)
      # Get nodeName
      #nodes = tree.findall(".//*%s" % nodeName) # This line seems to not work for root child node!! Bug?
      node = tree.findall(".//*../%s" % parent)
      # Check if we get only one node (as expected)
      if len(node) > 1:
        raise IOError("Get multiple nodes for '%s' in file '%s'" % (parent, fname))
      elif len(node) == 0:
        raise IOError("Cannot find '%s' in file '%s'" % (parent, fname))
      else:
        node = node[0]
      # Remove content of node
      node.clear()
      # Modify the node attribute
      if spectralBands:
        attrib = {"bandNumber":"0", "spectralDartMode":"0"}
      else:
        attrib = {}
      if isinstance(attributName, list) and isinstance(value, list):
        if isinstance(value[0], list):
          for bandNumber, val in enumerate(value):
            if spectralBands:
              attrib["bandNumber"] = str(bandNumber)
            for atr, v in zip(attributName, val):
              attrib[atr] = v
            node.append(ET.Element(subnode, attrib=attrib))
        else:
          for atr, v in zip(attributName, value):
            attrib[atr] = v
          node.append(ET.Element(subnode, attrib=attrib))
      elif isinstance(attributName, str) and isinstance(value, str):
        attrib[attributName] = value
        node.append(ET.Element(subnode, attrib=attrib))
      else:
        raise ValueError("Wrong parameter used: attributName and value should be both either a list of string or a string")
      # Write new XML tree in fname
      tree.write(fname)
  XMLReplaceNodeContent = staticmethod(XMLReplaceNodeContent)
  def XMLAddNode(fname, parent, treeNodes, nodesSetup):
    """ Add a node (subnode) to a given parent in the provided fname file.
    """
    if sys.platform.startswith('java'):
      from javax.xml.parsers import DocumentBuilderFactory
      from javax.xml.transform import TransformerFactory
      from javax.xml.transform import OutputKeys
      from javax.xml.transform.dom import DOMSource
      from javax.xml.transform.stream import StreamResult
      from java.io import File
      # Get whole tree
      tree = DocumentBuilderFactory.newInstance().newDocumentBuilder().parse(fname)
      # Get nodeName
      node = tree.getElementsByTagName(parent)
      # Check if we get only one node (as expected)
      if node.getLength() > 1:
        raise IOError("Get multiple nodes for '%s' in file '%s'" % (parent, fname))
      elif node.getLength() == 0:
        raise IOError("Cannot find '%s' in file '%s'" % (parent, fname))
      else:
        node = node.item(0)
      # Create all the new nodes
      nodes = {parent:node}
      for name in treeNodes:
        nodes[name] = (tree.createElement(name))
        for atr, val in zip(*[ nodesSetup[name][key] for key in nodesSetup[name].iterkeys() if key in ["attribute", "value"] ]):
          nodes[name].setAttribute(atr, val)
      # Add all created node to its parent (previous node in the list)
      for name, elem in nodes.iteritems():
        if name != parent:
          nodes[nodesSetup[name]["parent"]].appendChild(elem)
      # Write new XML tree in fname
      transformer = TransformerFactory.newInstance().newTransformer()
      transformer.setOutputProperty(OutputKeys.INDENT, "yes")
      source = DOMSource(tree)
      result = StreamResult(File(fname))
      transformer.transform(source, result)
    else:
      import xml.etree.ElementTree as ET
      # Get whole tree from xml
      tree = ET.parse(fname)
      # Get nodeName
      #nodes = tree.findall(".//*%s" % nodeName) # This line seems to not work for root child node!! Bug?
      node = tree.findall(".//*../%s" % parent)
      # Check if we get only one node (as expected)
      if len(node) > 1:
        raise IOError("Get multiple nodes for '%s' in file '%s'" % (parent, fname))
      elif len(node) == 0:
        raise IOError("Cannot find '%s' in file '%s'" % (parent, fname))
      else:
        node = node[0]
      # Create all the new nodes
      nodes = {parent:node}
      for name in treeNodes:
        attrib = {}
        for atr, val in zip(*[ nodesSetup[name][key] for key in nodesSetup[name].iterkeys() if key in ["attribute", "value"] ]):
          attrib[atr] = val
        nodes[name] = ET.Element(name, attrib)
      # Add all created node to its parent (previous node in the list)
      for name, elem in nodes.iteritems():
        if name != parent:
          nodes[nodesSetup[name]["parent"]].append(elem)
      # Write new XML tree in fname
      tree.write(fname)
  XMLAddNode = staticmethod(XMLAddNode)
  def XMLGetNodeAttributeValue(fname, nodeName, attributName):
    """ Return the value of the given attributName for the given nodeName
    """
    if sys.platform.startswith('java'):
      from javax.xml.parsers import DocumentBuilderFactory
      from org.w3c.dom import Element
      # Get whole tree
      tree = DocumentBuilderFactory.newInstance().newDocumentBuilder().parse(fname)
      # Get nodeName
      node = tree.getElementsByTagName(nodeName)
      # Check if we get only one node (as expected)
      if node.getLength() > 1:
        raise IOError("Get multiple nodes for '%s' in file '%s'" % (nodeName, fname))
      elif node.getLength() == 0:
        raise IOError("Cannot find '%s' in file '%s'" % (nodeName, fname))
      else:
        node = node.item(0)
      # Check if that node has attributName
      if node.hasAttribute(attributName):
        return node.getAttributes().getNamedItem(attributName).getNodeValue()
      else:
        raise IOError("Attribute name '%s' not found for node '%s' in file '%s'" % (attributName, nodeName, fname))
    else:
      import xml.etree.ElementTree as ET
      # Get whole tree from xml
      tree = ET.parse(fname)
      # Get nodeName
      #nodes = tree.findall(".//*%s" % nodeName) # This line seems to not work for root child node!! Bug?
      node = tree.findall(".//*../%s[@%s]" % (nodeName, attributName))
      # Check if we get only one node (as expected)
      if len(node) > 1:
        raise IOError("Get multiple nodes for '%s' in file '%s'" % (nodeName, fname))
      elif len(node) == 0:
        raise IOError("Cannot find '%s' in file '%s'" % (nodeName, fname))
      else:
        node = node[0]
      # Check if that node has an attributName
      if attributName in node.keys():
        return node.get(attributName)
      else:
        raise IOError("Attribute name '%s' not found for node '%s' in file '%s'" % (attributName, nodeName, fname))
  XMLGetNodeAttributeValue = staticmethod(XMLGetNodeAttributeValue)
  def getBandsFromGUI(sensor):
    """ Return a DART spectral bands list: ["deltaLambda", "meanLambda"] in micro meter
    In case of several bands the result should be a list of list:
    [["deltaLambda0", "meanLambda0"], ["deltaLambda1", "meanLambda1"], ["deltaLambda2", "meanLambda2"], ...]
    e.g.: [["0.02", "0.56"], ["0.02", "0.58"], ["0.02", "0.60"], ["0.02", "0.62"]]
    """

  # TODO sensor spectral band data should not be hardcoded here

    # https://github.com/netceteragroup/esa-beam/blob/master/beam-3dveglab-vlab/src/main/scenes/librat_scenes/wb.MSI.dat
    # https://sentinel.esa.int/web/sentinel/user-guides/sentinel-2-msi/resolutions/radiometric
    if VLAB.K_SENTINEL2 == sensor:
      bands = [
        ["0.02",        "0.443"],       # band  1
        ["0.065",       "0.49"],        # band  2
        ["0.035",       "0.56"],        # band  3
        ["0.03",        "0.665"],       # band  4
        ["0.015",       "0.705"],       # band  5
        ["0.015",       "0.74"],        # band  6
        ["0.02",        "0.783"],       # band  7
        ["0.115",       "0.842"],       # band  8
        ["0.02",        "0.945"],       # band  9
        ["0.03",        "1.375"],       # band 10
        ["0.09",        "1.61"],        # band 11
        ["0.18",        "2.19"],        # band 12
      ]
    # https://github.com/netceteragroup/esa-beam/blob/master/beam-3dveglab-vlab/src/main/scenes/librat_scenes/wb.OLCI.dat
    # https://sentinel.esa.int/web/sentinel/user-guides/sentinel-3-olci/resolutions/radiometric
    elif VLAB.K_SENTINEL3 == sensor:
      bands = [
        ["0.015",       "0.4"],         # band Oa1
        ["0.01",        "0.413"],       # band Oa2
        ["0.01",        "0.49"],        # band Oa4
        ["0.01",        "0.51"],        # band Oa5
        ["0.01",        "0.56"],        # band Oa6
        ["0.01",        "0.62"],        # band Oa7
        ["0.01",        "0.665"],       # band Oa8
        ["0.0075",      "0.681"],       # band Oa10
        ["0.01",        "0.709"],       # band Oa11
        ["0.0075",      "0.754"],       # band Oa12
        ["0.0025",      "0.761"],       # band Oa13
        ["0.015",       "0.779"],       # band Oa16
        ["0.02",        "0.865"],       # band Oa17
        ["0.01",        "0.885"],       # band Oa18
        ["0.01",        "0.9"],         # band Oa19
        ["0.04",        "1.02"],        # band Oa21
      ]
    # https://github.com/netceteragroup/esa-beam/blob/master/beam-3dveglab-vlab/src/main/scenes/librat_scenes/wb.MODIS.dat
    # http://oceancolor.gsfc.nasa.gov/DOCS/RSR_tables.htmlhttp://oceancolor.gsfc.nasa.gov/DOCS/RSR_tables.html
    elif VLAB.K_MODIS == sensor:
      bands = [
        ["0.047493",    "0.66"],        # Band 8  ?
        ["0.038252",    "0.84"],        # Band 12 ?
        ["0.010633",    "0.485"],       # Band 4  ?
        ["0.01975367",  "0.57"],        # band 7  ?
        ["0.023356",    "1.24"],        # band 14 ?
        ["0.027593",    "1.65"],        # band 15 ?
        ["0.053079",    "2.22"],        # band 16 ?
      ]
    # https://github.com/netceteragroup/esa-beam/blob/master/beam-3dveglab-vlab/src/main/scenes/librat_scenes/wb.MERIS.dat
    # http://earth.esa.int/pub/ESA_DOC/ENVISAT/MERIS/VT-P017-DOC-005-E-01-01_meris.faq.1_1.pdf
    elif VLAB.K_MERIS == sensor:
      bands = [
        ["0.01",        "0.415799988"], # band  1
        ["0.01",        "0.447600006"], # band  2
        ["0.01",        "0.486600006"], # band  3
        ["0.01",        "0.505700012"], # band  4
        ["0.01",        "0.557599976"], # band  5
        ["0.01",        "0.619599976"], # band  6
        ["0.01",        "0.668799988"], # band  7
        ["0.0075",      "0.679700012"], # band  8
        ["0.01",        "0.709099976"], # band  9
        ["0.0075",      "0.755000"],    # band 10
        ["0.00375",     "0.762200012"], # band 11
        ["0.015",       "0.776700012"], # band 12
        ["0.02",        "0.867000"],    # band 13
        ["0.01",        "0.885400024"], # band 14
        ["0.01",        "0.9"],         # band 15
      ]
    # https://github.com/netceteragroup/esa-beam/blob/master/beam-3dveglab-vlab/src/main/scenes/librat_scenes/wb.LANDSAT.ETM.dat
    # TODO: lambdaDeltas not found - just copied from OLI
    elif VLAB.K_LANDSAT_ETM == sensor:
      bands = [
        ["0.01598",     "0.44"],        # band 1 Blue
        ["0.05733",     "0.56"],        # band 2 Green
        ["0.03747",     "0.66"],        # band 3 Red
        ["0.02825",     "0.835"],       # band 4 NIR
        ["0.08472",     "1.65"],        # band 5 SWIR1
        ["0.18666",     "2.2"],         # band 8 SWIR2
      ]
    # https://github.com/netceteragroup/esa-beam/blob/master/beam-3dveglab-vlab/src/main/scenes/librat_scenes/wb.LANDSAT.OLI.dat
    # http://landsat.gsfc.nasa.gov/?p=5779
    elif VLAB.K_LANDSAT_OLI == sensor:
      bands = [
        ["0.01598",     "0.44"],        # band  CA
        ["0.06004",     "0.47"],        # band  Blue
        ["0.05733",     "0.56"],        # band  Green
        ["0.03747",     "0.655"],       # band  Red
        ["0.02825",     "0.865"],       # band  NIR
        ["0.08472",     "1.61"],        # band  SWIR1
        ["0.18666",     "2.2"],         # band  SWIR2
        ["0.17240",     "0.6"],         # band  Pan
        ["0.02039",     "1.37"],        # band  Cirrus
      ]
    else:
      VLAB.logger.info("getBandsFromGUI: unknown sensor=%s" % (sensor))
      bands = [[]]

    VLAB.logger.info("getBandsFromGUI: sensor=%s returning %s" % (sensor, bands))

    return bands
  getBandsFromGUI = staticmethod(getBandsFromGUI)
  class path:
    def exists(path):
      if sys.platform.startswith('java'):
        from java.io import File
        return File(path).exists()
      else:
        import os
        return os.path.exists(path)
    exists = staticmethod(exists)
    def isabs(path):
      if sys.platform.startswith('java'):
        from java.io import File
        return File(path).isAbsolute()
      else:
        import os
        return os.path.isabs(path)
    isabs = staticmethod(isabs)
    def isdir(path):
      if sys.platform.startswith('java'):
        from java.io import File
        return File(path).isDirectory()
      else:
        import os
        return os.path.isdir(path)
    isdir = staticmethod(isdir)
    def join(path, *args):
      if sys.platform.startswith('java'):
        from java.io import File
        f = File(path)
        for a in args:
          g = File(a)
          if g.isAbsolute() or len(f.getPath()) == 0:
            f = g
          else:
            f = File(f, a)
        return f.getPath()
      else:
        import os
        return os.path.join(path, *args)
    join = staticmethod(join)
    def isfile(path):
      if sys.platform.startswith('java'):
        from java.io import File
        return File(path).isfile()
      else:
        import os
        return os.path.isfile(path)
    isfile = staticmethod(isfile)
    def normcase(path):
      if sys.platform.startswith('java'):
        from java.io import File
        return File(path).getPath()
      else:
        import os
        return os.path.normcase(path)
    normcase = staticmethod(normcase)
    def normpath(path):
      if sys.platform.startswith('java'):
        from java.io import File
        return File(path).getCanonicalPath()
      else:
        import os
        return os.path.normpath(path)
    normpath = staticmethod(normpath)
    def split(path):
      if sys.platform.startswith('java'):
        from java.io import File
        f=File(path)
        d=f.getParent()
        if not d:
          if f.isAbsolute():
            d = path
          else:
            d = ""
        return (d, f.getName())
      else:
        import os
        return os.path.split(path)
    split = staticmethod(split)
  def frange(end, start=0, inc=0):
    """a jython-compatible range function with float increments"""
    import math
    if not start:
      start = end + 0.0
      end = 0.0
    else: end += 0.0
    if not inc:
      inc = 1.0
    count = int(math.ceil((start - end) / inc))
    L = [None] * count
    L[0] = end
    for i in (xrange(1,count)):
      L[i] = L[i-1] + inc
    return L
  frange = staticmethod(frange)
  def openFileIfNotExists(filename):
    """open file exclusively"""
    if sys.platform.startswith('java'):
      from java.io import File
      File(filename).getParentFile().mkdirs()
      if File(filename).createNewFile():
        return open(filename, 'w')
      else:
        return None
    else:
      import os
      try:
        # os.O_EXCL => open exclusive => acquire a lock on the file
        fd = os.open(filename, os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_TRUNC)
      except:
        return None
      fobj = os.fdopen(fd,'w')
      return fobj
  openFileIfNotExists = staticmethod(openFileIfNotExists)
  def rndInit(seed = None):
    """initialize the randon number generator"""
    if sys.platform.startswith('java'):
      from java.util import Random
      if seed == None:
        return Random()
      else:
        return Random(seed)
    else:
      import random
      random.seed(seed)
      return None
  rndInit = staticmethod(rndInit)
  def rndNextFloat(randState):
    """return the next pseudo-random floating point number in the sequence"""
    if sys.platform.startswith('java'):
      from java.util import Random
      return randState.nextFloat()
    else:
      import random
      return random.random()
  rndNextFloat = staticmethod(rndNextFloat)
  def r2d(v):
    """jython-compatible conversion of radians to degrees"""
    if sys.platform.startswith('java'):
      from java.lang import Math
      return Math.toDegrees(v)
    else:
      return math.degrees(v)
  r2d = staticmethod(r2d)
  def d2r(v):
    """jython-compatible conversion of degrees to radians"""
    if sys.platform.startswith('java'):
      from java.lang import Math
      return Math.toRadians(float(v))
    else:
      return math.radians(v)
  d2r = staticmethod(d2r)
  def mkDirPath(path):
    """create directory (including non-existing parents) for the given path"""
    if sys.platform.startswith('java'):
      from java.io import File
      if not File(path).isDirectory():
        if not File(path).mkdirs():
          raise RuntimeError('failed to mkdir %s' % path)
    else:
      import os
      try:
        os.stat(path)
      except:
        os.makedirs(path)
  mkDirPath = staticmethod(mkDirPath)
  def fPath(d,n):
    """get file path of the file defined by directory d and file name n"""
    if sys.platform.startswith('java'):
      from java.io import File
      return File(d, n).getPath()
    else:
      import os
      return os.path.join(d, n)
  fPath = staticmethod(fPath)
  def savetxt(a, b, fmt=False):
    """save text b in a text file named a"""
    fh = open(a, 'w')
    if not fmt:
      fmt = '%s'
    for row in b:
      for element in row:
        fh.write(fmt % element + ' ')
      fh.write('\n')
    fh.close()
  savetxt = staticmethod(savetxt)
  def osName():
    """return which OS we are currently running on"""
    if sys.platform.startswith('java'):
      from java.lang import System
      oname = System.getProperty('os.name')
    else:
      import os
      oname = os.name
      if not oname.endswith('x'): oname = 'Windows'
    return oname
  osName = staticmethod(osName)
  def expandEnv(instr):
    """potentially expand environment variables in the given string"""
    outstr = instr
    m = {'$HOME':'HOME','%HOMEDRIVE%':'HOMEDRIVE','%HOMEPATH%':'HOMEPATH'}
    for e in m:
      if outstr.find(e) != -1:
        if sys.platform.startswith('java'):
          from java.lang import System
          repl = System.getenv(m[e])
        else:
          import os
          repl = os.getenv(m[e])
        if repl != None:
          outstr = outstr.replace(e, repl)
    return outstr
  expandEnv = staticmethod(expandEnv)

  if sys.platform.startswith('java'):
    from java.lang import Runnable
    class Helper(Runnable):
      def __init__(self, nm, strm, fName):
        self.nm=nm; self.strm=strm; self.fp=None
        if fName != None:
          if VLAB.fileExists(fName):
            self.fp = open(fName, 'w')
          else:
            self.fp = VLAB.openFileIfNotExists(fName)
      def run(self):
        """helper class for slurping up child streams"""
        from java.io import BufferedReader
        from java.io import InputStreamReader
        line = None; br = BufferedReader(InputStreamReader(self.strm))
        line = br.readLine()
        while (line != None):
          if self.fp != None:
            self.fp.write(line + VLAB.lineSeparator())
            self.fp.flush()
          VLAB.logger.info('%s %s' %(self.nm, line.rstrip()))
          line = br.readLine()
        br.close()
        if self.fp != None:
          self.fp.close()
  else:
    def helper(nm, strm):
      """helper method for slurping up child streams"""
      for line in strm: VLAB.logger.info('%s %s' %(nm, line.rstrip()))
      if not strm.closed: strm.close()
    helper = staticmethod(helper)
  def doExec(cmdrec):
    """run the specified external program under windows or unix"""
    cmdLine = []
    osName = VLAB.osName()
    if osName.startswith('Windows'):
      cmd=cmdrec['windows']
      exe = cmd['exe']
      cmdLine = ['cmd', '/c']
      cmdstr = '"'
      # None means it is .bat command
      if exe != None:
        cmdstr += ' "' + VLAB.expandEnv(exe) + '" '
      for i in cmd['cmdline']:
        expanded = VLAB.expandEnv(i)
        if " " in expanded:
          cmdstr += ' "' + expanded + '" '
        else:
          cmdstr += ' '  + expanded + ' '
      cmdstr += '"'
      cmdLine.append(cmdstr)
    else:
      cmd=cmdrec['linux']
      exe = VLAB.expandEnv(cmd['exe'])
      cmdLine.append(exe)
      for i in cmd['cmdline']:
        cmdLine.append(VLAB.expandEnv(i))

    VLAB.logger.info('cmdLine is [%s]' % cmdLine)
    if sys.platform.startswith('java'):
      from java.lang import ProcessBuilder
      from java.lang import Thread
      from java.io import BufferedWriter
      from java.io import OutputStreamWriter
      from java.io import File
      pb = ProcessBuilder(cmdLine)
      if 'cwd' in cmd and cmd['cwd'] != None:
        pb.directory(File(VLAB.expandEnv(cmd['cwd'])))
      if 'env' in cmd and cmd['env'] != None:
        env = pb.environment()
        cmdenv = cmd['env']
        for e in cmdenv:
          env[e] = VLAB.expandEnv(cmdenv[e])
      proc = pb.start()
      stdoutfName = None
      if 'stdout' in cmd and cmd['stdout'] != None:
        stdoutfName = VLAB.expandEnv(cmd['stdout'])
      stderrfName = None
      if 'stderr' in cmd and cmd['stderr'] != None:
        stderrfName = VLAB.expandEnv(cmd['stderr'])
      outs = Thread(VLAB.Helper('out', proc.getInputStream(), stdoutfName))
      errs = Thread(VLAB.Helper('err', proc.getErrorStream(), stderrfName))
      outs.start(); errs.start()
      bw = BufferedWriter(OutputStreamWriter(proc.getOutputStream()))
      if 'stdin' in cmd and cmd['stdin'] != None:
        inFile = VLAB.expandEnv(cmd['stdin'])
        VLAB.logger.info('stdin is [%s]' % inFile)
        if 'cwd' in cmd and cmd['cwd'] != None:
          if not VLAB.fileExists(inFile):
            # try pre-pending the cwd
            inFile = VLAB.fPath(VLAB.expandEnv(cmd['cwd']), inFile)
            if not VLAB.fileExists(inFile):
              raise RuntimeError('Cannot find stdin "%s"' % cmd['cwd'])
        fp = open(inFile, 'r')
        for line in fp:
          bw.write(line)
        bw.close()
        fp.close()
      exitCode = proc.waitFor()
      outs.join(); errs.join()
    else:
      import threading, subprocess, os
      if 'cwd' in cmd and cmd['cwd'] != None:
        os.chdir(VLAB.expandEnv(cmd['cwd']))
      if 'env' in cmd and cmd['env'] != None:
        cmdenv = cmd['env']
        for e in cmdenv:
          os.putenv(e, VLAB.expandEnv(cmdenv[e]))
      if 'stdin' in cmd and cmd['stdin'] != None:
        proc = subprocess.Popen(cmdLine, stdin=open(VLAB.expandEnv(cmd['stdin']),'r'),stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      else:
        proc = subprocess.Popen(cmdLine, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      t1 = threading.Thread(target=VLAB.helper, args=('out', proc.stdout))
      t2 = threading.Thread(target=VLAB.helper, args=('err', proc.stderr))
      t1.start(); t2.start()
      exitCode = proc.wait()
      t1.join(); t2.join()
    VLAB.logger.info('exitCode=%d' % exitCode)
    return exitCode
  doExec = staticmethod(doExec)

  def valuesfromfile(path, transpose=False):
    """Returns a 2D array with the values of the csv file at 'path'.

    Keyword arguments:
    transpose -- transpose the matrix with the values

    """
    fp = open(path)
    values = [line.strip().split() for line in fp
              if not line.startswith('#')]
    fp.close()
    values = [[float(value) for value in row] for row in values]
    if transpose:
      values = zip(*values)
    return values
  valuesfromfile = staticmethod(valuesfromfile)
  def fabsa(x):
    """Return the element-wise abs() of the given array."""
    return map(lambda x : math.fabs(x), x)
  fabsa = staticmethod(fabsa)
  def cosa(arcs):
    """Return the element-wise cos() of 'arcs' array given in degrees."""
    return map(lambda x : math.cos(VLAB.d2r(x)), arcs)
  cosa = staticmethod(cosa)
  def replacerectinarray(array, replacement, xul, yul, xlr, ylr):
    """Replace the array with the specified rectangle substituted with
    replacement.
    (array[xul:xlr,yul:ylr])
     +---------------+
     |(xul, yul)     |
     |               |
     |     (xlr, ylr)|
     +---------------+
    """
    ri = 0
    for x in xrange(xul, xlr):
      array[x][yul:ylr] = replacement[ri]
      ri += 1
    return array
  replacerectinarray = staticmethod(replacerectinarray)
  def replaceinarray(haystack, predicate, replacement):
    """Return 'haystack' with 'predicate' matches replaced by 'replacement'"""
    return map(lambda item : {True: replacement, False: item}[predicate(item)],
               haystack)
  replaceinarray = staticmethod(replaceinarray)
  def sqrta(values):
    """Return the element-wise sqrt() of the given array."""
    return map(math.sqrt, values)
  sqrta = staticmethod(sqrta)
  def suba(lista, listb):
    """Subtract the values of a list from the values of another list."""
    if len(lista) != len(listb):
      raise ValueError("Arguments have to be of same length.")
    return map(operator.sub, lista, listb)
  suba = staticmethod(suba)
  def adda(lista, listb):
    """Add the values of a list to the values of another list."""
    if len(lista) != len(listb):
      raise ValueError("Arguments have to be of same length.")
    return map(operator.add, lista, listb)
  adda = staticmethod(adda)
  def diva(lista, listb):
    """Return the element-wise division of 'lista' by 'listb'."""
    if len(lista) != len(listb):
      raise ValueError("Arguments have to be of same length.")
    return map(operator.div, lista, listb)
  diva = staticmethod(diva)
  def mula(lista, listb):
    """Return the element-wise multiplication of 'lista' with 'listb'."""
    if len(lista) != len(listb):
      raise ValueError("Arguments have to be of same length.")
    return map(operator.mul, lista, listb)
  mula = staticmethod(mula)
  def powa(values, exponent):
    """Returns the element-wise exp('exponent') of the given array."""
    if isinstance(exponent, (list, tuple)):
      return map(lambda x, y : x ** y, values, exponent)
    return map(lambda x : x ** exponent, values)
  powa = staticmethod(powa)
  def treemap(fn, tree):
    """Applies `fn' to every value in `tree' which isn't a list and
    returns a list with the same shape as tree and the value of `fn'
    applied to the values in their place.

    """
    result = []
    for node in tree:
      if isinstance(node, (list, tuple)):
        result += [VLAB.treemap(fn, node)]
      else:
        result += [fn(node)]
    return result
  treemap = staticmethod(treemap)
  def makemaskeq(array, value):
    return VLAB.treemap(lambda x : x == value, array)
  makemaskeq = staticmethod(makemaskeq)
  def awhere(mask):
    """Returns the coordinates of the cells which evaluate true."""
    result = []
    if isinstance(mask, (list, tuple)):
      for i, cell in enumerate(mask):
        result += [[i] + sub for sub in VLAB.awhere(cell)
                   if isinstance(sub, (list, tuple))]
      return result
    else:
      if mask:
        return [[]]
      else:
        return []
  awhere = staticmethod(awhere)
  def aclone(tree):
    """Make a deep copy of `tree'."""
    if isinstance(tree, (list, tuple)):
      return list(map(VLAB.aclone, tree))
    return tree
  aclone = staticmethod(aclone)
  def make_chart(title, x_label, y_label, dataset):
    """Helper for creating Charts"""
    if sys.platform.startswith('java'):
      from org.jfree.chart import ChartFactory, ChartFrame, ChartUtilities
      from org.jfree.chart.axis import NumberTickUnit
      from org.jfree.chart.plot import PlotOrientation
      from org.jfree.data.xy import XYSeries, XYSeriesCollection
      chart = ChartFactory.createScatterPlot(title, x_label, y_label, dataset,
                                           PlotOrientation.VERTICAL, True,
                                           True, False)
      plot = chart.getPlot()
      domain_axis = plot.getDomainAxis()
      domain_axis.setRange(-70, 70)
      range_axis = plot.getRangeAxis()
      range_axis.setRange(0.0, 0.4)
      range_axis.setTickUnit(NumberTickUnit(0.05))
      return chart
    else:
      # TODO: re-merge original python implementation
      raise Exception("original make_chart()")
      return None
  make_chart = staticmethod(make_chart)
  def make_dataset():
    """Dataset helper for supporting chart creation"""
    if sys.platform.startswith('java'):
      from org.jfree.data.xy import XYSeriesCollection
      return XYSeriesCollection()
    else:
      # TODO: re-merge original python implementation
      raise Exception("original make_dataset()")
      return None
  make_dataset = staticmethod(make_dataset)
  def plot(dataset, x, y, label):
    """plot dataset with x and y values and the given label"""
    if sys.platform.startswith('java'):
      from org.jfree.data.xy import XYSeries
      series = XYSeries(label)
      for next_x, next_y in zip(x, y):
        series.add(float(next_x), float(next_y))
      dataset.addSeries(series)
    else:
      # TODO: re-merge original python implementation
      raise Exception("original plot()")
      return None
  plot = staticmethod(plot)
  def save_chart(chart, filename):
    """save the generated chart in the given filename"""
    if sys.platform.startswith('java'):
      from java.io import File
      from org.jfree.chart import ChartUtilities
      ChartUtilities.saveChartAsPNG(File(filename), chart, 800, 600)
    else:
      # TODO: re-merge original python implementation
      raise Exception("save_chart")
      pass
  save_chart = staticmethod(save_chart)
  def maskand(array, mask):
    return map(lambda a, b : a & b, array, mask)
  maskand = staticmethod(maskand)
  def unique(array):
    """return unique values in the given input array"""
    sortedarray = list(array)
    sortedarray.sort()
    result = []
    def addifunique(x, y):
      if x != y:
        result.append(x)
      return y
    result.append(reduce(addifunique, sortedarray))
    return result
  unique = staticmethod(unique)
  def ravel(a):
    def add(a, i):
      if not(isinstance(a, (list, tuple))):
        a = [a]
      if isinstance(i, (list, tuple)):
        return a + ravel(i)
      else:
        return a + [i]
    return reduce(add, a)
  ravel = staticmethod(ravel)
  def approx_fprime(xk, f, epsilon, *args):
    f0 = f(xk, *args)
    grad = [0. for i in xrange(len(xk))]
    ei = [0. for i in xrange(len(xk))]
    for k in xrange(len(xk)):
      ei[k] = 1.0
      d = map(lambda i : i * epsilon, ei)
      grad[k] = (f(VLAB.adda(xk, d), *args) - f0) / d[k]
      ei[k] = 0.0
    return grad
  approx_fprime = staticmethod(approx_fprime)
  def min_l_bfgs_b(f, initial_guess, args=(), bounds=None, epsilon=1e-8):
    """The `approx_grad' is not yet implemented, because it's not yet
used."""
    pnt = None
    if sys.platform.startswith('java'):
      ### no longer needed - installer resolves SOs/DLLs
      # from java.lang import System, ClassLoader
      # from java.io import File
      # libDirs = System.getProperty("beam.libDirs")
      # if libDirs == None:
      #   raise RuntimeError("beam.libDirs is not known to Java")
      #
      ### http://blog.cedarsoft.com/2010/11/setting-java-library-path-programmatically
      # libPath = System.getProperty("java.library.path")
      # libPath += File.pathSeparator + libDirs
      # System.setProperty("java.library.path", libPath)
      # syspathfield = ClassLoader.getDeclaredField("sys_paths")
      # syspathfield.setAccessible(True);
      # syspathfield.set(None, None)

      from lbfgsb import DifferentiableFunction, FunctionValues, Bound, Minimizer
      class function(DifferentiableFunction):
        def __init__(self, function, args=()):
          self.function = function
          self.args = args
        def getValues(self, x):
          f = self.function(x, *self.args)
          g = VLAB.approx_fprime(x, self.function, epsilon, *self.args)
          return FunctionValues(f, g)
      min = Minimizer()
      min.setBounds([Bound(bound[0], bound[1]) for bound in bounds])
      result = min.run(function(f, args), VLAB.ravel(initial_guess))
      pnt = result.point
    return pnt
  min_l_bfgs_b = staticmethod(min_l_bfgs_b)
  def doLibradtran(args):

    q = {
      'rpv_file':  args['rpv_file'],
      'outfile' :  args['outfile'],
      'infile'  :  args['infile'],
    }

    for k in args:
      q[k] = args[k]

    if args['scene'] == VLAB.K_LAEGERN:
      q['latitude']  = '47.481667'
      q['longitude'] = '-8.394722,17'
    elif args['scene'] == VLAB.K_THARANDT:
      q['latitude']  = '50.9676498'
      q['longitude'] = '-13.520354'

    if args['aerosol'] == VLAB.K_RURAL:
      q['aerosol'] = '1'
    elif args['aerosol'] == VLAB.K_MARITIME:
      q['aerosol'] = '2'
    elif args['aerosol'] == VLAB.K_URBAN:
      q['aerosol'] = '5'
    elif args['aerosol'] == VLAB.K_TROPOSPHERIC:
      q['aerosol'] = '6'

    # determine wavelength min/max from rpv_file
    rpv_vals = VLAB.valuesfromfile(q['rpv_file'])
    (wmin, wmax) = (99999, 0)
    for r_entry in rpv_vals:
      wavelen = float(r_entry[0])
      if wavelen < wmin:
        wmin = int(round(wavelen))
      if wavelen > wmax:
        wmax = int(round(wavelen))
    q['wavelength'] = '%d %d' % (wmin, wmax)
    VLAB.logger.info('%s: wavelength param "%s"' % (VLAB.me(), q['wavelength']))

    if VLAB.osName().startswith('Windows'):
      sfile = VLAB.expandEnv('%HOMEDRIVE%%HOMEPATH%\\.beam\\beam-vlab\\auxdata\\libRadtran_win32\\data\\solar_flux\\NewGuey2003.dat')
    else:
      sfile =  VLAB.expandEnv('$HOME/.beam/beam-vlab/auxdata/libRadtran_lin64/data/solar_flux/NewGuey2003.dat')

    if " " in sfile:
      q['solar_file'] = '"' + sfile + '"'
    else:
      q['solar_file'] = sfile

    if " " in q['rpv_file']:
      q['rpv_file'] = '"' + q['rpv_file'] + '"'

    sdata = """
source solar       %s
mol_abs_param      LOWTRAN
rte_solver         disort
rpv_file           %s
deltam             on
number_of_streams  6
zout               TOA
output_user        lambda uu
quiet
""" % (q['solar_file'], q['rpv_file'])

    if 'aerosol' in q:
      sdata += "aerosol_default\n"
      sdata += "aerosol_haze       %s\n" % (q['aerosol'])
    if 'O3' in q:
      sdata += "mol_modify         O3 %s DU\n" % (q['O3'])
    if 'CO2' in q:
      sdata += "mixing_ratio       CO2 %s\n" % (q['CO2'])
    if 'H2O' in q:
      sdata += "mixing_ratio       H2O %s\n" % (q['H2O'])
    if 'umu' in q:
      sdata += "umu                %s\n" % (q['umu'])
    if 'phi' in q:
      sdata += "phi                %s\n" % (q['phi'])
    if 'latitude' in q:
      sdata += "latitude           %s\n" % (q['latitude'])
    if 'longitude' in q:
      sdata += "longitude          %s\n" % (q['longitude'])
    if 'time' in q:
      sdata += "time               %s\n" % (q['time'])
    if 'sza' in q:
      sdata += "sza                %s\n" % (q['sza'])
    if 'phi0' in q:
      sdata += "phi0               %s\n" % (q['phi0'])
    if 'wavelength' in q:
      sdata += "wavelength         %s\n" % (q['wavelength'])

    fp = open(q['infile'], 'w')
    fp.write(sdata)
    fp.close()

    cmd = {
     'linux' : {
       'cwd'     : '$HOME/.beam/beam-vlab/auxdata/libRadtran_lin64/examples',
       'exe'     : '$HOME/.beam/beam-vlab/auxdata/libRadtran_lin64/bin/uvspec',
       'cmdline' : [],
       'stdin'   : q['infile'],
       'stdout'  : q['outfile'],
       'stderr'  : None,
       'env'     : None
     },
     'windows' : {
       'cwd'     : '%HOMEDRIVE%%HOMEPATH%\\.beam\\beam-vlab\\auxdata\\libRadtran_win32\\examples',
       'exe'     : '%HOMEDRIVE%%HOMEPATH%\\.beam\\beam-vlab\\auxdata\\libRadtran_win32\\bin\\uvspec.exe',
       'cmdline' : [],
       'stdin'   : q['infile'],
       'stdout'  : q['outfile'],
       'stderr'  : None,
       'env'     : None
    }
    }
    VLAB.logger.info('%s: spawning libradtran...' % VLAB.me())
    exitCode = VLAB.doExec(cmd)
    if exitCode != 0:
      raise Exception("uvspec failed with return code=%d" % exitCode)
  doLibradtran = staticmethod(doLibradtran)


  ###########################################################################
  #
  # Minimize_* functions...
  #
  # Nelder-Mead simplex minimization of a nonlinear (multivariate) function.
  #
  # The programming interface is via the minimize() function; see below.
  #
  # This code has been adapted from the C-coded nelmin.c which was
  # adapted from the Fortran-coded nelmin.f which was, in turn, adapted
  # from the papers
  #
  #   J.A. Nelder and R. Mead (1965)
  #   A simplex method for function minimization.
  #   Computer Journal, Volume 7, pp 308-313.
  #
  #   R. O'Neill (1971)
  #   Algorithm AS47. Function minimization using a simplex algorithm.
  #   Applied Statistics, Volume 20, pp 338-345.
  #
  # and some examples are in
  #
  #   D.M. Olsson and L.S. Nelson (1975)
  #   The Nelder-Mead Simplex procedure for function minimization.
  #   Technometrics, Volume 17 No. 1, pp 45-51.
  #
  # For a fairly recent and popular incarnation of this minimizer,
  # see the amoeba function in the famous "Numerical Recipes" text.
  #
  # P. Jacobs
  # School of Engineering, The University of Queensland
  # 07-Jan-04
  #
  # Modifications by C. Schenkel
  # Netcetera
  # 31-Oct-13
  #
  ###########################################################################
  def Minimize_create_new_point(c1, p1, c2, p2):
    """
    Create a new N-dimensional point as a weighting of points p1 and p2.
    """
    p_new = []
    for j in range(len(p1)):
      p_new.append(c1 * p1[j] + c2 * p2[j])
    return p_new
  Minimize_create_new_point = staticmethod(Minimize_create_new_point)

  def Minimize_take_a_step(smplx, Kreflect, Kextend, Kcontract):
    """
    Try to move away from the worst point in the simplex.

    The new point will be inserted into the simplex (in place).
    """
    i_low = smplx.lowest()
    i_high = smplx.highest()
    x_high = smplx.vertex_list[i_high]
    f_high = smplx.f_list[i_high]
    # Centroid of simplex excluding worst point.
    x_mid = smplx.centroid(i_high)
    f_mid = smplx.f(x_mid)
    smplx.nfe += 1

    # First, try moving away from worst point by
    # reflection through centroid
    x_refl = VLAB.Minimize_create_new_point(1.0+Kreflect, x_mid, -Kreflect, x_high)
    f_refl = smplx.f(x_refl)
    smplx.nfe += 1
    if f_refl < f_mid:
      # The reflection through the centroid is good,
      # try to extend in the same direction.
      x_ext = VLAB.Minimize_create_new_point(Kextend, x_refl, 1.0-Kextend, x_mid)
      f_ext = smplx.f(x_ext)
      smplx.nfe += 1
      if f_ext < f_refl:
        # Keep the extension because it's best.
        smplx.replace_vertex(i_high, x_ext, f_ext)
      else:
        # Settle for the original reflection.
        smplx.replace_vertex(i_high, x_refl, f_refl)
    else:
      # The reflection is not going in the right direction, it seems.
      # See how many vertices are better than the reflected point.
      count = 0
      for i in range(smplx.N+1):
        if smplx.f_list[i] > f_refl: count += 1
      if count <= 1:
        # Not too many points are higher than the original reflection.
        # Try a contraction on the reflection-side of the centroid.
        x_con = VLAB.Minimize_create_new_point(1.0-Kcontract, x_mid, Kcontract, x_high)
        f_con = smplx.f(x_con)
        smplx.nfe += 1
        if f_con < f_high:
          # At least we haven't gone uphill; accept.
          smplx.replace_vertex(i_high, x_con, f_con)
        else:
          # We have not been successful in taking a single step.
          # Contract the simplex about the current lowest point.
          smplx.contract_about_one_point(i_low)
      else:
        # Retain the original reflection because there are many
        # vertices with higher values of the objective function.
        smplx.replace_vertex(i_high, x_refl, f_refl)
    return
  Minimize_take_a_step = staticmethod(Minimize_take_a_step)

  def Minimize_minimize(f, x, dx=None, tol=1.0e-6,
         maxfe=300, n_check=20, delta=0.001,
         Kreflect=1.0, Kextend=2.0, Kcontract=0.5, args=()):
    """
    Locate a minimum of the objective function, f.

    Input:
    f   : user-specified function f(x)
    x   : list of N coordinates
    args  : Extra arguments passed to f, i.e. ``f(x, *args)''.
    dx    : list of N increments to apply to x when forming
          the initial simplex.  Their magnitudes determine the size
          and shape of the initial simplex.
    tol   : the terminating limit for the standard-deviation
          of the simplex function values.
    maxfe : maximum number of function evaluations that we will allow
    n_check : number of steps between convergence checks
    delta : magnitude of the perturbations for checking a local minimum
          and for the scale reduction when restarting
    Kreflect, Kextend, Kcontract: coefficients for locating the new vertex

    Output:
    Returns a tuple consisting of
    [0] a list of coordinates for the best x location,
      corresponding to min(f(x)),
    [1] the function value at that point,
    [2] a flag to indicate if convergence was achieved
    [3] the number of function evaluations and
    [4] the number of restarts (with scale reduction)
    """
    converged = 0
    N = len(x)
    if dx == None:
      dx = [0.1] * N
    smplx = Minimize_NMSimplex(x, dx, f, args)

    while (not converged) and (smplx.nfe < maxfe):
      # Take some steps and then check for convergence.
      for i in range(n_check):
        VLAB.Minimize_take_a_step(smplx, Kreflect, Kextend, Kcontract)
      # Pick out the current best vertex.
      i_best = smplx.lowest()
      x_best = list(smplx.get_vertex(i_best))
      f_best = smplx.f_list[i_best]
      # Check the scatter of vertex values to see if we are
      # close enough to call it quits.
      mean, stddev = smplx.f_statistics()
      if stddev < tol:
        # All of the points are close together but we need to
        # test more carefully.
        converged = smplx.test_for_minimum(i_best, delta)
        if not converged:
          # The function evaluations are all very close together
          # but we are not at a true minimum; rescale the simplex.
          smplx.rescale(delta)

    return x_best, f_best, converged, smplx.nfe, smplx.nrestarts
  Minimize_minimize = staticmethod(Minimize_minimize)

  #
  # from here to "VLAB end" is used only for testing
  #

  def fakebye(self, event):
    """fake beam callback for existing the program"""
    me=self.__class__.__name__ +'::'+VLAB.me()
    VLAB.logger.info('%s: exiting' % me)
    sys.exit()

  def fakeDoProcessing(self, params):
    """fake beam helper for driving processing in test mode"""
    me=self.__class__.__name__ +'::'+VLAB.me()
    VLAB.logger.info('%s: starting' % me)

    VLAB.logger.info('params: %s' % params)
    if params[VLAB.P_RTProcessor] == VLAB.K_DART:
      rtProcessor = DART()
    elif params[VLAB.P_RTProcessor] == VLAB.K_LIBRAT:
      rtProcessor = LIBRAT()
    elif params[VLAB.P_RTProcessor] == VLAB.K_DUMMY:
      rtProcessor = DUMMY()
    else:
      raise RuntimeError('unknown processor: <%s>' % params[VLAB.P_RTProcessor])
    rtProcessor.doProcessing(None, params)
    VLAB.logger.info('%s : %s' % (me, 'finished'))

  def fakerun(self, event):
    """fake beam callback for running a processor"""
    me=self.__class__.__name__ +'::'+VLAB.me()
    VLAB.logger.info('%s: starting' % me)
    params = {}
    for i in self.plst:
      if type(self.vmap[i]) == str:
         params[i] = self.cmap[i].text
      elif type(self.vmap[i]) == tuple:
         lst = self.vmap[i]
         params[i] = lst[self.cmap[i].selectedIndex]
    self.fakeDoProcessing(params)

  def fakebeam(self):
    """fake beam Swing GUI"""
    me=self.__class__.__name__ +'::'+VLAB.me()
    VLAB.logger.info('%s: starting' % me)

    from javax import swing
    from java  import awt

    v = 5; h = 10; self.window = swing.JFrame(VLAB.PROCESSOR_NAME)
    self.window.windowClosing = self.fakebye
    self.window.contentPane.layout = awt.BorderLayout()
    tabbedPane = swing.JTabbedPane()

    self.window.contentPane.add("Center", tabbedPane)
    for tabGroups in VLAB.model:
      for tabName in tabGroups:
        tab = swing.JPanel()
        tab.layout = swing.BoxLayout(tab, swing.BoxLayout.PAGE_AXIS)
        tabbedPane.addTab(tabName, tab)
        for group in tabGroups[tabName]:
          tab.add(swing.JLabel(''))
          p = swing.JPanel()
          p.layout = awt.GridLayout(0, 4);
          p.layout.vgap = v;p.layout.hgap = h
          for groupName in group:
            p.border = swing.BorderFactory.createTitledBorder(groupName)
            for groupTuple in group[groupName]:
              if len(groupTuple) == 4:
                (lbl, nm, typ, vals) = groupTuple

                p.add(swing.JLabel(lbl+':', swing.SwingConstants.RIGHT))
                self.vmap[nm] = vals
                if type(vals) == tuple:
                  self.cmap[nm] = swing.JComboBox(self.vmap[nm])
                else:
                  if type(typ) == tuple:
                    exec('self.cmap[nm] = swing.'+typ[0]+'(self.vmap[nm])')
                    self.cmap[nm].setEditable(typ[1])
                  else:
                    exec('self.cmap[nm] = swing.'+typ+'(self.vmap[nm])')
                self.plst.append(nm)
                p.add(self.cmap[nm])
              else:
                p.add(swing.JLabel(""))
                p.add(swing.JLabel(""))
          tab.add(p)
        # hack
        for i in range(50):
          tab.add(swing.Box.createVerticalGlue())
        tab.add(swing.JLabel(''))
        p = swing.JPanel()
        p.layout = awt.GridLayout(0, 8)
        p.layout.hgap = 4
        for i in range(1,5):
          p.add(swing.JLabel(""))
        p.add(swing.JButton("Run",   actionPerformed=self.fakerun))
        p.add(swing.JButton("Close", actionPerformed=self.fakebye))
        p.add(swing.JButton("Help"))
        tab.add(p)
    self.window.pack(); self.window.show()

  # TESTS
  def selftests(self):
    """run a pre-defined set of tests"""
    me=self.__class__.__name__ +'::'+VLAB.me()
    VLAB.logger.info('%s: starting' % me)

    # scenario 1
    params = {
      VLAB.P_3dScene             : 'RAMI',
      VLAB.P_AtmosphereCO2       : '1.6',
      VLAB.P_ViewingAzimuth      : '0.0',
      VLAB.P_AtmosphereWater     : '0.0',
      VLAB.P_OutputPrefix        : 'RAMI_',
      VLAB.P_ViewingZenith       : '20.0',
      VLAB.P_AtmosphereAerosol   : 'Rural',
      VLAB.P_DHP_Zenith          : '20.0',
      VLAB.P_SceneYW             : '100',
      VLAB.P_DHP_3dScene         : 'RAMI',
      VLAB.P_Bands               : '1, 2, 3, 4, 5, 6, 7, 8, 9, 10',
      VLAB.P_OutputDirectory     : '',
      VLAB.P_AtmosphereOzone     : '300',
      VLAB.P_SceneLocFile        : '',
      VLAB.P_SceneYC             : '100',
      VLAB.P_DHP_OutputDirectory : '',
      VLAB.P_DHP_OutputPrefix    : 'RAMI00_',
      VLAB.P_RTProcessor         : VLAB.K_DUMMY,
      VLAB.P_SceneXW             : '50',
      VLAB.P_IlluminationAzimuth : '0.0',
      VLAB.P_Sensor              : 'MSI (Sentinel 2)',
      VLAB.P_AsciiFile           : 'Yes',
      VLAB.P_ImageFile           : 'Yes',
      VLAB.P_SceneXC             : '-50',
      VLAB.P_DHP_Y               : '0',
      VLAB.P_DHP_X               : '0',
      VLAB.P_DHP_ImageFile       : 'Yes',
      VLAB.P_DHP_AsciiFile       : 'Yes',
      VLAB.P_DHP_Resolution      : '100x100',
      VLAB.P_DHP_Azimuth         : '0.0',
      VLAB.P_IlluminationZenith  : '20.0',
      VLAB.P_DHP_RTProcessor     : VLAB.K_DUMMY,
      VLAB.P_DHP_Height          : '0',
      VLAB.P_DHP_Orientation     : '0',
      VLAB.P_ScenePixel          : '8'
    }
    self.fakeDoProcessing(params)

    # scenario 2
    params[VLAB.P_RTProcessor] = VLAB.K_LIBRAT
    self.fakeDoProcessing(params)

    # scenario 3
    params[VLAB.P_RTProcessor] = VLAB.K_DART
    self.fakeDoProcessing(params)

#### VLAB end ################################################################

class Minimize_NMSimplex:
  """
  Stores the (nonlinear) simplex as a list of lists.

  In an N-dimensional problem, each vertex is a list of N coordinates
  and the simplex consists of N+1 vertices.
  """
  def __init__(self, x, dx, f, args):
    """
    Initialize the simplex.

    Set up the vertices about the user-specified vertex, x,
    and the set of step-sizes dx.
    f is a user-specified objective function f(x).
    """
    self.N = len(x)
    self.vertex_list = []
    self.f_list = []
    self.dx = list(dx)
    self.f = lambda x : f(x, *args)
    self.nfe = 0
    self.nrestarts = 0
    for i in range(self.N + 1):
      p = list(x)
      if i >= 1: p[i-1] += dx[i-1]
      self.vertex_list.append(p)
      self.f_list.append(f(p, *args))
      self.nfe += 1

  def rescale(self, ratio):
    """
    Pick out the current minimum and rebuild the simplex about that point.
    """
    i_min = self.lowest()
    for i in range(self.N):
      self.dx[i] *= ratio
    x = self.get_vertex(i_min)
    self.vertex_list = []
    self.f_list = []
    for i in range(self.N + 1):
      p = list(x)
      if i >= 1: p[i-1] += self.dx[i-1]
      self.vertex_list.append(p)
      self.f_list.append(self.f(p))
      self.nfe += 1
    self.nrestarts += 1
    return

  def get_vertex(self, i):
    return list(self.vertex_list[i])

  def replace_vertex(self, i, x, fvalue):
    self.vertex_list[i] = list(x)
    self.f_list[i] = fvalue
    return

  def lowest(self, exclude=-1):
    """
    Returns the index of the lowest vertex, excluding the one specified.
    """
    if exclude == 0:
      indx = 1
    else:
      indx = 0
    lowest_f_value = self.f_list[indx]
    for i in range(self.N + 1):
      if i == exclude: continue
      if self.f_list[i] < lowest_f_value:
        lowest_f_value = self.f_list[i]
        indx = i
    return indx

  def highest(self, exclude=-1):
    """
    Returns the index of the highest vertex, excluding the one specified.
    """
    if exclude == 0:
      indx = 1
    else:
      indx = 0
    highest_f_value = self.f_list[indx]
    for i in range(self.N + 1):
      if i == exclude: continue
      if self.f_list[i] > highest_f_value:
        highest_f_value = self.f_list[i]
        indx = i
    return indx

  def f_statistics(self):
    """
    Returns mean and standard deviation of the vertex fn values.
    """
    sum = 0.0
    for i in range(self.N + 1):
      sum += self.f_list[i]
    mean = sum / (self.N + 1)
    sum = 0.0
    for i in range(self.N +1):
      diff = self.f_list[i] - mean
      sum += diff * diff
    std_dev = math.sqrt(sum / self.N)
    return mean, std_dev

  def centroid(self, exclude=-1):
    """
    Returns the centroid of all vertices excluding the one specified.
    """
    xmid = [0.0]*self.N
    for i in range(self.N + 1):
      if i == exclude: continue
      for j in range(self.N):
        xmid[j] += self.vertex_list[i][j]
    for j in range(self.N):
      xmid[j] /= self.N
    return xmid

  def contract_about_one_point(self, i_con):
    """
    Contract the simplex about the vertex i_con.
    """
    p_con = self.vertex_list[i_con]
    for i in range(self.N + 1):
      if i == i_con: continue
      p = self.vertex_list[i]
      for j in range(self.N):
        p[j] = 0.5 * (p[j] + p_con[j])
      self.f_list[i] = self.f(p)
      self.nfe += 1
    return

  def test_for_minimum(self, i_min, delta):
    """
    Perturb the minimum vertex and check that it is a local minimum.
    """
    is_minimum = 1  # Assume it is true and test for failure.
    f_min = self.f_list[i_min]
    for j in range(self.N):
      # Check either side of the minimum, perturbing one
      # coordinate at a time.
      p = self.get_vertex(i_min)
      p[j] += self.dx[j] * delta
      f_p = self.f(p)
      self.nfe += 1
      if f_p < f_min:
        is_minimum = 0
        break
      p[j] -= self.dx[j] * delta * 2
      f_p = self.f(p)
      self.nfe += 1
      if f_p < f_min:
        is_minimum = 0
        break
    return is_minimum

#
# end Minimize_NMSimplex
#

#### DUMMY start #############################################################
class DUMMY:
  if VLAB.osName().startswith('Windows'):
    SDIR=VLAB.expandEnv('%HOMEDRIVE%%HOMEPATH%/.beam/beam-vlab/auxdata/dummy_win32')
  else:
    SDIR=VLAB.expandEnv('$HOME/.beam/beam-vlab/auxdata/dummy_lin64')

  """A dummy processor for testing the VLAB plugin """
  def __init__(self):
    me=self.__class__.__name__ +'::'+VLAB.me()
    VLAB.logger.info('%s: constructor completed...' % me)
  def doProcessing(self, pm, args):
    """do processing for DUMMY processor"""
    me=self.__class__.__name__ +'::'+VLAB.me()

    # defaults
    q = {
      'rpvfile'    : 'angles.rpv.2.dat',
    }

    # overwrite defaults
    for a in args:
      q[a] = args[a]

    if (pm != None):
      pm.beginTask("Computing BRF...", 10)
    # ensure at least 1 second to ensure progress popup feedback
    time.sleep(1)

    # dummy processor
    VLAB.logger.info('%s: doExec() on %s' % (me, args))
    cmd = {
    'linux' : {
      'cwd'     : '$HOME/.beam/beam-vlab/auxdata/dummy_lin64/',
      'exe'     : '$HOME/.beam/beam-vlab/auxdata/dummy_lin64/dummy',
      'cmdline' : [ '-e', '1', '-r', '3' ],
      'stdin'   : None,
      'stdout'  : None,
      'stderr'  : None,
      'env'     : None
    },
    'windows' : {
      'cwd'     : '%HOMEDRIVE%%HOMEPATH%/.beam/beam-vlab/auxdata/dummy_win32',
      'exe'     : '%HOMEDRIVE%%HOMEPATH%/.beam/beam-vlab/auxdata/dummy_win32//dummy.exe',
      'cmdline' : [ '-e', '1', '-r', '3' ],
      'stdin'   : None,
      'stdout'  : None,
      'stderr'  : None,
      'env'     : None
    }
    }
    VLAB.doExec(cmd)

    if (pm != None):
      pm.beginTask("Plotting...", 10)
    time.sleep(1)
    # create a dummy chart
    dataset = VLAB.make_dataset()
    VLAB.plot(dataset, [20,  30, 60], [0.1,  0.2, 0.3],  'original')
    VLAB.plot(dataset, [-60, -30, 0], [0.05, 0.1, 0.15], 'inverted')
    chart = VLAB.make_chart('', 'Viewing Zenith (deg)', u"\u03A1", dataset)
    VLAB.save_chart(chart, "%s/%s" % (DUMMY.SDIR, 'vlab_chart.png'))

    if (pm != None):
      pm.beginTask("Inverting...", 10)
    time.sleep(1)
    VLAB.logger.info("inverting...");

    from lbfgsb import LBFGSBException, DifferentiableFunction, FunctionValues, Minimizer, Bound, IterationFinishedListener

    class VLabFun(DifferentiableFunction):
      def getValues(self, points):
        p = points[0]
        VLAB.logger.info("Calculating function for x=%s" % (p))
        return FunctionValues(math.pow(p+4, 2), [2*(p+4)])

    class VLabListener(IterationFinishedListener):
      ii = 0
      def iterationFinished(self, points, fVal, gradients):
        VLAB.logger.info("[%d] x=%f, v=%f, g=%f" % (self.ii, points[0], fVal, gradients[0]))
        self.ii = self.ii + 1
        return True

    # make it a subclass of lbfgsb
    class lbfgsb:
      class VLabDummyRun:
        def main(self,args):
          try:
            fun = VLabFun()
            alg = Minimizer()
            alg.setIterationFinishedListener(VLabListener())
            alg.setBounds([Bound(float(10), None)])
            result = alg.run(fun, [float(40)])
            VLAB.logger.info('The final result: %s' % (result))
          except LBFGSBException, e:
            VLAB.logger.info(e)

    run = lbfgsb.VLabDummyRun()
    run.main(sys.argv)

    VLAB.logger.info("writing rpv inputfile");
    # create rpv input file for radtran
    fp = open("%s/%s" % (DUMMY.SDIR, 'rpv_file.in'), 'w')
    for wb in [443, 490, 560, 665, 705, 740, 783, 842, 945, 1375, 1610, 2190]:
      fp.write("%s.0 %s %s %s\n" % (wb,"0.00000000","1.17285487","0.17957034"))
    fp.close()

    # arguments for doLibradtran
    r = {
      'CO2'      : q[VLAB.P_AtmosphereCO2],
      'H2O'      : q[VLAB.P_AtmosphereWater],
      'O3'       : q[VLAB.P_AtmosphereOzone],
      'scene'    : q[VLAB.P_3dScene],
      'aerosol'  : q[VLAB.P_AtmosphereAerosol],
      'sensor'   : q[VLAB.P_Sensor],
      'rpv_file' : '%s/%s' % (DUMMY.SDIR, "rpv_file.in"),
      'infile'   : '%s/%s' % (DUMMY.SDIR, 'UVSPEC-in.txt'),
      'outfile'  : '%s/%s' % (DUMMY.SDIR, 'UVSPEC-out.txt'),
    }
    #
    # TODO: loop over something to produce umu, phi ,phi0, sza, etc.
    #
    if (pm != None):
      pm.beginTask("Running libradtran...", 10)
    VLAB.logger.info("running Radtran");
    VLAB.doLibradtran(r)
    VLAB.logger.info('%s: finished computing...' % me)

    # Copy to results directory
    if (pm != None):
      pm.beginTask("Copying results...", 10)
    resdir = VLAB.fPath(DUMMY.SDIR, "../results/dummy/%s" % q[VLAB.P_OutputDirectory])
    VLAB.mkDirPath(resdir)
    VLAB.logger.info('%s: copy result %s -> %s' % (me, DUMMY.SDIR, resdir))
    VLAB.copyDir(DUMMY.SDIR, resdir)
    VLAB.logger.info('%s: Done...' % me)

#### DUMMY end ###############################################################

#### DART start ##############################################################

##############################################################################
#
# Dart_* integration routines
#
# Authors: Nicolas Lauret, Fabian Schneider
#
# converted to "BEAM-limited jython" by Jason Brazile
#
#==============================================================================
#title            :Dart_DARTDao.py
#description      :This script can be used to recover DART images and spectral bands
#coding       :utf-8
#author           :Nicolas Lauret, (Fabian Schneider)
#date             :20130328
#version          :1.0
#usage            :see Dart_DartImages.py
#==============================================================================

def Dart_enum(**enums):
  return type('Enum', (), enums)

Dart_ProjectionPlane = Dart_enum(SENSOR_PLANE=0, ORTHOPROJECTION=1, BOA_PLANE=2)
Dart_DataUnit = Dart_enum(BRF_TAPP=0, RADIANCE=1)
Dart_DataLevel = Dart_enum(BOA=0, SENSOR=1, TOA=2, ATMOSPHERE_ONLY=3)
Dart_SpectralBandMode = Dart_enum(VISIBLE=0, VISIBLE_AND_THERMAL=1, THERMAL=2)

class Dart_DARTEnv :
  simulationsDirectory = 'simulations'

  inputDirectory = 'input'
  outputDirectory = 'output'
  sequenceDirectory = 'sequence'

  libPhaseDirectory = 'lib_phase'
  bandRootDirectory = 'BAND'

  brfDirectory = 'BRF'
  tappDirectory = 'Tapp'
  radianceDirectory = 'Radiance'

  toaDirectory = 'TOA'
  radiativeBudgetDirectory = 'RADIATIVE_BUDGET'

  iterRootDirectory = 'ITER'
  couplDirectory = 'COUPL'
  sensorDirectory = 'SENSOR'

  #imageDirectoy = VLAB.path.join('IMAGES_DART', 'Non_Projected_Image')
  imageDirectoy = 'IMAGES_DART'
  orthoProjectedImageDirectory = 'IMAGE_PROJETEE'
  nonProjectedImageDirectory = 'Non_Projected_Image'

  brfFile = 'brf'
  radianceFile = 'radiance'
  radianceAtmoFile = 'AtmosphereRadiance'
  tappFile = 'tapp'
  radiativeBudgetFile = 'RadiativeBudget'

  propertiesFile = 'simulation.properties.txt'

# Class SpectralBand
class Dart_SpectralBand:
  def __init__(self) :
    self.index = 0
    self.lambdaMin = 0.
    self.lambdaMax = 0.
    self.mode = Dart_SpectralBandMode.VISIBLE

  def __str__(self):
    return 'Dart_SpectralBand(' + str(self.index) + ': [' + str(self.lambdaMin) + '; ' + str(self.lambdaMax) + ']; ' + str(self.mode) + ')'

  def getCentralWaveLength(self):
    return (self.lambdaMax + self.lambdaMin) / 2.

  def getBandWidth(self):
    return (self.lambdaMax - self.lambdaMin)

# Class Direction
class Dart_Direction :
  def __init__(self, theta, phi, solidAngle = 1, angularSector = 1, index = -1) :
    self.theta = theta
    self.phi = phi
    self.solidAngle = solidAngle
    self.angularSector = angularSector
    self.index = index

  def __str__(self):
    return 'Dart_Direction(' + str(self.theta) + ', ' + str(self.phi) + ')'

  def equal(self, dir2) :
    return abs(self.theta - dir2.theta) < 0.001 and abs(self.phi - dir2.phi) < 0.001

# Class BRF, Tapp, Radiance, per direction
class Dart_BRF :
  def __init__(self) :
    self.valeursParDirections = []

  def __str__(self):
    string = '<BDAverage'
    for (direction, moyenne) in self.valeursParDirections :
      string += '\n' + str(direction) + ' : ' + str(moyenne)
    string += '>'
    return string

  def addValeurDansDirection (self, direction, valeur) :
    self.valeursParDirections.append((direction, valeur))

  def getValueForDirection(self, directionRecherchee) :
    for (directionCourante, valeurCourante) in self.valeursParDirections :
      if (directionCourante.equal(directionRecherchee)) :
        return valeurCourante

  def getValue(self, indiceDirection) :
    return self.valeursParDirections[indiceDirection]

# Classe Images par direction
# FIXME Is this class still needed?
class Dart_Images :
  def __init__(self) :
    self.matrice2DparDirections = []

  def addMatriceDansDirection (self, direction, matrice) :
    self.matrice2DparDirections.append((direction, matrice))

  def getMatrice2D(self, directionRecherchee) :
    for (directionCourante, matriceCourante) in self.matrice2DparDirections :
      if (directionCourante.equal(directionRecherchee)) :
        return matriceCourante

# Classe Bilan Radiatif par type
# FIXME Is this class still needed?
class Dart_BilanRadiatif :
  def __init__(self) :
    self.matriceParType = []

  def getTypeBilan(self) :
    typeBilans = []
    for (typeBilanCourant, matriceCourante) in self.matriceParType :
      typeBilans.append(typeBilanCourant)
    return typeBilans

  def contientTypeBilan(self, typeBilan) :
    for (typeBilanCourant, matriceCourante) in self.matriceParType :
      if typeBilanCourant == typeBilan :
        return True
    return False

def Dart_getModeFromString(modeString):
  if modeString == 'T':
    return Dart_SpectralBandMode.THERMAL
  elif modeString == 'R+T':
    return Dart_SpectralBandMode.VISIBLE_AND_THERMAL
  else :
    return Dart_SpectralBandMode.VISIBLE

def Dart_getNumMaxIteration(path) :
  dirList = [f for f in VLAB.listdir(path) if (f[0] != '.') and (VLAB.path.isdir(VLAB.path.join(path, f))) and f.startswith(Dart_DARTEnv.iterRootDirectory) and f != Dart_DARTEnv.iterRootDirectory + 'X']

  maxIter = -1
  for rep in dirList :
    numIter = int(rep.split(Dart_DARTEnv.iterRootDirectory)[1])
  if numIter > maxIter :
    maxIter = numIter
  return maxIter

def Dart_readProperties(propertyPath):
  # propFile= file(propertyPath, "rU" )
  propFile= file(propertyPath, "r" )
  propDict= dict()
  for propLine in propFile:
    propDef= propLine.strip()
    if len(propDef) == 0:
      continue
    if propDef[0] in ( '!', '#' ):
      continue
    punctuation= [ propDef.find(c) for c in ':= ' ] + [ len(propDef) ]
    found= min( [ pos for pos in punctuation if pos != -1 ] )
    name= propDef[:found].rstrip()
    value= propDef[found:].lstrip(":= ").rstrip()
    propDict[name]= value
  propFile.close()
  return propDict;

def Dart_readPropertiesFromFile(stringFile):
  properties = StringIO.StringIO(stringFile)
  propertiesLines = properties.readlines()
  propertiesDico = {}
  for line in propertiesLines:
    prop,valeur = line.rstrip("\n\r\t").split(':')[0],line.rstrip("\n\r\t").split(':')[1]
    propertiesDico[prop] = valeur
  return propertiesDico

class Dart_DARTSimulation :
  def __init__(self, name, rootSimulations) :
    self.name = name
    self.rootSimulationsDirectory = rootSimulations

  def __str__(self):
    return self.name

  def getAbsolutePath(self) :
    return VLAB.path.join(self.rootSimulationsDirectory.getAbsolutePath(), self.name)

  def isValid(self) :
    if self.name != '' and VLAB.path.exists(self.getAbsolutePath()) :
      dirList=[f for f in VLAB.listdir(self.getAbsolutePath()) if (f[0] != '.') and (VLAB.path.isdir(VLAB.path.join(self.getAbsolutePath(), f)))]
      for directory in dirList:
        # On test si le dossier contient des dossiers output, input et/ou sequence
        # On relance la methode recursivement sur les eventuels autres dossiers (hors input, output et sequence)
        if (directory == Dart_DARTEnv.inputDirectory) or (directory == Dart_DARTEnv.outputDirectory) or (directory == Dart_DARTEnv.sequenceDirectory) :
          return True
    return False

  def getProperties(self):
    return Dart_readProperties(VLAB.path.join(self.getAbsolutePath(), Dart_DARTEnv.outputDirectory, Dart_DARTEnv.propertiesFile))

  def getSpectralBands(self):
    properties = self.getProperties()
    nbSpectralBand = int(properties['phase.nbSpectralBands'])
    bandes = []
    for numBand in range(nbSpectralBand):
      bande = Dart_SpectralBand()
      bande.index = numBand
      bande.lambdaMin = float(properties['dart.band' + str(numBand) + '.lambdaMin'])
      bande.lambdaMax = float(properties['dart.band' + str(numBand) + '.lambdaMax'])
      bande.mode = Dart_getModeFromString(properties['dart.band' + str(numBand) + '.mode'])
      bandes.append(bande)
    return bandes

  def getSceneGeolocation(self) :
    properties = self.getProperties()
    return (float(properties['dart.maket.latitude']), float(properties['dart.maket.longitude']))

  def getDiscretizedDirection(self):
    properties = self.getProperties()
    nbDD = int(properties['direction.numberOfDirections'])
    discretizedDirections = []
    for i in range(nbDD) :
      discretizedDirections.append(Dart_Direction(float(properties['direction.direction' + str(i) +'.thetaCenter']), float(properties['direction.direction' + str(i) +'.phiCenter']), solidAngle = float(properties['direction.direction' + str(i) +'.omega']), angularSector = int(properties['direction.direction' + str(i) +'.angularSector']), index = i))
    return discretizedDirections

  def getUserDirections(self) :
    properties = self.getProperties()
    nbUD = int(properties['direction.nbOfAdditionalSpots'])
    userDirections = []
    for i in range(nbUD) :
      additionalSpotIndex = int(properties['direction.additionalSpot' + str(i) + '.directionIndex'])
      userDirections.append(Dart_Direction(float(properties['direction.direction' + str(additionalSpotIndex) +'.thetaCenter']), float(properties['direction.direction' + str(additionalSpotIndex) +'.phiCenter']), index = additionalSpotIndex))
    return userDirections

  def listNomsSequences(self) :
    sequencePath = VLAB.path.join(self.getAbsolutePath(), Dart_DARTEnv.sequenceDirectory)
    listNom = []
    if (VLAB.path.exists(sequencePath)) :
      dirList=[f for f in VLAB.listdir(sequencePath) if (f[0] != '.') and (VLAB.path.isdir(VLAB.path.join(sequencePath, f)))]
      for sequence in dirList :
        nomSequence = sequence.rpartition('_')[0]
        if (not nomSequence in listNom) :
          listNom.append(nomSequence)
    listNom.sort()
    return listNom

  def listSequences(self, nom) :
    sequencePath = VLAB.path.join(self.getAbsolutePath(), Dart_DARTEnv.sequenceDirectory)
    listSequence = [f for f in VLAB.listdir(sequencePath) if (f[0] != '.') and (VLAB.path.isdir(VLAB.path.join(sequencePath, f))) and f.startswith(nom + '_')]

    listSequence.sort(lambda a, b: cmp(int(a[len(nom)+1:]),int(b[len(nom)+1:])))
    listSimuSequence = [Dart_DARTSimulation(VLAB.path.join(self.name, Dart_DARTEnv.sequenceDirectory, s), self.rootSimulationsDirectory) for s in listSequence]
    return listSimuSequence

  def getSequence(self, nomSequence, numeroSequence) :
    return Dart_DARTSimulation(VLAB.path.join(self.name, Dart_DARTEnv.sequenceDirectory, nomSequence + '_' + str(numeroSequence)), self.rootSimulationsDirectory);

  def getSubdirectory(self, spectralBand = 0, dataType = Dart_DataUnit.BRF_TAPP, level = Dart_DataLevel.BOA, iteration = 'last') :
    simulationPath = self.getAbsolutePath()
    bandPath = VLAB.path.join(simulationPath, Dart_DARTEnv.outputDirectory, Dart_DARTEnv.bandRootDirectory + str(spectralBand))
    brfPath = ''
    if dataType == Dart_DataUnit.RADIANCE :
      brfPath = VLAB.path.join(bandPath, Dart_DARTEnv.radianceDirectory)
      if (level == Dart_DataLevel.TOA or level == Dart_DataLevel.ATMOSPHERE_ONLY) :
        brfPath = VLAB.path.join(brfPath, Dart_DARTEnv.toaDirectory) # Radiance/TOA
      elif (level == Dart_DataLevel.SENSOR) :
        brfPath = VLAB.path.join(brfPath, Dart_DARTEnv.sensorDirectory) # Radiance/SENSOR
      elif (not iteration == 'last') :
        brfPath = VLAB.path.join(brfPath, iteration) # Radiance/ITER...
      else :
        # Recherche du dossier COUPL
        tmpPath = VLAB.path.join(brfPath, Dart_DARTEnv.couplDirectory) # Radiance/COUPL
        if (not VLAB.path.exists(tmpPath)) :
        # Recherche du dossier ITERX
          tmpPath = VLAB.path.join(brfPath, Dart_DARTEnv.iterRootDirectory + 'X') # Radiance/ITERX
          if (not VLAB.path.exists(tmpPath)) :
            # Recherche du dossier ITER de plus fort nombre
            tmpPath = VLAB.path.join(brfPath, Dart_DARTEnv.iterRootDirectory + str(Dart_getNumMaxIteration(brfPath)))
        brfPath = tmpPath;
    else :
      if (level == Dart_DataLevel.BOA) :
        # Test de la presence d'un dossier brf, sinon tapp
        brfPath = VLAB.path.join(bandPath, Dart_DARTEnv.brfDirectory)
        if (not VLAB.path.exists(brfPath)) :
          # on essaie le dossier tapp
          brfPath = VLAB.path.join(bandPath, Dart_DARTEnv.tappDirectory)
        if (not iteration == 'last') :
          brfPath = VLAB.path.join(brfPath, iteration) # BRF_TAPP/ITER...
        else :
          tmpPath = VLAB.path.join(brfPath, Dart_DARTEnv.couplDirectory) # BRF_TAPP/COUPL
          if (not VLAB.path.exists(tmpPath)) :
            # Recherche du dossier ITERX
            tmpPath = VLAB.path.join(brfPath, Dart_DARTEnv.iterRootDirectory + 'X') # BRF_TAPP/ITERX
            if (not VLAB.path.exists(tmpPath)) :
              # Recherche du dossier ITER de plus fort nombre
              tmpPath = VLAB.path.join(brfPath, Dart_DARTEnv.iterRootDirectory + str(Dart_getNumMaxIteration(brfPath)))
          brfPath = tmpPath;
      elif (level == Dart_DataLevel.SENSOR) :
        brfPath = VLAB.path.join(bandPath, Dart_DARTEnv.sensorDirectory) # SENSOR
      else :
        brfPath = VLAB.path.join(bandPath, Dart_DARTEnv.toaDirectory) # TOA

    return brfPath

  def getAveragePerDirection(self, spectralBand = 0, dataType = Dart_DataUnit.BRF_TAPP, level = Dart_DataLevel.BOA, iteration = 'last') :
    brfPath = self.getSubdirectory(spectralBand, dataType, level, iteration)
    brf = Dart_BRF()
    if (VLAB.path.exists(brfPath)) :
      # recherche du nom de fichier contenant le brf/tapp/radiance
      if (dataType == Dart_DataUnit.RADIANCE) :
        if (level == Dart_DataLevel.ATMOSPHERE_ONLY):
          brfPath = VLAB.path.join(brfPath, Dart_DARTEnv.radianceAtmoFile)
        else:
          brfPath = VLAB.path.join(brfPath, Dart_DARTEnv.radianceFile)
      else :
        tmpPath = VLAB.path.join(brfPath, Dart_DARTEnv.brfFile)
        if (not VLAB.path.exists(tmpPath)) :
          tmpPath = VLAB.path.join(brfPath, Dart_DARTEnv.tappFile)
        brfPath = tmpPath

      if (VLAB.path.exists(brfPath) and VLAB.path.isfile(brfPath)) :
        # lecture du fichier et remplissage du conteneur
        fichierBRF = open(brfPath, "r")
        lines = fichierBRF.readlines()
        for line in lines :
          split = line.split()
          brf.addValeurDansDirection(Dart_Direction(float(split[0]), float(split[1])), float(split[2]))
        fichierBRF.close()
    return brf

  def getImageNameInDirection(self, direction):
    properties = self.getProperties()
    imageNumber = properties['dart.products.images.number']
    imageIndex = 0
    found = False
    imageName = None
    while (imageIndex < imageNumber and not found):
      directionIndex = int(properties['dart.products.image' + str(imageIndex) + '.directionIndex'])
      if (directionIndex == direction.index):
        imageName = properties['dart.products.image' + str(imageIndex) + '.name']
        found = True
      else:
        imageIndex = imageIndex + 1
    return imageName

  def getImageMinMaxInDirection(self, direction, spectralBand = 0, dataType = Dart_DataUnit.BRF_TAPP, level = Dart_DataLevel.BOA, iteration = 'last', projectionPlane=Dart_ProjectionPlane.SENSOR_PLANE) :
    brfPath = self.getSubdirectory(spectralBand, dataType, level, iteration)
    minImage = None
    maxImage = None
    if (VLAB.path.exists(brfPath)) :
      imageDirPath = VLAB.path.join(brfPath, Dart_DARTEnv.imageDirectoy)
      if (projectionPlane == Dart_ProjectionPlane.ORTHOPROJECTION):
        imageDirPath = VLAB.path.join(imageDirPath, Dart_DARTEnv.orthoProjectedImageDirectory)
      elif (projectionPlane == Dart_ProjectionPlane.BOA_PLANE):
        imageDirPath = VLAB.path.join(imageDirPath, Dart_DARTEnv.nonProjectedImageDirectory)
      imageName = self.getImageNameInDirection(direction)
      mprPath = VLAB.path.join(imageDirPath, imageName + '.mpr')
      if (VLAB.path.exists(mprPath)):
        mprFile = open(mprPath, "r")
        lines = mprFile.readlines()
        for line in lines :
          split = line.split('=')
          if (split[0].startswith('MinMax')):
            splitSplit = split[1].split(':')
            minImage = float(splitSplit[0])
            maxImage = float(splitSplit[1])
            mprFile.close()
            return (minImage, maxImage)
        mprFile.close()
    return (minImage, maxImage)

  def getImageInDirection(self, direction, spectralBand = 0, dataType = Dart_DataUnit.BRF_TAPP, level = Dart_DataLevel.BOA, iteration = 'last', projectionPlane=Dart_ProjectionPlane.SENSOR_PLANE):
    brfPath = self.getSubdirectory(spectralBand, dataType, level, iteration)
    VLAB.logger.info('brfPath is %s' % brfPath)
    data = []
    if (VLAB.path.exists(brfPath)):
      imageDirPath = VLAB.path.join(brfPath, Dart_DARTEnv.imageDirectoy)
      if (projectionPlane == Dart_ProjectionPlane.ORTHOPROJECTION):
        imageDirPath = VLAB.path.join(imageDirPath, Dart_DARTEnv.orthoProjectedImageDirectory)
      elif (projectionPlane == Dart_ProjectionPlane.BOA_PLANE):
        imageDirPath = VLAB.path.join(imageDirPath, Dart_DARTEnv.nonProjectedImageDirectory)
      imageName = self.getImageNameInDirection(direction)
      # Recovery of the size of the image, in pixels
      mprPath = VLAB.path.join(imageDirPath, imageName + '.mpr')
      VLAB.logger.info('mprPath is %s' % mprPath)
      if (VLAB.path.exists(mprPath)):
        sizeX = 0
        sizeY = 0
        mprFile = open(mprPath, "r")
        lines = mprFile.readlines()
        for line in lines:
          split = line.split('=')
          if (split[0].startswith('Size')):
            splitSplit = split[1].split(' ')
            sizeX = int(splitSplit[0])
            sizeY = int(splitSplit[1])
        mprFile.close()
        mpSharpPath = VLAB.path.join(imageDirPath, imageName + '.mp#')
        if (VLAB.path.exists(mpSharpPath)):
          mpSharpFile = open(mpSharpPath, "rb")
          for x in range(sizeX):
            line = []
            for y in range(sizeY):
              line.append(struct.unpack('d', mpSharpFile.read(8))[0])
            data.append(line)
          mpSharpFile.close()
    return data

  def getIterMaxPath(self, spectralBand, iterX=True):
    """ Return the iterYY folder where YY is X is exist and iterX is True or the iterMax folder
    """
    # Get spectralBand folder
    iterFolder = VLAB.path.join(self.rootSimulationsDirectory, self.name, "output", spectralBand, "BRF")
    # Get list of iter folders
    iters = [ folder.lstrip('ITER') for folder in VLAB.listdir(iterFolder)
              if folder.startswith('ITER')]
    # Get iterX is exists otherwise select iterMax
    if iterX and 'X' in iters:
      return VLAB.path.join(iterFolder, "ITERX")
    else:
      if 'X' in iters:
        iters.remove('X')
      iters = [ int(i) for i in iters ]
      return VLAB.path.join(iterFolder, "ITER" + str(max(iters)))


class Dart_DARTRootSimulationDirectory :
  def __init__(self) :
    pass

  def samefile(self, path1, path2) :
    return VLAB.path.normcase(VLAB.path.normpath(path1)) == VLAB.path.normcase(VLAB.path.normpath(path2))

  def getAbsolutePath(self) :
    return VLAB.path.join(DART.SDIR)#, Dart_DARTEnv.simulationsDirectory)

  def getSimulationsList(self) :
    rootSimulationPath = self.getAbsolutePath()
    # Liste de tous les fichier/dossier non cache du repertoire
    dirList=[f for f in VLAB.listdir(rootSimulationPath) if (f[0] != '.') and (VLAB.path.isdir(VLAB.path.join(rootSimulationPath, f)))]
    dirList.sort()
    listSimulations = []
    for directory in dirList:
      self.listSimulationsInPath(listSimulations, directory)
    return listSimulations

  def listSimulationsInPath(self, listSimulations, path) :
    rootPath = path
    if not VLAB.path.isabs(path):
      rootPath = VLAB.path.join(self.getAbsolutePath(), path)
    dirList=[f for f in VLAB.listdir(rootPath) if (f[0] != '.') and (VLAB.path.isdir(VLAB.path.join(rootPath, f)))]
    dirList.sort()

    isSimulation = False
    for directory in dirList:
      # On test si le dossier contient des dossiers output, input et/ou sequence
      # On relance la methode recursivement sur les eventuels autres dossiers (hors input, output et sequence)
      if (directory != Dart_DARTEnv.inputDirectory) and (directory != Dart_DARTEnv.outputDirectory) and (directory != Dart_DARTEnv.sequenceDirectory) :
        self.listSimulationsInPath(listSimulations, VLAB.path.join(path, directory))
      else :
        isSimulation = True
    if isSimulation :
      self.addSimulation(listSimulations, path)

  def addSimulation(self, listSimulations, path):
    simulation = self.getSimulation(path)
    if simulation.isValid() :
      listSimulations.append(simulation)

  def getSimulation(self, name) :
    rootSimulationPath = self.getAbsolutePath()
    rootPath = name
    if not VLAB.path.isabs(name):
      rootPath = VLAB.path.join(rootSimulationPath, name)
    simulationName = ''
    if not VLAB.path.exists(rootPath) :
      simulationName = name
    elif not self.samefile(rootPath, rootSimulationPath) :
      if VLAB.path.isdir(rootPath):
        (head, tail) = VLAB.path.split(rootPath)
        while not self.samefile(head, rootSimulationPath) and head !='' :
          simulationName = VLAB.path.join(tail, simulationName)
          (head, tail) = VLAB.path.split(head)
        else :
          if head != '' :
            simulationName = VLAB.path.join(tail, simulationName)
          else :
            simulationName = ''
    return Dart_DARTSimulation(simulationName, self)

class Dart_DARTDao :
  def __init__(self) :
    pass

  def getRootSimulationDirectory(self) :
    return Dart_DARTRootSimulationDirectory()

  def getSimulationsList(self) :
    return self.getRootSimulationDirectory().getSimulationsList()

  def getSimulation(self, name) :
    return self.getRootSimulationDirectory().getSimulation(name)

# FIXME Is this class still needed?
def Dart_Bandes(simulationProperties):
  propertiesDico = Dart_readPropertiesFromFile(simulationProperties)
  i = int(propertiesDico['phase.nbSpectralBands'])
  bandes = []
  for j in range(i):
    bande = {}
    bande['spectralBandwidth'] = round(float(propertiesDico['dart.band' + str(j) + '.lambdaMax']) - float(propertiesDico['dart.band' + str(j) + '.lambdaMin']),4)
    a = float(propertiesDico['dart.band' + str(j) + '.lambdaMin']) + bande['spectralBandwidth'] / 2
    bande['centralWavelength'] = round(float(a),4)
    bande['mode'] = propertiesDico['dart.band' + str(j) + '.mode']
    bandes.append(bande)
  return bandes

class Dart_dolibradtran:

  def main(self, q):
    # generate arguments for doLibradtran
    r = {
      'CO2'      : q[VLAB.P_AtmosphereCO2],
      'H2O'      : q[VLAB.P_AtmosphereWater],
      'O3'       : q[VLAB.P_AtmosphereOzone],
      'scene'    : q[VLAB.P_3dScene],
      'aerosol'  : q[VLAB.P_AtmosphereAerosol],
      'sensor'   : q[VLAB.P_Sensor],
      'rpv_file' : '%s/rami.TOA/rpv.rami.libradtran.dat.all' % LIBRAT.SDIR,
      'infile'   : '%s/%s/input/%s' % (DART.SDIR, q['simulationName'], 'UVSPEC-in.txt'),
      'outfile'  : '%s/%s/output/%s' %(DART.SDIR, q['simulationName'], 'UVSPEC-out.txt'),
    }
    #
    # TODO: loop over something to produce umu, phi ,phi0, sza, etc.
    #
    VLAB.doLibradtran(r)

#==============================================================================
#title            :Dart_DartImages.py
#description      :This script can be used to write a *.bsq binary file and a corresponding ENVI header *.hdr from DART output images
#required scripts :Dart_DARTDao.py
#author           :Fabian Schneider, Nicolas Lauret
#date             :20130328
#version          :1.0
#usage            :see writeDataCube.py
#==============================================================================


class Dart_DartImages :
  def __init__(self) :
    pass

  # http://rightfootin.blogspot.ch/2006/09/more-on-python-flatten.html, based on Mike C. Fletcher's BasicTypes library
  def flatten( self, l, ltypes=(list, tuple)):
    ltype = type(l)
    l = list(l)
    i = 0
    while i < len(l):
      while isinstance(l[i], ltypes):
        if not l[i]:
          l.pop(i)
          i -= 1
          break
        else:
          l[i:i + 1] = l[i]
      i += 1
    return ltype(l)

  def getImagesBandsAsList( self, args ) :

    simulation = Dart_DARTDao().getSimulation( args['di_simName'] )

    imagesList = []
    spectralBandsList = []

    if args['di_isSeq']:
      sequencesList = simulation.listSequences( args['di_sequence'] )

      for sequence in sequencesList:
        # Recover the number of Spectral Band
        spectralBands = sequence.getSpectralBands()

        # Recover the Directions
        if args['ii_isUsrDir']:
          directions = sequence.getUserDirections()
        else:
          directions = simulation.getDiscretizedDirection()

        # Recover the images in the defined direction for each spectral band
        for band in spectralBands:
          VLAB.logger.info('spectralBand: %s' % (band))
          imagesList.append(sequence.getImageInDirection( directions[ args['ii_dirNum'] ], band.index, args['ii_dType'], args['ii_iLevel'], args['ii_iter'],  args['ii_projPlane'] ))
          spectralBandsList.append( band )
    else:
      # Recover the number of Spectral Band
      spectralBands = simulation.getSpectralBands()

      # Recover the Directions
      if args['ii_isUsrDir']:
        directions = sequence.getUserDirections()
      else:
        directions = simulation.getDiscretizedDirection()

      # Recover the images in the defined direction for each spectral band
      for band in spectralBands:
        imagesList.append(simulation.getImageInDirection( directions[ args['ii_dirNum'] ], band.index, args['ii_dType'], args['ii_iLevel'], args['ii_iter'],  args['ii_projPlane'] ))
        spectralBandsList.append( band )

    VLAB.logger.info('imagesList has %d entries' % len(imagesList))
    VLAB.logger.info('spectralBandsList has %d entries' % len(spectralBandsList))
    return imagesList, spectralBandsList

  def writeDataCube( self, args ) :

    imagesList, spectralBandsList = self.getImagesBandsAsList( args )

    # write BSQ binary file
    if (len(args['OutputDirectory']) == 0):
      args['OutputDirectory'] = '%s/%s/' % (DART.SDIR, args['di_simName'])
    VLAB.mkDirPath(args['OutputDirectory'])
    fname = '%s/%s%s.bsq' % (args['OutputDirectory'], args['OutputPrefix'], args['di_outfname'])
    VLAB.logger.info('writing output bsq %s' % (fname))
    fout = open( fname, 'wb')
    flatarray = array('f', self.flatten( imagesList ))
    flatarray.tofile(fout)
    fout.close()

    # ENVI header information, more infos on: http://geol.hu/data/online_help/ENVI_Header_Format.html
    samples = 0
    lines = 0
    if (len(imagesList) > 0):
      lines = len( imagesList[0] )
      if (len(imagesList[0]) > 0):
        samples = len( imagesList[0][0] )
    bands = len( imagesList )
    headerOffset = 0
    fileType = 'ENVI Standard'
    dataType = 4
    interleave = 'BSQ'
    byteOrder = 0
    xStart = 1
    yStart = 1
    defaultBands = '{0}'
    wavelengthUnits = 'Nanometers'
    wavelength = ''
    fwhm = ''
    for band in spectralBandsList:
      wavelength += str( band.getCentralWaveLength()*1000 ) + ', '
      fwhm += str( band.getBandWidth()*1000 ) + ', '

    # write ENVI header file
    if (len(args['OutputDirectory']) == 0):
      args['OutputDirectory'] = '%s/%s/' % (DART.SDIR, args['di_simName'])
    VLAB.mkDirPath(args['OutputDirectory'])
    fname = '%s/%s%s.hdr' % (args['OutputDirectory'], args['OutputPrefix'], args['di_outfname'])
    VLAB.logger.info('writing output hdr %s' % (fname))
    fout = open( fname, 'w')
    fout.writelines( 'ENVI ' + '\n' )
    fout.writelines( 'description = { ' + args['hi_desc'] + ' }' + '\n' )
    fout.writelines( 'samples = ' + str( samples ) + '\n' )
    fout.writelines( 'lines = ' + str( lines ) + '\n' )
    fout.writelines( 'bands = ' + str( bands ) + '\n' )
    fout.writelines( 'header offset = ' + str( headerOffset ) + '\n' )
    fout.writelines( 'file type = ' + fileType + '\n' )
    fout.writelines( 'data type = ' + str( dataType ) + '\n' )
    fout.writelines( 'interleave = ' + interleave + '\n' )
    fout.writelines( 'sensor type = ' + args['hi_sensor'] + '\n' )
    fout.writelines( 'byte order = ' + str( byteOrder ) + '\n' )
    fout.writelines( 'x start = ' + str( xStart ) + '\n' )
    fout.writelines( 'y start = ' + str( yStart ) + '\n' )
    fout.writelines( 'map info = {' + args['hi_projName'] + ', ' + str( args['hi_xRefPixl'] ) + ', ' + str( args['hi_yRefPixl'] ) + ', ' + str( args['hi_xRefCoord'] ) + ', ' + str( args['hi_yRefCoord'] ) + ', ' + str( args['hi_xPixSize'] ) + ', ' + str( args['hi_yPixSize'] ) + ', ' + args['hi_pixUnits'] + ' }' + '\n' )
    fout.writelines( 'default bands = ' + defaultBands + '\n' )
    fout.writelines( 'wavelength units = ' + wavelengthUnits + '\n' )
    fout.writelines( 'wavelength = { ' + wavelength[:-2] + ' }' + '\n' )
    fout.writelines( 'fwhm = { ' + fwhm[:-2] + ' }' + '\n' )
    fout.close()

#==============================================================================
#title            :writeDataCube.py
#description      :This script writes a *.bsq binary file and a corresponding ENVI header *.hdr from DART output images
#required scripts :Dart_DartImages.py + Dart_DARTDao.py
#author           :Fabian Schneider
#date             :20130328
#version          :1.0
#usage            :python writeDataCube.py
#==============================================================================

#
# End of Dart_* integration routines
#

class DART:
  if VLAB.osName().startswith('Windows'):
    SDIR=VLAB.expandEnv('%HOMEDRIVE%%HOMEPATH%/.beam/beam-vlab/auxdata/dart_local/simulations')
  else:
    SDIR=VLAB.expandEnv('$HOME/.beam/beam-vlab/auxdata/dart_local/simulations')

  """Integration glue for calling external DART programs"""
  def __init__(self):
    me=self.__class__.__name__ +'::'+VLAB.me()
    VLAB.logger.info('%s: constructor completed...' % me)

  def dartSZA2libradtranSZA(self, sz, sa):
    """ DART uses theta value from 0 to 180 for zenith angle (half a circle) 
        and 0 to 360 for azimuth angle (full circle).
        In the upper sphere the zenith range is from 0 to 90.
        It is necessary to convert to libradtran zenith and azimuth range
        (-90 to 90 for zenith and 0-180 for azimuth).
    """
    if sa > 180.0:
      sz = -sz
      sa = sa - 180.0

    return sz, sa

  def _writeSeqFile(self, args):
    """ Write DART sequence file
    """
    sstr = """<?xml version="1.0" encoding="UTF-8"?>
<DartFile version="1.0">
    <DartSequencerDescriptor sequenceName="sequence;;%s">
        <DartSequencerDescriptorEntries>
            <DartSequencerDescriptorGroup groupName="group_%s">%s
            </DartSequencerDescriptorGroup>
        </DartSequencerDescriptorEntries>
        <DartSequencerPreferences dartLaunched="true"
            demGeneratorLaunched="false" directionLaunched="true"
            displayEnabled="true" hapkeLaunched="false"
            maketLaunched="true" numberParallelThreads="1"
            phaseLaunched="false" prospectLaunched="false"
            triangleFileProcessorLaunched="false"
            vegetationLaunched="false" zippedResults="false"/>
        <DartLutPreferences addedDirection="false" coupl="true"
            generateLUT="false" iterx="true" luminance="true"
            ordre="true" otherIter="true" phiMax="" phiMin=""
            reflectance="true" sensor="true" storeIndirect="false"
            thetaMax="" thetaMin="" toa="true"/>
    </DartSequencerDescriptor>
</DartFile>
"""
    dstr = """
                <DartSequencerDescriptorEntry args="%s"
                    propertyName="%s" type="enumerate"/>"""
    groupstr = ""
    for ent in args['entries']:
      (dargs, prop) = ent
      groupstr += (dstr % (dargs, prop))
    paramfilename = '%s/%s/%s' % (DART.SDIR, args['simulation'], args['fileName'])
    VLAB.logger.info('writing sequence paramfile "%s"' % paramfilename)
    fp = open(paramfilename, 'w')
    fp.write(sstr % (args['fileName'].rstrip(".xml"), args['fileName'].rstrip('.xml'), groupstr))
    fp.close()

  def doProcessing(self, pm, args):
    """do processing for DART processor"""
    me=self.__class__.__name__ +'::'+VLAB.me()

    if (pm != None):
      pm.beginTask("Computing BRF...", 10)
    # ensure at least 1 second to ensure progress popup feedback
    time.sleep(1)

    q = {
      'rpvfile'    : 'angles.rpv.2.dat',
      'simulation' : 'Unknown',

      ## RPV inversion
      'verbose':True,
      'plot':True,
      'show':False,
      'three':True,
      'paramfile':'result.brdf.dat.3params.dat',
      'plotfile':'result.brdf.dat.3params',
      'wbfile':'wb.full_spectrum.1nm.dat',
      'wb':'wb.full_spectrum.1nm.dat',
      'v':True
    }

    # overwrite defaults
    for a in args:
      # ensure arguments get passed on
      q[a] = args[a]
      if a == 'Sensor':
        q['sensor'] = args[a]
        if args[a] == VLAB.K_SENTINEL2:
          q['wb'] = 'wb.MSI.dat'
          q['wbfile'] = "%s/%s" % (LIBRAT.SDIR, 'wb.MSI.dat')
          q['angfile'] = "%s/%s" % (LIBRAT.SDIR, 'angles.MSI.dat')
        elif args[a] == VLAB.K_SENTINEL3:
          q['wb'] = 'wb.OLCI.dat'
          q['wbfile'] = "%s/%s" % (LIBRAT.SDIR, 'wb.OLCI.dat')
          q['angfile'] = "%s/%s" % (LIBRAT.SDIR, 'angles.OLCI.dat')
        elif args[a] == VLAB.K_MODIS:
          q['wb'] = 'wb.MODIS.dat'
          q['wbfile'] = "%s/%s" % (LIBRAT.SDIR, 'wb.MODIS.dat')
          q['angfile'] = "%s/%s" % (LIBRAT.SDIR, 'angles.MODIS.dat')
        elif args[a] == VLAB.K_MERIS:
          q['wb'] = 'wb.MERIS.dat'
          q['wbfile'] = "%s/%s" % (LIBRAT.SDIR, 'wb.MERIS.dat')
          q['angfile'] = "%s/%s" % (LIBRAT.SDIR, 'angles.MERIS.dat')
        elif args[a] == VLAB.K_LANDSAT_OLI:
          q['wb'] = 'wb.LANDSAT.OLI.dat'
          q['wbfile'] = "%s/%s" % (LIBRAT.SDIR, 'wb.LANDSAT.OLI.dat')
          q['angfile'] = "%s/%s" % (LIBRAT.SDIR, 'angles.LANDSAT.dat')
        elif args[a] == VLAB.K_LANDSAT_ETM:
          q['wb'] = 'wb.LANDSAT.ETM.dat'
          q['wbfile'] = "%s/%s" % (LIBRAT.SDIR, 'wb.LANDSAT.ETM.dat')
          q['angfile'] = "%s/%s" % (LIBRAT.SDIR, 'angles.LANDSAT.dat')
        else:
          q['wb'] = 'wb.full_spectrum.1nm.dat'
          q['wbfile'] = "%s/%s" % (LIBRAT.SDIR, 'wb.full_spectrum.1nm.dat')
          q['angfile'] = "%s/%s" % (LIBRAT.SDIR, 'angles.rami.dat')
      if a == VLAB.P_3dScene:
        if args[a] == VLAB.K_RAMI:
          q['simulation'] = 'HET01_DIS_UNI_NIR_20'
        elif args[a] == VLAB.K_LAEGERN:
          q['simulation'] = 'Laegern'
        elif args[a] == VLAB.K_THARANDT:
          q['simulation'] = "Tharandt"
      elif a == VLAB.P_ViewingAzimuth:
        q['va'] = args[a]
      elif a == VLAB.P_ViewingZenith:
        q['vz'] = args[a]
      elif a == VLAB.P_IlluminationAzimuth:
        q['sa'] = args[a]
      elif a == VLAB.P_IlluminationZenith:
        q['sz'] = args[a]
      elif a == VLAB.P_Bands:
        # This would allow choosing particular bands
        # q['bands'] = [int(i) for i in tuple(args[a].split(", "))]
        bands = VLAB.getBandsFromGUI(args[VLAB.P_Sensor])
        q['bands'] = range(1,len(bands)+1)
      elif a == VLAB.P_ScenePixel:
        q['pixelSize'] = args[a]
      else:
        q[a] = args[a]

    # Setup new simulation folder name
    q['simulationName'] = q['simulation'] + "_run"

    # Setup RPV inversion parameters
    q['dataf'] = 'result.%s.brdf.dat' % q['simulation']
    q['paramfile'] = 'result.%s.brdf.dat.3params.dat' % q['simulation']
    q['plotfile'] = 'result.%s.brdf.3params' % q['simulation']
    q['outputFolder'] = VLAB.path.join(DART.SDIR, q['simulationName'])
    q['opdir']        = VLAB.path.join(DART.SDIR, q['simulationName'])
    q['rpv'] = 'result.%s.brdf.dat.3params.dat' % q['simulation']

    ## LibRadtran parameters
    q['infile'] = "%s/%s" % (q['outputFolder'], "libradtran_in.dat")
    q['outfile'] = "%s/%s" % (q['outputFolder'], "libradtran_out.dat")
    q['rpv_file'] = "%s/%s" % (q['outputFolder'], q['paramfile'])
    q['CO2'] = args[VLAB.P_AtmosphereCO2]
    q['H2O'] = args[VLAB.P_AtmosphereWater]
    q['O3'] = args[VLAB.P_AtmosphereOzone]
    q['scene'] = args[VLAB.P_3dScene]
    q['aerosol'] = args[VLAB.P_AtmosphereAerosol]
    q['sensor'] = args[VLAB.P_Sensor]


    # 1. Create the DART scene
    # 1. a. Copy DART original input file to a new folder
    VLAB.copyDir(VLAB.path.join(DART.SDIR, q['simulation']), VLAB.path.join(DART.SDIR, q['simulationName']))

    # 1. b. Update the DART input files with parameters from GUI
    # In phase change the number of thread
    phase = VLAB.path.join(DART.SDIR, q['simulationName'], "input", "phase.xml")
    # We do not yet trust self reporting of CPUs
    if False:
      VLAB.XMLEditNode(phase, "ExpertModeZone", "nbThreads", str(VLAB.getAvailProcessors()))
    else:
      VLAB.XMLEditNode(phase, "ExpertModeZone", "nbThreads", str(VLAB.CONF_DART_N_THREAD))

    # In maket change the pixel size
    maket = VLAB.path.join(DART.SDIR, q['simulationName'], "input", "maket.xml")
    ## TODO: Fix it when the option will be avaiblable
    if str(q['pixelSize']).isdigit():
        VLAB.XMLEditNode(maket, "CellDimensions", ["x", "z"], [q['pixelSize']]*2)
    else:
        VLAB.logger.info("WARNING: Changing cell dimensions is currently not available")
    # In direction change the Sun viewving angle
    direction = VLAB.path.join(DART.SDIR, q['simulationName'], "input", "directions.xml")
    VLAB.XMLEditNode(direction, "SunViewingAngles",
                     ["sunViewingAzimuthAngle", "sunViewingZenithAngle"],
                     [q['sa'], q['sz']])
    # In direction set ifCosWeighted and numberOfPropagationDirections attributes
    VLAB.XMLEditNode(direction, "Directions",
                     ["ifCosWeighted", "numberOfPropagationDirections"],
                     ["1", "100"])
    # In direction set viewing direction
    VLAB.XMLAddNode(direction, "Directions",
                    ["AddedDirections", "ZenithAzimuth", "Square", "DefineOmega"],
                    {"AddedDirections": {"attribute":
                                         ["directionType", "ifSquareShape", "imageDirection"],
                                         "value": ["0", "1", "1"],
                                         "parent":"Directions"},
                     "ZenithAzimuth": {"attribute":
                                       ["directionAzimuthalAngle", "directionZenithalAngle"],
                                       "value": [q['va'], q['vz']],
                                       "parent":"AddedDirections"},
                     "Square": {"attribute": ["widthDefinition"], "value": ["0"],
                                "parent":"AddedDirections"},
                     "DefineOmega": {"attribute": ["omega"], "value": ["0.001"], "parent":"Square"}
                    }
                   )
    # In phase force the radiance to be stored (could be not selected)
    VLAB.XMLEditNode(phase, "BrfProductsProperties", "luminanceProducts", "1")
    # In phase change the spectral bands
    bands = VLAB.getBandsFromGUI(q[VLAB.P_Sensor])
    VLAB.XMLReplaceNodeContent(phase, "SpectralIntervals", "SpectralIntervalsProperties",
                               ["deltaLambda", "meanLambda"],
                               bands, spectralBands=True)
    # In phase change add SpectralIrradianceValue for each spectral bands
    if q['simulation'] == "HET01_DIS_UNI_NIR_20":
        VLAB.XMLReplaceNodeContent(phase, "SpectralIrradiance", "SpectralIrradianceValue",
                                   ["bandNumber", "irradiance"],
                                   [ [str(bandNumber), str(1000.0)] for bandNumber in xrange(len(bands)) ]
                                  )
    # In coeff_diff change multiplicativeFactorForLUT to allways be equal to "0"
    coeffDiff = VLAB.path.join(DART.SDIR, q['simulationName'], "input", "coeff_diff.xml")
    VLAB.XMLEditNode(coeffDiff, "LambertianMulti", "useMultiplicativeFactorForLUT", "0", multiple=True)
    VLAB.XMLEditNode(coeffDiff, "UnderstoryMulti", "useMultiplicativeFactorForLUT", "0", multiple=True)

    # Get number of band
    nbBands = len(bands)

    # 2. a. Run DART direction module
    cmd = {
      'linux' : {
        'cwd'     : '$HOME/.beam/beam-vlab/auxdata/dart_lin64/tools/linux',
        'exe'     : '/bin/bash',
        'cmdline' : ['$HOME/.beam/beam-vlab/auxdata/dart_lin64/tools/linux/dart-directions.sh', q['simulationName']],
        'stdin'   : None,
        'stdout'  : None,
        'stderr'  : None,
        'env'     : None,
        },
      'windows'   : {
        'cwd'     : '%HOMEDRIVE%%HOMEPATH%/.beam/beam-vlab/auxdata/dart_win32/tools/windows',
        'exe'     : None,
        'cmdline' : ['%HOMEDRIVE%%HOMEPATH%/.beam/beam-vlab/auxdata/dart_win32/tools/windows/dart-directions.bat', q['simulationName']],
        'stdin'   : None,
        'stdout'  : None,
        'stderr'  : None,
        'env'     : None,
       }
    }
    VLAB.logger.info('command: %s' % cmd)
    exitCode = VLAB.doExec(cmd)
    if exitCode != 0:
      raise Exception("dart-directions failed with return code=%d" % exitCode)

    # 2. b. Get the first two cols (sz, sa) where sz < 70 deg - use as sequence
    zlist = []; alist = []
    for row in VLAB.valuesfromfile('%s/%s/output/directions.txt' % (DART.SDIR, q['simulationName'])):
      (sz, sa, _, _)  = row
      if (sz < 70.0):
        zlist.append(sz); alist.append(sa)
    zparam = ";".join('%.2f' % x for x in zlist)
    aparam = ";".join('%.2f' % x for x in alist)

    # 2. c. Edit simulation directions.xml file to set the number of direcions to 200
    VLAB.XMLEditNode(direction, "Directions", "numberOfPropagationDirections", "200")

    # 2. d. Write sequence file
    seqparams = {'fileName'   : 'SunDirections.xml',
                 'simulation' : q['simulationName'],
                 'entries'    : [[aparam, 'Directions.SunViewingAngles.sunViewingAzimuthAngle'],
                                 [zparam, 'Directions.SunViewingAngles.sunViewingZenithAngle']
                                ]
                }
    self._writeSeqFile(seqparams)


    # 3. a. Run DART to pregenerate phase, maket, (3D obj..) before the sequence
    cmd = {
      'linux' : {
        'cwd'     : '$HOME/.beam/beam-vlab/auxdata/dart_lin64/tools/linux',
        'exe'     : '/bin/bash',
        'cmdline' : ['$HOME/.beam/beam-vlab/auxdata/dart_lin64/tools/linux/dart-full.sh', q['simulationName']],
        'stdin'   : None,
        'stdout'  : None,
        'stderr'  : None,
        'env'     : None,
        },
      'windows'   : {
        'cwd'     : '%HOMEDRIVE%%HOMEPATH%/.beam/beam-vlab/auxdata/dart_win32/tools/windows',
        'exe'     : None,
        'cmdline' : ['%HOMEDRIVE%%HOMEPATH%/.beam/beam-vlab/auxdata/dart_win32/tools/windows/dart-full.bat', q['simulationName']],
        'stdin'   : None,
        'stdout'  : None,
        'stderr'  : None,
        'env'     : None,
       }
    }
    VLAB.logger.info('command: %s' % cmd)
    exitCode = VLAB.doExec(cmd)
    if exitCode != 0:
      raise Exception("dart-full failed with return code=%d" % exitCode)

    # 3. b. Run the sun directions sequence with number of directions=200
    cmd = {
      'linux' : {
        'cwd'     : '$HOME/.beam/beam-vlab/auxdata/dart_lin64/tools/linux',
        'exe'     : '/bin/bash',
        'cmdline' : ['$HOME/.beam/beam-vlab/auxdata/dart_lin64/tools/linux/dart-sequence.sh', q['simulationName'], seqparams['fileName']],
        'stdin'   : None,
        'stdout'  : None,
        'stderr'  : None,
        'env'     : None,
        },
      'windows'   : {
        'cwd'     : '%HOMEDRIVE%%HOMEPATH%/.beam/beam-vlab/auxdata/dart_win32/tools/windows',
        'exe'     : None,
        'cmdline' : ['%HOMEDRIVE%%HOMEPATH%/.beam/beam-vlab/auxdata/dart_win32/tools/windows/dart-sequence.bat', q['simulationName'], seqparams['fileName']],
        'stdin'   : None,
        'stdout'  : None,
        'stderr'  : None,
        'env'     : None,
       }
    }
    VLAB.logger.info('command: %s' % cmd)
    exitCode = VLAB.doExec(cmd)
    if exitCode != 0:
      raise Exception("dart-sequence failed with return code=%d" % exitCode)

    # 4.a. Select the values of sz < 70 to get BANDX.angles.rpv.2.dat
    # for each spectral band in the DART simulation
    brdfList = []
    rpvFiles = []
    seqDir = VLAB.path.join(DART.SDIR, q['simulationName'], "sequence")
    # Loop over all Sun direction
    for seqSubDir in VLAB.listdir(seqDir):
      brdfList = []
      dirFile = VLAB.path.join(seqDir, seqSubDir, "input", "directions.xml")
      sa = float(VLAB.XMLGetNodeAttributeValue(dirFile, "SunViewingAngles", "sunViewingAzimuthAngle"))
      sz = float(VLAB.XMLGetNodeAttributeValue(dirFile, "SunViewingAngles", "sunViewingZenithAngle"))
      selectedBRF = []
      vzList, vaList = [], []
      # Loop over each spectral band
      for bandNumber in xrange(nbBands):
        dartBRF = VLAB.path.join(Dart_DARTSimulation(seqSubDir, seqDir).getIterMaxPath('BAND' + str(bandNumber)), "brf")
        if bandNumber <= 0:
            # Get vz, va and brf for band 0
            vzList, vaList, selectedBRF = VLAB.valuesfromfile(dartBRF, transpose=True)
            selectedBRF = [selectedBRF]
        else:
            # Get brf only for the other bands (>0) (same order in all bands in brf file)
            selectedBRF.append(VLAB.valuesfromfile(dartBRF, transpose=True)[-1])
      # Filter, convert and append the BRF values and viewing angles to the brdfList variable
      for vz, va, brf in zip(vzList, vaList, zip(*selectedBRF)):
        if vz < 70.0:
          # Convert DART output to librattran input
          vz, va = self.dartSZA2libradtranSZA(vz, va)
          brf = [ "%.2f" % BRFval for BRFval in brf ]
          brdfList.append( "%.2f\t%.2f\t%.2f\t%.2f\t" % (vz, va, sz, sa) + "\t".join(brf) )

    # Write brdf in the result file
    fp = open(VLAB.path.join(q['outputFolder'], q['dataf']), "w")
    fp.write("\n".join(brdfList))
    fp.close()

    # 4.b. Run RPV inverter
    rpv_invert = Librat_rpv_invert()
    rpv_invert.main(q)

    # 4.b. Run libradtran
    VLAB.doLibradtran(q)

    #
    # collect result into a consolidated data cube
    #
    dargs = {
      'di_simName'   : q['simulationName'],
      'di_isSeq'     : False,
      'di_sequence'  : 'sequence_apex',
      'di_outfname'  : 'DartOutput',
      'ii_iLevel'    : Dart_DataLevel.BOA,
      'ii_isUsrDir'  : False,
      'ii_dirNum'    : 0,
      'ii_dType'     : Dart_DataUnit.RADIANCE,
      'ii_iter'      : 'last',
      'ii_projPlane' : Dart_ProjectionPlane.SENSOR_PLANE,
      'hi_desc'      : 'some text',
      'hi_sensor'    : 'APEX',
      'hi_projName'  : 'Arbitrary',
      'hi_xRefPixl'  : 1,
      'hi_yRefPixl'  : 1,
      'hi_xRefCoord' : '2669660.0000',
      'hi_yRefCoord' : '1259210.0000',
      'hi_xPixSize'  : 1,
      'hi_yPixSize'  : 1,
      'hi_pixUnits'  : 'units=Meters'
    }
    # merge in data cube arguments
    for d in dargs:
      args[d] = dargs[d]

    VLAB.logger.info('args is %s' % args)
    Dart_DartImages().writeDataCube( args )
    VLAB.logger.info('%s: finished computing...' % me)

    # Copy to results directory
    srcdir = VLAB.path.join(DART.SDIR, q['simulationName'])
    if VLAB.fileExists(srcdir):
      # Copy to results directory
      resdir = VLAB.fPath(DART.SDIR, "../../results/dart/%s/%s" % (args['OutputDirectory'], q['simulationName']))
      VLAB.mkDirPath(resdir)
      VLAB.logger.info('%s: skipping copy of result %s -> %s' % (me, srcdir, resdir))
      #too much data, too much time
      #VLAB.copyDir(srcdir, resdir)
      VLAB.logger.info('%s: Done...' % me)

#### DART end ################################################################

#### LIBRAT start ############################################################
#
# Librat_ integration routines contributed by Mat Disney and Philip Lewis 
# adapted for BEAM-embedded jython by Cyrill Schenkel and Jason Brazile
#
################
class Librat_dobrdf:
  def _writeCamFile(self, camFile, args):

    # defaults
    q = {
      'cam_camera'      : 'simple camera',
      'perspective'     : False,
      'result_image'    : 'result.image',
      'integral_mode'   : 'scattering order',
      'integral'        : 'result',
      'vz'              : 0,
      'va'              : 0,
      'twist'           : 0,
      'look'            : (0., 0., 0.),
      'ideal'           : (100., 100.),
      'boom'            : 1000.,
      'npixels'         : 100000,
      'rpp'             : 1,
      'fov'             : 180
    }

    # overwrite defaults
    for a in args:
      q[a] = args[a]

    cdata = ' camera { \n' \
+ ' %s = "%s";\n' %('camera.name', q['cam_camera']) \
+ ' %s = %s;\n'   %('geometry.zenith', q['vz']) \
+ ' %s = %s;\n'   %('geometry.azimuth', q['va']) \
+ ' %s = "%s";\n' %('result.image', q['result_image']) \
+ ' %s = "%s";\n' %('result.integral.mode', q['integral_mode']) \
+ ' %s = "%s";\n' %('result.integral', q['integral']) \
+ ' %s = %s;\n'   %('samplingCharacteristics.nPixels', q['npixels']) \
+ ' %s = %s;\n'   %('samplingCharacteristics.rpp', q['rpp']) \
+ ' %s = %s;\n'   %('geometry.idealArea', ', '.join(map(str,map('%.1f'.__mod__, q['ideal'])))) \
+ ' %s = %s;\n'   %('geometry.lookat', ', '.join(map(str,map('%.1f'.__mod__,q['look_xyz'])))) \
+ ' %s = %s;\n'   %('geometry.boomlength', q['boom'])

    if q['perspective']:
      cdata += ' %s = %s;\n' %('geometry.perspective', q['perspective'])
    if q['twist']:
      cdata += ' %s = %s;\n' %('geometry.twist', q['twist'])
    if q['fov']:
      cdata += ' %s = %s;\n' %('geometry.fieldOfView', q['fov'])
    if 'lidar' in q:
      if q['lidar']:
        cdata += ' %s = %s;\n' %('lidar.binStep', q['binStep']) \
               + ' %s = %s;\n' %('lidar.binStart', q['binStart']) \
               + ' %s = %s;\n' %('lidar.nBins', q['nBins'])
    cdata += '}'

    if q['fov'] and q['ideal']:
      raise Exception("camera: setting both 'ideal area' and 'fov' is not allowed")

    fp = open(camFile, 'w')
    try:
      fp.write(cdata)
    finally:
      fp.close()

  def _writeLightFile(self, lightFile, args):

    # defaults
    q = {
      'light_camera' : 'simple illumination',
       'sz'          : 0.,
       'sa'          : 0.,
       'twist'       : 0.,
    }

    # overwrite detaults
    for a in args:
      q[a] = args[a]

    ldata = ' camera { \n' \
+ ' %s = "%s";\n'   %('camera.name', q['light_camera']) \
+ ' %s = "%.1f";\n' %('geometry.zenith', float(q['sz'])) \
+ ' %s = "%.1f";\n' %('geometry.azimuth', float(q['sa'])) \
+ ' %s = "%.1f";\n' %('geometry.twist', float(q['twist']))

    key = "sideal"
    if key in q: ldata += '%s = %s\n' %('geometry.idealArea', ', '.join(map(str, map('%.1f'.__mod__, q[key]))))
    key = "slook_xyz"
    if key in q: ldata += '%s = %s\n' %('geometry.lookat', ', '.join(map(str, map('%.1f'.__mod__, q[key]))))
    key = "sboom"
    if key in q: ldata += '%s = %s\n' %('geometry.boom', q[key])
    key = "sperspective"
    if key in q: ldata += '%s = %s\n' %('geometry.perspecitive', q[key])
    key = "sfov"
    if key in q: ldata += '%s = %s\n' %('geometry.fov', q[key])
    ldata += '}'
    fp = open(lightFile, 'w')
    try:
      fp.write(ldata)
    finally:
      fp.close()


  def _writeInputFile(self, inpFile, lightFile, camFile):
    idata = '14' \
   + ' "' \
   + VLAB.getFullPath(camFile) \
   + '" "' \
   + VLAB.getFullPath(lightFile) \
   + '"'
    fp = open(inpFile, 'w')
    try:
      fp.write(idata)
    finally:
      fp.close()

  def _writeGrabFile(self, grabFile, args):
    gFilePath = VLAB.getFullPath(grabFile)
    if VLAB.osName().startswith('Windows'): 
      gFilePath = gFilePath.replace("\\", "\\\\")
    # 'cwd'     : '$HOME/.beam/beam-vlab/auxdata/librat_scenes',
    gdata = """cmd = {
  'linux' : {
    'cwd'     : '$HOME/.beam/beam-vlab/auxdata/librat_scenes',
    'exe'     : '$HOME/.beam/beam-vlab/auxdata/librat_lin64/src/start/ratstart',
    'cmdline' : ['-RATv', '-m', '%s', '-RATsensor_wavebands', '$HOME/.beam/beam-vlab/auxdata/librat_scenes/%s', '$HOME/.beam/beam-vlab/auxdata/librat_scenes/%s' ],
    'stdin'   : '%s',
    'stdout'  : '%s',
    'stderr'  : '%s',
    'env'     : {
      'BPMS'  : '$HOME/.beam/beam-vlab/auxdata/librat_lin64/',
  'LD_LIBRARY_PATH' :  '$HOME/.beam/beam-vlab/auxdata/librat_lin64/src/lib',
    }},
  'windows'   : {
    'cwd'     : '%HOMEDRIVE%%HOMEPATH%/.beam/beam-vlab/auxdata/librat_scenes',
    'exe'     : '%HOMEDRIVE%%HOMEPATH%/.beam/beam-vlab/auxdata/librat_win32/src/start/ratstart.exe',
    'cmdline' : ['-RATv', '-m', '%s', '-RATsensor_wavebands', '%HOMEDRIVE%%HOMEPATH%/.beam/beam-vlab/auxdata/librat_scenes/%s', '%HOMEDRIVE%%HOMEPATH%/.beam/beam-vlab/auxdata/librat_scenes/%s' ],
    'stdin'   : '%s',
    'stdout'  : '%s',
    'stderr'  : '%s',
    'env'     : {
      'BPMS'  : '%HOMEDRIVE%%HOMEPATH%/.beam/beam-vlab/auxdata/librat_win32'
   }}
}
"""
    # hack to allow replacing only %s
    escaped = gdata.replace("%%","\x81\x81").replace("%H","\x81H").replace("%/","\x81/")
    replaced = escaped % \
   (args['sorder'], args['wbfile'], args['objfile'], gFilePath+'.inp', gFilePath+'.out.log', gFilePath+'.err.log', \
    args['sorder'], args['wbfile'], args['objfile'], gFilePath+'.inp', gFilePath+'.out.log', gFilePath+'.err.log')
    gdata = replaced.replace("\x81", "%")
    gdata += 'global grabme_retval\n'
    gdata += 'grabme_retval = VLAB.doExec(cmd)\n'
    try:
      fp = open(gFilePath, 'w')
      fp.write(gdata)
    finally:
      fp.close()

  def main(self, args):
    me=self.__class__.__name__ +'::'+VLAB.me()
    VLAB.logger.info('======> %s' % me)
    for a in args:
      VLAB.logger.info("%s -> %s" % (a, args[a]))

    # set up defaults
    q = {
      'INFINITY'        : 1000000,
      'lightfile'       : 'light.dat',
      'camfile'         : 'camera.dat',
      'wbfile'          : 'wb.test.dat',
      'anglefile'       : 'angles.dat',
      'objfile'         : 'veglab_test.obj',

      'blacksky'        : '',
      'npixels'         : 1000000,
      'image'           : 1,
      'rpp'             : 1,
      'fov'             : False,
      'sorder'          : 100,
      'nice'            : None,
      'boom'            : 100000,
      'ideal'           : False,
      'samplingPattern' : False,
      'mode'            : 'scattering order',
      'opdir'           : 'brdf',
      'result_root'     : 'result',
      'camera_root'     : 'camera',
      'light_root'      : 'light',
      'grabme_root'     : 'grabme',

      'look_xyz'        : (150, 150, 35),
      'location'        : False,
      'vz'              : -1,
      'va'              : -1,
      'sz'              : -1,
      'sa'              : -1,
    }
    for a in args:
      if a == 'look':
        q['look_xyz'] = args[a]
      elif a == 'result':
        q['result_root'] = args[a]
      elif a == 'camera':
        q['camera_root'] = args[a]
      elif a == 'light':
        q['light_root'] = args[a]
      elif a == 'grabme':
        q['grabme_root'] = args[a]
      elif a == 'wb':
        q['wbfile'] = args[a]
      elif a == 'angles':
        q['anglefile'] = args[a]
      elif a == 'obj':
        q['objfile'] = args[a]
      else:
        q[a] = args[a]

    VLAB.mkDirPath('%s/%s' %(LIBRAT.SDIR, q['opdir']))

    angfp = VLAB.checkFile('%s/%s' % (LIBRAT.SDIR, q['anglefile']))
    wbfp  = VLAB.checkFile('%s/%s' % (LIBRAT.SDIR, q['wbfile']))
    objfp = VLAB.checkFile('%s/%s' % (LIBRAT.SDIR, q['objfile']))

    # vz va sz sa
    ang = VLAB.valuesfromfile('%s/%s' % (LIBRAT.SDIR, q['anglefile']))

    if 'lookFile' in q:
      lookfp = VLAB.checkFile('%s/%s' % (LIBRAT.SDIR, q['lookFile']))
      q['look_xyz'] = VLAB.valuesfromfile('%s/%s' % (LIBRAT.SDIR, q['lookFile']))

    if len(q['look_xyz']) == 3:
      q['look_xyz'] = ((q['look_xyz']),)

    if len(ang) < 4 or (len(ang) > 4 and len(ang[0]) != 4):
      VLAB.logger.info("%s: wrong number of fields (%i) in %s - should be 4\n"%(me, len(ang[1]), q['anglefile']))
      raise Exception()

    if len(ang) == 4:
      ang = ((ang),)

    for n, a in enumerate(ang):
      q['vz'] = a[0]
      q['va'] = a[1]
      q['sz'] = a[2]
      q['sa'] = a[3]

      for ll, look in enumerate(q['look_xyz']):
        lightfile = VLAB.fPath('%s/%s' % (LIBRAT.SDIR, q['opdir']), q['light_root'] + '_sz_' + str(q['sz']) + '_sa_' + str(q['sa']) + '_dat')
        ligfp = VLAB.openFileIfNotExists(lightfile)
        if ligfp != None:
          nq = {
            'sz' : q['sz'],
            'sa' : q['sa'],
          }
          self._writeLightFile(lightfile, nq)

        rooty = q['objfile'] + '_vz_' + str(q['vz']) + '_va_' + str(q['va']) + '_sz_' + str(q['sz']) + '_sa_' + str(q['sa']) + '_xyz_' + str(look[0]) + '_' + str(look[1]) + '_' + str(look[2]) + '_wb_' + q['wbfile']
        grabme = VLAB.fPath('%s/%s' % (LIBRAT.SDIR, q['opdir']), q['grabme_root'] + '.' + rooty)
        if 'dhp' in q:
          location = list(look)
          look[2] = q['INFINITY']
          sampling = 'circular'

        if not VLAB.fileExists(grabme):
          grabfp = VLAB.openFileIfNotExists(grabme)
          q['grabme_log'] = grabme + '.log'
          q['camfile'] = VLAB.fPath('%s/%s' % (LIBRAT.SDIR, q['opdir']), q['camera_root'] + '.' + rooty)
          q['oproot'] = VLAB.fPath('%s/%s' % (LIBRAT.SDIR, q['opdir']), q['result_root'] + '.' + rooty)
          nq = {
            'name'             : 'simple camera',
            'vz'               : q['vz'],
            'va'               : q['va'],
            'integral'         : q['oproot'],
            'integral_mode'    : q['mode'],
            'npixels'          : q['npixels'],
            'rpp'              : q['rpp'],
            'boom'             : q['boom'],
            'ideal'            : q['ideal'],
            'look_xyz'         : look,
            'location'         : q['location'],
            'fov'              : q['fov'],
            'samplingPattern'  : q['samplingPattern'],
            'file'             : q['camfile'],
            'grabme_log'       : q['grabme_log'],
            'camfile'          : q['camfile']
          }
          if 'image' in q:
            if 'hips' in q:
              nq['imfile'] = q['oproot'] + '.hips'
            else:
              nq['imfile'] = q['oproot'] + '.bim'
          else:
            nq['imfile'] = 'image'
          self._writeCamFile(nq['camfile'], nq)
          self._writeInputFile(grabme + '.inp', lightfile, nq['camfile'])
          nq = {
            'blacksky' : q['blacksky'],
            'sorder'   : q['sorder'],
            'objfile'  : q['objfile'],
            'wbfile'   : q['wbfile']
          }
          self._writeGrabFile(grabme, nq)
          global grabme_retval
          grabme_retval = 0
          globdict = globals()
          execfile(grabme, globdict)
          if grabme_retval != 0:
            raise Exception("grabme failed with return code=%d" % grabme_retval)

          # move resulting .hdr and result.image
          hdrFile = None
          imgFile = None
          for f in VLAB.listdir(LIBRAT.SDIR):
            if f.endswith(".hdr"):
              hdrFile = f
            elif f.endswith("result.image"):
              imgFile = f
          if hdrFile != None:
            VLAB.renameFile(LIBRAT.SDIR + "/" + hdrFile, grabme + '.hdr')
          if imgFile != None:
            VLAB.renameFile(LIBRAT.SDIR + "/" + imgFile, grabme + '.img')
    VLAB.logger.info('Done')

#############################################################################

class Librat_dolibradtran:

  def main(self, q):
    # initial arguments for doLibradtran
    r = {
      'CO2'      : q[VLAB.P_AtmosphereCO2],
      'H2O'      : q[VLAB.P_AtmosphereWater],
      'O3'       : q[VLAB.P_AtmosphereOzone],
      'scene'    : q[VLAB.P_3dScene],
      'aerosol'  : q[VLAB.P_AtmosphereAerosol],
      'sensor'   : q[VLAB.P_Sensor],
      'rpv_file' : VLAB.path.join(LIBRAT.SDIR, q['rpv'])
    }

    VLAB.mkDirPath('%s/%s' % (LIBRAT.SDIR, q['opdir']))
    angfp = VLAB.checkFile('%s/%s' % (LIBRAT.SDIR, q['angfile']))
    wbfp = VLAB.checkFile('%s/%s' % (LIBRAT.SDIR, q['wbfile']))
    rpvfp = VLAB.checkFile(r['rpv_file'])

    rpv = VLAB.valuesfromfile(r['rpv_file'])
    if len(rpv[0]) != 4: # length of index 1 because index 0 is heading
      VLAB.logger.info("%s: rpv file %s wrong no. of cols (should be 4: lambda (nm), rho0, k, theta\n" % (sys.argv[0], rpv_file))
      raise Exception()

    angt = VLAB.valuesfromfile('%s/%s' % (LIBRAT.SDIR, q['angfile']))
    wb = [i[1] for i in VLAB.valuesfromfile('%s/%s' % (LIBRAT.SDIR, q['wbfile']))]

    nbands = len(wb)
    wbstep = 1
    if q['v']:
      VLAB.logger.info('%s: wbmin = %i, wbmax = %i, wbstep = %i\n'%(sys.argv[0],min(wb),max(wb),wbstep))

    if q['v']:
      # only do all angles if time not specified, if time specified use that to get sza and phi0
      if q['lat'] and ['lon'] and ['time']:
        VLAB.logger.info("%s: doing lat lon time, not using sun angles in file %s\n" % (sys.argv[0], q['anglefile']))

    # check for op file if required
    if not VLAB.fileExists('%s/%s' % (LIBRAT.SDIR, q['plotfile'])):
      VLAB.logger.info('%s/%s' % (LIBRAT.SDIR, q['plotfile']))
      plotfilefp = VLAB.openFileIfNotExists('%s/%s' % (LIBRAT.SDIR, q['plotfile']))
    else:
      VLAB.logger.info('plotfile %s already exists - move/delete and re-run\n'%(q['plotfile']))
      raise Exception('plotfile %s already exists - move/delete and re-run\n'%(q['plotfile']))

    # loop over angles and do all wb at once for each angle
    for a, aa in enumerate(angt):
      # need special case for 1 angle only, in which case angt = 4
      if len(angt) == 1:
        vzz = angt[0][0]
        vaa = angt[0][1]
        szz = angt[0][2]
        saa = angt[0][3]
      else:
        # sz, saz generated by user-specified dates and times, lat, lon if that option given
        # AND: need to check angles that we are absolute i.e. no -ves
        vzz = angt[a][0]
        vaa = angt[a][1]
        szz = angt[a][2]
        saa = angt[a][3]

      VLAB.logger.info(str(vzz))
      umu = math.cos(vzz)
      angstr = str(vzz) + '_' + str(vaa) + '_' + str(szz) + '_' + str(saa)

      libradtran_ip = VLAB.fPath(LIBRAT.SDIR, q['root'] + '.ip.' + q['wbfile'] + '_' + angstr)
      libradtran_op = VLAB.fPath(LIBRAT.SDIR, q['root'] + '.op.' + q['wbfile'] + '_' + angstr)

      if q['v']:
        VLAB.logger.info('doing ip file %s\n'%(libradtran_ip))
        #sort out zen/azimuth angles i.e. if vz is -ve
      if vzz < 0:
        # doesn't matter as we use umu from above anyway but ...
        vzz *= -1.
      if vaa < 0:
        vaa = 180. - vaa
      if szz < 0:
        szz *= -1.
      if saa < 0:
        saa = 180. - saa

      # add view angles
      def valueorlisttostring(val):
        try:
          return ' '.join(map(str, val))
        except TypeError:
          return str(val)

      r['umu'] = valueorlisttostring(umu)
      r['phi'] = valueorlisttostring(vaa)

      # add sz angles
      if q['lat'] and q['lon'] and q['time']:
        r['latitude'] = q['lat']
        r['longitude'] = q['lon']
        r['time'] = q['time']
      else:
        # print out sun angles
        r['sza'] = valueorlisttostring(szz)
        r['phi0'] = valueorlisttostring(saa)

      # write out wavelengths i.e. min and max. Step is determined by step in solar file i.e. 1nm default
      r['wavelength'] = str(int(min(wb))) + ' ' + str(int(max(wb)))
      # run the libradtran command
      r['infile']  = libradtran_ip
      r['outfile'] = libradtran_op
      for k,v in r.items():
        VLAB.logger.info("  [%s] => %s" % (k, v))
      VLAB.doLibradtran(r)

      # now check if a single angle (i.e. angt.size == 4 ) and if so, break out of loop
      if 4 == len(angt) * len(angt[0]) or (q['lat'] and q['lon'] and q['time']): break

      # finish angle loop & srt out collating results into LUT file at end if required
      # write header line i.e. vz va sz sa wb_min -> wb_max
      plotfilefp.write('# vz va sz sa %e %e %e\n' % (min(wb), max(wb), wbstep))
      # plotfilefp.flush()

      for f in [f for f in VLAB.listdir('%s/%s' % (LIBRAT.SDIR, q['opdir'])) if f.startswith('op.')]:
        vzz = f.split('_')[-4]
        vaa = f.split('_')[-3]
        szz = f.split('_')[-2]
        saa = f.split('_')[-1]
        d = VLAB.valuesfromfile('%s/%s' % (LIBRAT.SDIR, f),transpose=True)
        plotfilefp.write('%s %s %s %s ' % (vzz,vaa,szz,saa))
        plotfilefp.write(' '.join(map(str, d[1])) + '\n')

      plotfilefp.flush()
      plotfilefp.close()

#############################################################################
class Librat_drivers:
  """ setup the scene"""
  def main(self, args):
    me=self.__class__.__name__ +'::'+VLAB.me()

    # initialize with defaults

    # sun angles for eg UK (lat 51' 0" 0' 0") 1 Jun 2013 10:30 am
    # sun_position -lat 51 -lon 0 -date 01:05:2013 -t 10:30:00
    # va, sz, sa = 0, 34, 141
    q = {
            'vz' : 0,
            'va' : 0,
            'sz' : 34,
            'sa' : 141,
      'nsamples' : 1000,
         'xdims' : (0, 300, 30),
         'ydims' : (0, 300, 30),
             'z' : 0,
       'angFile' : 'angles.dat',
      'lookFile' : 'look.dat',
    }

    # fill in: lookFile, angFile, xdums, ydims, z, sz, sa, nsamples...
    for a in args:
      if a == 'angles':
        q['angFile']  = args[a]
      elif a == 'look':
        q['lookFile'] = args[a]
      elif a == 'n':
        q['nsamples'] = args[a]
      else:
        q[a] = args[a]

    if 'msi' in q:
      # across whole swath
      # zmin, vzmax, vzstep = -22, 54, 4
      q['angles'] = (0, 0, 0, 0)
      q['angles'] = (q['vz'], q['va'], q['sz'], q['sa'])
    elif 'olci' in q:
      q['vzmin'], q['vzmax'], q['vzstep'] = -22, 54, 4
      q['vzz'] = VLAB.frange(q['vzmin'], q['vzmax']+q['vzstep'], q['vzstep'])
      q['angles'] = [[0. for col in range(4)] for row in range(len(q['vzz']))]
      q['angles'][:,0] = q['vzz']
      q['angles'][:,1] = q['vz']
      q['angles'][:,2] = q['sz']
      q['angles'][:,3] = q['sa']
    elif 'around' in q:
      q['vamin'], q['vamax'], q['vastep'] =  0, 360, 10
      q['vaa'] = VLAB.frange(q['vamin'], q['vamax']+q['vastep'], q['vastep'])
      q['vz'], q['sz'], q['sa'] = 70., 30, 90
      q['angles'] = [[0. for col in range(4)] for row in range(len(q['vaa']))]
      q['angles'][:,0] = q['vz']
      q['angles'][:,1] = q['vaa']
      q['angles'][:,2] = q['sz']
      q['angles'][:,3] = q['sa']
    elif 'multiple' in q:
      # this one for multiple vz, va angles
      q['vzmin'], q['vzmax'], q['vzstep'] = -70,  70, 10
      q['vamin'], q['vamax'], q['vastep'] =   0, 340, 20
      q['vzz'] = VLAB.frange(q['vzmin'], q['vzmax']+q['vzstep'], q['vzstep'])
      q['vaa'] = VLAB.frange(q['vamin'], q['vamax']+q['vastep'], q['vastep'])

      q['angles'] = [[0. for col in range(4)] for row in range(len(q['vzz'])*len(q['vzz']))]

      for n, va in enumerate(q['vaa']):
        q['angles'][n*len(q['vzz']):(n+1)*len(q['vzz']),0] = q['vzz']
        q['angles'][n*len(q['vzz']):(n+1)*len(q['vzz']),1] = q['vz']
        q['angles'][n*len(q['vzz']):(n+1)*len(q['vzz']),2] = q['sz']
        q['angles'][n*len(q['vzz']):(n+1)*len(q['vzz']),3] = q['sa']
    elif 'random' in q:
      # random n samples of COSINE-WEIGHTED view and illum angles
      # In order that we get the required number, nsamples,  AND can disregard all those with
      # vz > 70 and vz < -70 (not valid for RPV) do twice as many as you need, discard
      # all those outside the angle range and then take the first n.
      nn = q['nsamples']*2

      if VLAB.CONF_RND_REPRODUCE:
        rState = VLAB.rndInit(17)
      else:
        rState = VLAB.rndInit()

      # view angles first
      u1    = [VLAB.rndNextFloat(rState) for i in range(nn)]
      r     = [math.sqrt(i)        for x in u1]
      theta = [2.*math.pi*x for x in [VLAB.rndNextFloat(rState) for i in range(nn)]]


      x  = [r[i] * math.cos(theta[i]) for i in range(nn)]
      y  = [r[i] * math.sin(theta[i]) for i in range(nn)]
      z  = [math.sqrt(1 - u1[i])      for i in range(nn)]

      q['vz'] = [math.acos(z[i])      for i in range(nn)]
      q['va'] = [math.atan(y[i]/x[i]) for i in range(nn)]

      # if x -ve then vz -ve
      for i in range(nn):
        if (x[i]<0):
          q['vz'][i] = q['vz'][i] * -1.

      # sun angles
      u1    = [VLAB.rndNextFloat(rState) for i in range(nn)]
      r     = [math.sqrt(i)              for x in u1]
      theta = [2.*math.pi*x for x in [VLAB.rndNextFloat(rState) for i in range(nn)]]

      x  = [r[i] * math.cos(theta[i]) for i in range(nn)]
      y  = [r[i] * math.sin(theta[i]) for i in range(nn)]
      z  = [math.sqrt(1 - u1[i])      for i in range(nn)]

      #np.savetxt('rpv.angles.test.plot',np.transpose([x,y,z]),fmt='%.6f')
      q['sz'] = [math.acos(z[i])      for i in range(nn)]
      q['sa'] = [math.atan(y[i]/x[i]) for i in range(nn)]

      # if x -ve then sz -ve
      for i in range(nn):
        if (x[i]<0):
          q['sz'][i] = q['sz'][i] * -1.

      vzdeg = [VLAB.r2d(q['vz'][i]) for i in range(nn)]
      vadeg = [VLAB.r2d(q['va'][i]) for i in range(nn)]
      szdeg = [VLAB.r2d(q['sz'][i]) for i in range(nn)]
      sadeg = [VLAB.r2d(q['sa'][i]) for i in range(nn)]
      # zip does a transpose
      angles = zip(vzdeg, vadeg, szdeg, sadeg)

      angles2 = list()
      for row in angles:
        if (row[0] > -70.) and (row[0] <= 70.) and (row[2] > -70.) and (row[2] <= 70.):
          angles2.append(row)

      # now take the first n
      q['angles'] = angles2[0:q['nsamples']]

      # x = np.sin(np.deg2rad(angles[:,0])) * np.cos(np.deg2rad(angles[:,1]))
      # y = np.sin(np.deg2rad(angles[:,0])) * np.sin(np.deg2rad(angles[:,1]))
      # z = np.cos(np.deg2rad(angles[:,0]))

      #np.savetxt('rpv.angles.test',angles,fmt='%.6f')
      #np.savetxt('rpv.angles.test.plot',np.transpose([x,y,z]),fmt='%.6f')
    else:
      # default
      q['vzmin'], q['vzmax'], q['vzstep'] = -70, 70, 5
      q['vzz'] = VLAB.frange(q['vzmin'],q['vzmax']+q['vzstep'],q['vzstep'])
      q['angles'] = [[0. for col in range(4)] for row in range(len(q['vzz']))]
      q['angles'][:,0] = q['vzz']
      q['angles'][:,1] = q['va']
      q['angles'][:,2] = q['sz']
      q['angles'][:,3] = q['sa']

    VLAB.savetxt(q['angFile'], q['angles'], fmt='%.1f')

    if 'lookFile' in q:
      x = VLAB.frange(q['xdims'][0],q['xdims'][1],q['xdims'][2])
      y = VLAB.frange(q['ydims'][0],q['ydims'][1],q['ydims'][2])
      looktrans = [[0. for col in range(len(x)*len(y))] for row in range(3)]
      for n, yy in enumerate(y):
        looktrans[0][n*len(x):(n+1)*len(x)] = x
        looktrans[1][n*len(x):(n+1)*len(x)] = [yy for i in range(len(y))]
        looktrans[2][n*len(x):(n+1)*len(x)] = [0. for i in range(len(x))]
      # zip does a transpose
      look = zip(*looktrans)
      VLAB.savetxt(q['lookFile'],look,fmt='%.1f')

#############################################################################
class Librat_plot:
  """plot results"""
  def main(self, args):
    me=self.__class__.__name__ +'::'+VLAB.me()
    VLAB.logger.info('======> %s' % me )
    for a in args:
      VLAB.logger.info("%s -> %s" % (a, args[a]))

    q = {
         'spec' : 'SPECTRAL_TEST/result.laegeren.obj_vz_0.0_va_0.0_sz_34.0_sa_141.0_xyz_150.0_150.0_700.0_wb_wb.full_spectrum.dat.direct',
       'wbfile' : 'wb.full_spectrum.dat',
         'root' : 'OLCI_brdf.scene/result.laegeren.obj',
         'spec' : False,
         'brdf' : True
    }

    for a in args:
      if a == 'angles':
        q['angfile'] = args[a]
      else:
        q[a] = args[a]

    if q['spec']:
      self.spec_plot(q['spec'], q['wbfile'])

    if q['brdf']:
      self.brdf_plot(q['root'], q['angfile'], q['wbfile'])

  def spec_plot(self,spec,wbspec):
    wbspec_contents = VLAB.valuesfromfile('%s/%s' % (LIBRAT.SDIR, wbspec), transpose=True)

    wb = wbspec_contents[1];
    op1 = spec + '.plot.png'

    data = wbspec_contents
    refl = data[1:,].sum(axis=1)
    # TODO Implement rest of function
    raise Exception("spec_plot()")
  def brdf_plot(self,root,angfile,wbfile):
    opdat = LIBRAT.SDIR + '/' + root + '.brdf.dat'
    opplot = LIBRAT.SDIR + '/' + root + '.brdf.png'
    ang = VLAB.valuesfromfile('%s/%s' % (LIBRAT.SDIR, angfile), transpose=True)
    wb = VLAB.valuesfromfile('%s/%s' % (LIBRAT.SDIR, wbfile), transpose=True)[1]

    result = [[0. for i in range(len(wb))] for i in range(len(ang[0]))]

    ff = [root.split('/')[0] + '/' + f for f in VLAB.listdir(root.split('/')[0])
          if f.endswith('.direct') and f.startswith(root.split('/')[1])]
    for f in ff:
      fsplit = f.split('_')
      vz = f.split('_')[fsplit.index('vz') + 1]
      va = f.split('_')[fsplit.index('va') + 1]
      sz = f.split('_')[fsplit.index('sz') + 1]
      sa = f.split('_')[fsplit.index('sa') + 1]

      data = VLAB.valuesfromfile('%s/%s' % (LIBRAT.SDIR, f), transpose=True)
      refl = [reduce(lambda x, y : x + y, i) for i in data[1:]]
      result[zip(*VLAB.awhere(
        VLAB.treemap(lambda x : x == float(vz), ang)))[1][0]] = refl
      # TODO test and cleanup (brdf_plot)
      # coords = VLAB.treemap(lambda x : x == float(vz), ang[0])
      # coords = map(lambda x, y : x & y, coords,
      #              VLAB.treemap(lambda x : x == float(va), ang[1]))
      # coords = map(lambda x, y : x & y, coords,
      #              VLAB.treemap(lambda x : x == float(sz), ang[2]))
      # coords = map(lambda x, y : x & y, coords,
      #              VLAB.treemap(lambda x : x == float(sa), ang[3]))
      coords = VLAB.makemaskeq(ang[0], float(vz))
      coords = VLAB.maskand(coords, VLAB.makemaskeq(ang[1], float(va)))
      coords = VLAB.maskand(coords, VLAB.makemaskeq(ang[2], float(sz)))
      coords = VLAB.maskand(coords, VLAB.makemaskeq(ang[3], float(sa)))
      coords = VLAB.awhere(coords)
      result[coords[0][0]] = refl
    dataset = VLAB.make_dataset()
    # was 3 and 7 - but 7 can be out of bounds
    for b in [1, 3]:
      VLAB.plot(dataset, ang[0], [i[b] for i in result],
           "waveband: %.1f" % wb [b])
    chart = VLAB.make_chart("band %d" % (b), "view zenith angle (deg.)",
                            u"\u03A1", dataset)
    VLAB.logger.info('%s: plotting brdf to: %s\n'%(sys.argv[0], opplot))
    VLAB.logger.info('%s: saving brdf data to: %s\n'%(sys.argv[0], opdat))
    outdata = [[0. for i in xrange(len(result[0]) + len(ang))]
               for j in xrange(len(result))]
    VLAB.replacerectinarray(outdata, zip(*ang), 0, 0, len(result), len(ang))
    # FIXME: assign result instead of zip(*ang) (see plot.py:88)
    VLAB.replacerectinarray(outdata, result, 0, len(ang), len(result), len(result[0]) + len(ang))
    VLAB.savetxt(opdat, outdata, fmt='%.4f')
    VLAB.save_chart(chart, opplot)

class Librat_rpv_invert:
  """rpv inversion for integration with libmodtran"""
  def main(self, args):
    me=self.__class__.__name__ +'::'+VLAB.me()
    VLAB.logger.info('======> %s' % me)
    for a in args:
      VLAB.logger.info("%s -> %s" % (a, args[a]))

    # defaults
    q = {
	'dataf' : 'rpv.rami.2/result.HET01_DIS_UNI_NIR_20.obj.brdf.dat',
	'wbfile' : 'wb.MSI.dat',
	'wbNum' : 3, # 665 nm in this case
	'verbose' : 1,
	'plot' : 1,
	'show' : 0
    }

    for a in args:
      if a == 'wb':
        q['wbfile'] = args[a]
      else:
        q[a] = args[a]

    # Set output folder
    if "outputFolder" in q.keys():
      outputFolder = q['outputFolder']
    else:
      outputFolder = LIBRAT.SDIR
      q['wbfile'] = "%s/%s" % (outputFolder, q['wbfile'])

    wb   = VLAB.valuesfromfile(q['wbfile'], transpose=True)[1]
    data = VLAB.valuesfromfile('%s/%s' % (outputFolder, q['dataf']),  transpose=True)

    # check shape of 2 data files i.e. that there are same no. of wbs on each line of datafile ( + 4 angles)
    if len(wb) != len(data) - 4:
      VLAB.logger.info('%s: no of wavebands different in brdf file %s and wb file %s\n'%(sys.argv[0],q['dataf'],q['wbfile']))
      raise Exception('%s: no of wavebands different in brdf file %s and wb file %s\n'%(sys.argv[0],q['dataf'],q['wbfile']))

    rho0, k, bigtet, rhoc = 0.03, 1.2, 0.1, 0.2

    if q['three']:
      params = [rho0, k, bigtet]
    else:
      params = [rho0, k, bigtet, rhoc]

    if args['paramfile']:
      opdat = args['paramfile']
    else:
      opdat = q['dataf'] + '.params.dat'

    if q['verbose']: VLAB.logger.info('%s: saving params to %s\n'%(sys.argv[0], opdat))

    # create the file if it doesn't exist
    dfp = VLAB.openFileIfNotExists('%s/%s' % (outputFolder, opdat))
    if dfp != None:
      dfp.close()

    # open the previously created file
    opfp = open('%s/%s' % (outputFolder,  opdat), 'w')

    if q['three']:
      opfp.write('# wb rho0 k bigtet\n')
    else:
      opfp.write('# wb rho0 k bigtet rhoc\n')

    ymin, ymax = (0, 0.25)
    xmin, xmax = (-75., 75)

    for wbNum, band in enumerate(wb):
      if q['verbose']: VLAB.logger.info('%s: doing band %i (%f)\n'%(sys.argv[0], wbNum, band))

      invdata = [[0. for i in xrange(len(data))] for i in xrange(5)]
      invdata[0:4] = data[0:4]
      invdata[4] = data[4 + q['wbNum']]

      # invdata = [[0. for i in xrange(15)] for i in xrange(5)]
      # invdata[0:4] = [i[0:15] for i in data[0:4]]
      # invdata[4] = data[4 + q['wbNum']][0:15]

      porig = params
      p_est = params
      p_est = VLAB.Minimize_minimize(self.obj, params, args=(invdata,))[0]
      if q['three']:
        p_est = VLAB.min_l_bfgs_b(self.obj, p_est, args=(invdata,), bounds=((0., None), (0., None), (None, None)))
      else:
        p_est = VLAB.min_l_bfgs_b(self.obj, p_est, args=(invdata,), bounds=((0., None), (0., None),(None, None), (None, None)))
      r = self.rpv(p_est, invdata)
      rmse = math.sqrt(reduce(lambda x, y : x + y, map(lambda x : x ** 2, VLAB.suba(r, invdata[4]))))
      if q['three']:
        opfp.write('%.1f %.8f %.8f %.8f\n' % (band, p_est[0], p_est[1], p_est[2]))
      else:
        opfp.write('%.1f %.8f %.8f %.8f %.8f\n' % (band, p_est[0], p_est[1], p_est[2], p_est[3]))
      if q['plot']:
        if q['plotfile']:
          opplot = VLAB.path.join(outputFolder, q['plotfile'] + '.inv.wb.' + str(wbNum) + '.png')
        else:
          opplot = VLAB.path.join(outputFolder, q['dataf'] + '.inv.wb.' + str(wbNum) + '.png')

        if q['verbose']: VLAB.logger.info('%s: plotting to %s\n' % (sys.argv[0], opplot))

        dataset = VLAB.make_dataset()
        VLAB.plot(dataset, invdata[0], invdata[4], "original")
        VLAB.plot(dataset, invdata[0], r, "inverted")
        chart = VLAB.make_chart("band %i (%f)" % (wbNum, band), "vza (deg)", u"\u03A1", dataset)
        dataset = None
        VLAB.save_chart(chart, opplot)
        chart = None
        # TODO test plot code
    opfp.close()
  def obj(self, p, x):
    fwd = self.rpv(p, x)
    obs = x[4]
    sse = reduce(lambda x, y : x + y,
                 map(lambda x : x ** 2,
                     VLAB.suba(obs, fwd)))
    return sse
  def rpv(self, params, data):
    if len(params) == 4:
      rho0, k, bigtet, rhoc = params
    else:
      rhoc = 1
      rho0, k, bigtet = params
    cosv = VLAB.cosa(data[0])
    coss = VLAB.fabsa(VLAB.cosa(data[2]))
    cosv = VLAB.replaceinarray(cosv, lambda x : x == 0, 1e-20)
    coss = VLAB.replaceinarray(coss, lambda x : x == 0, 1e-20)
    sins = VLAB.sqrta(map(lambda x : 1. - x ** 2, coss))
    sinv = VLAB.sqrta(map(lambda x : 1. - x ** 2, cosv))
    relphi = VLAB.suba(map(VLAB.d2r, data[1]),
                       map(VLAB.d2r, data[3]))
    relphi = map(lambda x : {True : 2 * math.pi - x, False : x}
                 [x > math.pi], relphi)
    cosp = map(lambda x : -1. * x, VLAB.cosa(relphi))
    tans = VLAB.diva(sins, coss)
    tanv = VLAB.diva(sinv, cosv)
    csmllg = VLAB.adda(VLAB.mula(coss, cosv),
                       VLAB.mula(VLAB.mula(sins, sinv), cosp))
    bigg = VLAB.sqrta(
      VLAB.suba(
        VLAB.adda(map(lambda x : x ** 2, tans), map(lambda x : x ** 2, tanv)),
        VLAB.mula(VLAB.mula(map(lambda x : x * 2.0, tans), tanv), cosp)))
    bgthsq = bigtet ** 2
    expon = k - 1.0
    if expon != 0.0:
      f1 = VLAB.mula(VLAB.powa(VLAB.mula(coss, cosv), expon),
                     VLAB.powa(VLAB.adda(coss, cosv), expon))
    else:
      fi = [1. for i in coss]
    denom = VLAB.powa(map(lambda x : 1. + bgthsq + 2. * bigtet * x, csmllg),
                      1.5)
    f2 = list(denom)
    f2 = map(lambda x : {True : (lambda : (1.0 - bgthsq) * 1e20),
                         False : (lambda : (1.0 - bgthsq) / x)}[x == 0.](), relphi)
    f3 = map(lambda x : 1.0 + (1 - rhoc) / (1. + x), bigg)
    return map(lambda x : rho0 * x, VLAB.mula(VLAB.mula(f1, f2), f3))

#############################################################################

class LIBRAT:
  if VLAB.osName().startswith('Windows'):
    SDIR=VLAB.expandEnv('%HOMEDRIVE%%HOMEPATH%/.beam/beam-vlab/auxdata/librat_scenes')
  else:
    SDIR=VLAB.expandEnv('$HOME/.beam/beam-vlab/auxdata/librat_scenes')

  """Integration glue for calling external LIBRAT programs"""
  def __init__(self):
    me=self.__class__.__name__ +'::'+VLAB.me()
    VLAB.logger.info('%s: constructor completed...' % me)

  def doProcessingTests(self, pm, args):
 
    """do processing tests for LIBRAT processor"""
    me=self.__class__.__name__ +'::'+VLAB.me()

    if (pm != None):
      pm.beginTask("Computing...", 10)
    # ensure at least 1 second to ensure progress popup feedback
    time.sleep(1)

    cmd = {
    'linux' : {
      'cwd'     : '$HOME/.beam/beam-vlab/auxdata/librat_lin64/src/start',
      'exe'     : '$HOME/.beam/beam-vlab/auxdata/librat_lin64/src/start/ratstart',
      'cmdline' : [
        '-sensor_wavebands', 'wavebands.dat', '-m', '100',
        '-sun_position', '0', '0', '10', 'test.obj'],
      'stdin'   : '$HOME/.beam/beam-vlab/auxdata/librat_lin64/src/start/starttest.ip',
      'stdout'  : None,
      'stderr'  : None,
      'env'     : {
        'LD_LIBRARY_PATH' : '$HOME/.beam/beam-vlab/auxdata/librat_lin64/src/lib/',
        'BPMS'  : '$HOME/.beam/beam-vlab/auxdata/librat_lin64/'
      }},
    'windows'   : {
      'cwd'     : '%HOMEDRIVE%%HOMEPATH%/.beam/beam-vlab/auxdata/librat_windows/src/start',
      'exe'     : '%HOMEDRIVE%%HOMEPATH%/.beam/beam-vlab/auxdata/librat_windows/src/start/ratstart.exe',
      'cmdline' : [
        '-sensor_wavebands', 'wavebands.dat', '-m', '100',
        '-sun_position', '0', '0', '10', 'test.obj'],
      'stdin'   : '%HOMEDRIVE%%HOMEPATH%/.beam/beam-vlab/auxdata/librat_windows/src/start/starttest.ip',
      'stdout'  : None,
      'stderr'  : None,
      'env'     : {
        'BPMS'  : '%HOMEDRIVE%%HOMEPATH%/.beam/beam-vlab/auxdata/librat_windows'
     }}
    }
    exitCode = VLAB.doExec(cmd)
    if exitCode != 0:
      raise Exception("librat-start failed with return code=%d" % exitCode)

    #
    # see https://github.com/netceteragroup/esa-beam/blob/master/beam-3dveglab-vlab/src/main/scenes/librat_scenes/libradtran.README
    #
    drivers      = Librat_drivers()
    dobrdf       = Librat_dobrdf()
    plot         = Librat_plot()
    rpv_invert   = Librat_rpv_invert()
    dolibradtran = Librat_dolibradtran()

    args = {
       'random' : True,
       'n'      : 1000,
       'angles' : 'angles.rpv.2.dat',
    }
    # drivers.main(args)

    # RAMI test case
    args = {
            'v' : True,
         'nice' : 19,
          'obj' : 'HET01_DIS_UNI_NIR_20.obj',
         'hips' : True,
           'wb' : 'wb.MSI.dat',
        'ideal' : (300., 300.),
         'look' : (150., 150., 710.),
          'rpp' : 4,
      'npixels' : 10000,
         'boom' : 786000,
       'angles' : 'angles.rpv.2.dat',
        'opdir' : 'rpv.rami'
    }
    # dobrdf.main(args)

    # LAEGEREN test case
    args = {
            'v' : True,
         'nice' : 19,
          'obj' : 'laegeren.obj.lai.1',
         'hips' : True,
           'wb' : 'wb.MSI.dat',
        'ideal' : (300., 300.),
         'look' : (150., 150., 710.),
          'rpp' : 4,
      'npixels' : 10000,
         'boom' : 786000 ,
       'angles' : 'angles.rpv.2.dat',
        'opdir' : 'rpv.laegeren'
    }
    # dobrdf.main(args)

    # FULL SPECTRUM RAMI test case
    args = {
            'v' : True,
         'nice' : 19,
          'obj' : 'HET01_DIS_UNI_NIR_20.obj',
           'wb' : 'wb.full_spectrum.1nm.dat',
        'ideal' : (80., 80.),
         'look' : (0., 0., 0.),
          'rpp' : 4,
      'npixels' : 10000,
         'boom' : 786000,
       'angles' : 'angle.rpv.cosDOM.dat',
        'opdir' : 'dart.rpv.rami'
    }
    # dobrdf.main(args)

    # FULL SPECTRUM LAEGEREN test case
    args = {
            'v' : True,
         'nice' : 19,
          'obj' : 'laegeren.obj.lai.1',
           'wb' : 'wb.full_spectrum.1nm.dat',
        'ideal' : (300., 300),
         'look' : (150., 150., 710),
          'rpp' : 4,
      'npixels' : 10000,
         'boom' : 786000,
       'angles' : 'angle.rpv.cosDOM.dat',
        'opdir' : 'dart.rpv.laegeren'
    }
    # dobrdf.main(args)

    args = {
         'brdf' : True,
       'angles' : 'angles.rpv.2.dat',
       'wbfile' : 'wb.MSI.dat',
        'bands' : (4, 7),
         'root' : 'rpv.rami/result.HET01_DIS_UNI_NIR_20.obj'
    }
    # plot.main(args)

    # RAMI
    args = {
         'brdf' : True,
       'angles' : 'angles.rpv.2.dat',
       'wbfile' : 'wb.MSI.dat',
         'root' : 'rpv.rami.2/result.HET01_DIS_UNI_NIR_20.obj',
        'bands' : (4, 7),
            'v' : True
    }
    # plot.main(args)

    # LAEGEREN
    args = {
         'brdf' : True,
       'angles' : 'angles.rpv.2.dat',
       'wbfile' : 'wb.MSI.dat',
         'root' : 'rpv.laegeren/result.laegeren.obj.lai.1',
        'bands' : (4, 7),
            'v' : True
    }
    # plot.main(args)

    # RAMI
    args = {
         'brdf' : True,
       'wbfile' : 'wb.full_spectrum.1nm.dat',
       'angles' : 'angle.rpv.cosDOM.dat',
         'root' : 'dart.rpv.rami/result.HET01_DIS_UNI_NIR_20.obj',
        'bands' : (250, 450),
            'v' : True
    }
    # plot.main(args)

    # RAMI
    args = {
        'three' : True,
            'v' : True,
         'plot' : True,
        'dataf' : 'rpv.rami.2/result.HET01_DIS_UNI_NIR_20.obj.brdf.dat',
    'paramfile' : 'rpv.rami.2/result.HET01_DIS_UNI_NIR_20.obj.brdf.dat.3params.dat',
     'plotfile' : 'rpv.rami.2/result.HET01_DIS_UNI_NIR_20.obj.brdf.3params',
    }
    # rpv_invert.main(args)

    # LAEGEREN
    args = {
        'three' : True,
            'v' : True,
         'plot' : True,
        'dataf' : 'rpv.laegeren/result.laegeren.obj.lai.1.brdf.dat',
    'paramfile' : 'rpv.laegeren/result.laegeren.obj.lai.1.brdf.dat.3params.dat',
     'plotfile' : 'rpv.laegeren/result.laegeren.obj.lai.1.brdf.3params'
    }
    # rpv_invert.main(args)

    args = {
        'three' : True,
            'v' : True,
         'plot' : True,
        'dataf' : 'dart.rpv.rami/result.HET01_DIS_UNI_NIR_20.obj.brdf.dat',
    'paramfile' : 'dart.rpv.rami/result.HET01_DIS_UNI_NIR_20.obj.brdf.dat.3params.dat',
     'plotfile' : 'dart.rpv.rami/result.HET01_DIS_UNI_NIR_20.obj.brdf.3params',
    }
    # rpv_invert.main(args)

    args = {
         'three': True,
            'v' : True,
         'plot' : True,
        'dataf' : 'dart.rpv.laegeren/result.laegeren.obj.lai.1.brdf.dat',
    'paramfile' : 'dart.rpv.laegeren/result.laegeren.obj.lai.1.brdf.dat.3params.dat',
     'plotfile' : 'dart.rpv.laegeren/result.laegeren.obj.lai.1.brdf.3params'
    }
    # rpv_invert.main(args)

    args = {
         'v' : True,
     'opdir' : 'rami.TOA',
    'angles' : 'angles.MSI.dat',
    'wbfile' : 'wb.MSI.dat',
       'rpv' : 'rpv.rami.2/result.HET01_DIS_UNI_NIR_20.obj.brdf.dat.3params.dat' ,
      'plot' : 'rami.TOA/rpv.rami.libradtran.dat.all'
    }
    # dolibradtran.main(args)

    args = {
         'v' : True,
     'opdir' : 'laegeren.TOA',
    'angles' : 'angles.MSI.dat',
    'wbfile' : 'wb.MSI.dat',
       'rpv' : 'rpv.laegeren/result.laegeren.obj.lai.1.brdf.dat.3params.dat',
      'plot' : 'laegeren.TOA/rpv.laegeren.libradtran.dat.all'
    }
    # dolibradtran.main(args)

    args = {
         'v' : True,
    'angles' : 'angle.rpv.cosDOM.dat',
    'wbfile' : 'wb.full_spectrum.1nm.dat',
     'opdir' : 'dart.rami.TOA',
       'rpv' : 'dart.rpv.rami/result.HET01_DIS_UNI_NIR_20.obj.brdf.dat.3params.dat',
      'plot' : 'dart.rami.TOA/rpv.rami.libradtran.dat.all'
    }
    # dolibradtran.main(args)

    args = {
          'v': True,
    'angles' : 'angle.rpv.cosDOM.dat',
    'wbfile' : 'wb.full_spectrum.1nm.dat',
     'opdir' : 'dart.laegeren.TOA',
       'rpv' : 'dart.rpv.laegeren/result.laegeren.obj.lai.1.brdf.dat.3params.dat',
      'plot' : 'dart.laegeren.TOA/rpv.laegeren.libradtran.dat.all'
    }
    # dolibradtran.main(args)

    args = {
          'v' : True,
      'opdir' : 'rami.TOA',
        'rpv' : 'rpv.laegeren/result.laegeren.obj.lai.1.brdf.dat.3params.dat',
       'plot' : 'rami.TOA/rpv.rami.libradtran.dat.all',
        'lat' : 50,
        'lon' : 0,
       'time' : '2013 0601 12 00 00'
    }
    # dolibradtran.main(args)

    args = {
          'v': True,
     'opdir' : 'laegeren.TOA.date',
       'rpv' : 'rpv.laegeren/result.laegeren.obj.lai.1.brdf.dat.3params.dat',
      'plot' : 'laegeren.TOA.date/rpv.laegeren.libradtran.dat.all',
       'lat' : 50,
       'lon' : 0,
      'time' : '2013 06 01 12 00 00'
    }
    # dolibradtran.main(args)


    # DHP Simulation
    args = {
         'v' : True,
      'nice' : 19,
       'obj' : 'laegeren.obj.lai.1',
      'hips' : True,
        'wb' : 'wb.image.dat',
       'dhp' : True,
'samplingPattern' : 'circular',
  'lookFile' : 'dhp.locations.ondem.dat',
    'angles' : 'angles.dhp.dat',
       'fov' : False,
       'rpp' : 8,
   'npixels' : 4000000,
     'opdir' : 'DHP_TEST'
    }
    # dobrdf.main(args)
    VLAB.logger.info('%s: Done...' % me)

  def doProcessing(self, pm, args):
    """do processing for LIBRAT processor"""
    me=self.__class__.__name__ +'::'+VLAB.me()

    VLAB.logger.info('%s: doProcessing()' % (me))
    # defaults
    q = {
       'angles' : 'angle.rpv.cosDOM.dat',
        'bands' : (250, 450),
         'boom' : 786000,
         'brdf' : True,
        'dataf' : 'dart.rpv.laegeren/result.laegeren.obj.lai.1.brdf.dat',
          'dhp' : True,
          'fov' : False,
         'hips' : False,
        'image' : True,
        'ideal' : (300., 300.),
          'lat' : 50,
          'lon' : 0,
         'look' : (150., 150., 710.),
     'lookFile' : 'dhp.locations.ondem.dat',
            'n' : 1000,
         'nice' : 19,
      'npixels' : 10000,
          'obj' : 'DEFAULT_OBJ',
        'opdir' : 'DEFAULT_DIR',
    'paramfile' : 'dart.rpv.rami/result.HET01_DIS_UNI_NIR_20.obj.brdf.dat.3params.dat',
         'plot' : 'dart.rami.TOA/rpv.rami.libradtran.dat.all',
     'plotfile' : 'rpv.rami.2/result.HET01_DIS_UNI_NIR_20.obj.brdf.3params',
         'plot' : 'rami.TOA/rpv.rami.libradtran.dat.all',
       'random' : True,
         'root' : 'rpv.rami/result.HET01_DIS_UNI_NIR_20.obj',
          'rpp' : 1,
          'rpv' : 'dart.rpv.rami/result.HET01_DIS_UNI_NIR_20.obj.brdf.dat.3params.dat',
          'rpv' : 'rpv.rami.2/result.HET01_DIS_UNI_NIR_20.obj.brdf.dat.3params.dat' ,
'samplingPattern' : 'circular',
        'three' : True,
         'time' : '2013 06 01 12 00 00',
            'v' : True,
       'wbfile' : 'wb.full_spectrum.1nm.dat',
           'wb' : 'wb.full_spectrum.1nm.dat'
    }

    VLAB.logger.info('%s: overwriting defaults' % (me))

    # overwrite defaults
    for a in args:
      if a == 'Sensor':
        q['sensor'] = args[a]
        q[a]        = args[a]
        if args[a] == VLAB.K_SENTINEL2:
          q['wb'] = 'wb.MSI.dat'
          q['wbfile'] = 'wb.MSI.dat'
          q['angfile'] = 'angles.MSI.dat'
        elif args[a] == VLAB.K_SENTINEL3:
          q['wb'] = 'wb.OLCI.dat'
          q['wbfile'] = 'wb.OLCI.dat'
          q['angfile'] = 'angles.OLCI.dat'
        elif args[a] == VLAB.K_MODIS:
          q['wb'] = 'wb.MODIS.dat'
          q['wbfile'] = 'wb.MODIS.dat'
          q['angfile'] = 'angles.MODIS.dat'
        elif args[a] == VLAB.K_MERIS:
          q['wb'] = 'wb.MERIS.dat'
          q['wbfile'] = 'wb.MERIS.dat'
          q['angfile'] = 'angles.MERIS.dat'
        elif args[a] == VLAB.K_LANDSAT_OLI:
          q['wb'] = 'wb.LANDSAT.OLI.dat'
          q['wbfile'] = 'wb.LANDSAT.OLI.dat'
          q['angfile'] = 'angles.LANDSAT.dat'
        elif args[a] == VLAB.K_LANDSAT_ETM:
          q['wb'] = 'wb.LANDSAT.ETM.dat'
          q['wbfile'] = 'wb.LANDSAT.ETM.dat'
          q['angfile'] = 'angles.LANDSAT.dat'
        else:
          q['wb'] = 'wb.full_spectrum.1nm.dat'
          q['wbfile'] = 'wb.full_spectrum.1nm.dat'
          q['angfile'] = 'angles.rami.dat'
      elif a == 'OutputDirectory':
        q['opdir'] = args[a]
      elif a == '3dScene':
        q['scene'] = VLAB.P_3dScene
        q[a]       = VLAB.P_3dScene
        if args[a] == VLAB.K_RAMI:
          q['obj'] = 'HET01_DIS_UNI_NIR_20.obj'
          q['lat'] = 0
          q['lon'] = 0
        elif args[a] == VLAB.K_LAEGERN:
          q['obj'] = 'laegeren.obj'
          q['lat'] = '47.4817'
          q['lon'] = '-8.3947'
        elif args[a] == VLAB.K_THARANDT:
          q['obj'] = 'HET01_DIS_UNI_NIR_20.obj' # FIXME: define when file is available
          q['lat'] = '50.9833'
          q['lon'] = '-13.5808'
        elif args[a] == VLAB.K_USER_DEFINED:
          q['obj'] = 'UserDefined.obj'
          # What about q['lat'] and q['lon']?
      elif a == 'Bands':
        # This would allow choosing particular bands
        # q['bands'] = [int(i) for i in tuple(args[a].split(", "))]
        bands = VLAB.getBandsFromGUI(args[VLAB.P_Sensor])
        q['bands'] = range(1,len(bands)+1)
      elif a == 'DHP_ImageFile':
        q['dhp'] = args[a] == 'Yes'
      elif a == 'ImageFile':
        q['image'] = args[a] == 'Yes'
      elif a == 'AsciiFile':
        q['ascii'] = args[a] == 'Yes'
      elif a == 'ViewingAzimuth':
        q['va'] = args[a]
      elif a == 'ViewingZenith':
        q['vz'] = args[a]
      elif a == 'DHP_Zenith':
        q['dhp_vz'] = args[a]
      elif a == 'DHP_Azimuth':
        q['dhp_va'] = args[a]
      elif a == 'IlluminationAzimuth':
        q['sz'] = args[a]
      elif a == 'IlluminationZenith':
        q['sa'] = args[a]
      else:
        q[a] = args[a]

    q['dataf']     = '%s/result.%s.brdf.dat' %(q['opdir'], q['obj'])
    q['paramfile'] = '%s/result.%s.brdf.dat.3params.dat' %(q['opdir'], q['obj'])
    q['plot']      = '%s/rpv.%s.dat.all' %(q['opdir'],q['obj'])
    q['plotfile']  = '%s/result.%s.brdf.3params' %(q['opdir'],q['obj'])
    q['root']      = '%s/result.%s' %(q['opdir'],q['obj'])
    q['rpv']       = '%s/result.%s.brdf.dat.3params.dat' %(q['opdir'],q['obj'])

    if 'dhp' in q:
      q['vz'] = q['dhp_vz']
      q['va'] = q['dhp_va']

    for a in ['dataf', 'paramfile','plot','plotfile','root', 'rpv']:
      VLAB.logger.info ('%s: q["%s"] is %s' % (me, a, q[a]))

    if VLAB.osName().startswith('Windows'):
      fullobjpath = '%s/%s' % (VLAB.expandEnv('%HOMEDRIVE%%HOMEPATH%/.beam/beam-vlab/auxdata/librat_scenes'), args['OutputDirectory'])
    else:
      fullobjpath = '%s/%s' % (VLAB.expandEnv('$HOME/.beam/beam-vlab/auxdata/librat_scenes'), args['OutputDirectory'])

    VLAB.logger.info ('%s: ensuring "%s" exists' %(me, fullobjpath))
    if not VLAB.path.exists(fullobjpath):
      VLAB.mkDirPath(fullobjpath)

    VLAB.logger.info('%s: instantiating objects' % (me))
    drivers      = Librat_drivers()
    dobrdf       = Librat_dobrdf()
    plot         = Librat_plot()
    rpv_invert   = Librat_rpv_invert()
    dolibradtran = Librat_dolibradtran()

    # not needed because we are using the dart angles
    # drivers.main()

    if (pm != None):
      pm.beginTask("Computing BRF...", 10)
    # ensure at least 1 second to ensure progress popup feedback
    time.sleep(1)

    VLAB.logger.info('%s: calling dobrdf.main()' % (me))
    dobrdf.main(q)

    if (pm != None):
      pm.beginTask("Plotting...", 10)
    VLAB.logger.info('%s: calling plot.main()' % (me))
    plot.main(q)

    VLAB.logger.info('%s: calling rpv.main()' % (me))
    if (pm != None):
      pm.beginTask("Inverting...", 10)
    rpv_invert.main(q)

    VLAB.logger.info('%s: calling dolibradtran.main()' % (me))
    if (pm != None):
      pm.beginTask("Libradtran...", 10)
    dolibradtran.main(q)

    VLAB.logger.info('%s: Finished computing...' % me)

    # Copy to results directory
    if VLAB.fileExists(fullobjpath):
      if (pm != None):
        pm.beginTask("Copying results...", 10)
      resdir = VLAB.fPath(LIBRAT.SDIR, "../results/librat/%s" % args['OutputDirectory'])
      VLAB.mkDirPath(resdir)
      VLAB.logger.info('%s: skipping copy of result %s -> %s' % (me, fullobjpath, resdir))
      #too much data, too much time
      #VLAB.copyDir(fullobjpath, resdir)
      VLAB.logger.info('%s: Done...' % me)

#### LIBRAT end ##############################################################

#### MAIN DISPATCH ####################################################

if not sys.platform.startswith('java'):
  VLAB.logger.info('%s: Mode: not jython and not BEAM' % VLAB.me)
  vlab = VLAB()
  vlab.selftests()
else:
  from java.lang import System
  beamVer = System.getProperty('beam.version')
  if beamVer == None:
    if System.getProperty('vlab.fakebeam') != None:
      VLAB.logger.info('%s: Mode: jython and fake BEAM' % VLAB.me)
      vlab = VLAB()
      vlab.fakebeam()
    else:
      VLAB.logger.info('%s: Mode: jython and not BEAM' % VLAB.me)
      vlab = VLAB()
      vlab.selftests()
  else:
    VLAB.logger.info('%s: Mode: jython and BEAM v%s' % (VLAB.me, beamVer))

### BEAM-only code ####################################################

    #
    # BEAM-specific code from here to end of file...
    #

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
    from java.lang         import IllegalArgumentException
    from java.lang         import Integer
    from java.lang         import ProcessBuilder
    from java.lang         import System
    from java.lang         import Thread
    from java.util         import ArrayList
    from java.util         import Arrays
    from java.util         import HashMap
    from java.util         import Map
    from java.util         import Vector
    from javax             import swing

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
      """Implements the BEAM Processor interface"""

      def __init__(self):
        me=self.__class__.__name__ +'::'+VLAB.me()
        VLAB.logger.info('%s: constructor completed...' % me)

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

      def process(self, pm, req):
        VLAB.logger.info('inside process...')
        me=self.__class__.__name__ +'::'+VLAB.me()
        ProcessorUtils.setProcessorLoggingHandler(VLAB.DEFAULT_LOG_PREFIX, 
          req, self.getName(), self.getVersion(), self.getCopyrightInformation())
        #VLAB.log("Parameter list:")
        #for i in range(req.getNumParameters()):
        #  VLAB.log(req.getParameterAt(i).getName() + " = " + req.getParameterAt(i).getValueAsText())

        VLAB.logger.info('%s: %s' % (me, ProcessorConstants.LOG_MSG_START_REQUEST))
        pm.beginTask('Running %s...' % VLAB.PROCESSOR_NAME, 10)
        VLAB.logger.info('%s: after pm.beginTask' % me)

        # ensure at least 1 second to ensure progress popup feedback
        time.sleep(1)
        VLAB.logger.info('%s: after sleep' % me)

        processor = self._getP(req, VLAB.P_RTProcessor)
        VLAB.logger.info('%s: processor is <%s>' % (me, processor))
        if processor == VLAB.K_DART:
          rtProcessor = DART()
        elif processor == VLAB.K_LIBRAT:
          rtProcessor = LIBRAT()
        elif processor == VLAB.K_DUMMY:
          rtProcessor = DUMMY()
        else:
          raise RuntimeError('unknown processor: <%s>' % processor)

        pm.beginTask("Computing top of canopy BRF...", 10)
        params = {}
        for i in VLAB.plst:
          val = self._getP(req, i)
          VLAB.logger.info('%s: val for %s is %s' % (me, i, val))
          params[i] = val

        VLAB.logger.info('%s: calling doProcessing' % me)
        rtProcessor.doProcessing(pm, params)

        VLAB.logger.info('%s : %s' % (me, ProcessorConstants.LOG_MSG_FINISHED_REQUEST))
        pm.done()

    ##
    ## BEAM-defined UI Implementation
    ##
    class VLabUiImpl(IVLabProcessorUi):
      """Implements the BEAM ProcessorUI interface"""
      def __init__(self):
        self._reqElemFac     = VLabRequestElementFactory()
        self._defaultFactory = DefaultRequestElementFactory.getInstance()
        self._requestFile    = File('')
        self.pmap            = {}

        me=self.__class__.__name__ +'::'+VLAB.me()
        VLAB.logger.info('%s: constructor completed...' % me)

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
                    if type(typ) == tuple:
                      self.pmap[nm].getEditor().setEnabled(typ[1])
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
      """Implements the BEAM RequestElementFactory interface"""
      def __init__(self):
        self._defaultFactory = DefaultRequestElementFactory.getInstance()
        self.pMap = {}
        me=self.__class__.__name__ +'::'+VLAB.me()
        VLAB.logger.info('%s : constructor completed...' % me)

      def getInstance(self):
        return VLabRequestElementFactory()

      def createParameter(self, name, value):
        Guardian.assertNotNullOrEmpty("name", name)
        try:
          param = self.createParamWithDefaultValueSet(name)
          if (value != None):
            param.setValueAsText(value, None)
        except IllegalArgumentException, e:
          VLAB.logger.info(e.getMessage)
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
            VLAB.logger.info('to be implemented!!!')
          elif (parameterName.endsWith(VLAB.P_CONDITION)):
            VLAB.logger.info('to be implemented!!!')
          elif (parameterName.endsWith(VLAB.P_OUTPUT)):
            VLAB.logger.info('to be implemented!!!')

        if (paramProps == None):
          raise IllegalArgumentException("Invalid parameter name '" + parameterName + "'.")
        return paramProps

      def createStringParamProperties(self):
        return self._defaultFactory.createStringParamProperties()
