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
# Authors: Cyrill Schenkel, Daniel Kueckenbrink, Joshy Cyriac, Marcel Kessler, Jason Brazile
#

##############################################################################
# Three ways to run it:
# 
# 1. embedded within the BEAM processor (normal case)
#
# 2. standalone tests - headless (either jython or python)
#
#    jython -Dpython.path=jcommon-1.0.16.jar:jfreechart-1.0.13.jar VLabImpl.py
#    python VLabImpl.py
#
# 3. standalone with a 'fake' swing-based gui
# 
#    jython -Dvlab.fakebeam=1 -Dpython.path=${HOME}/beam-4.11/lib/jcommon-1.0.16.jar:${HOME}/beam-4.11/lib/jfreechart-1.0.13.jar VLabImpl.py
#
# Those BEAM-supplied jars can also be obtained like this:
#    wget -U "Mozilla/5.0" http://repo1.maven.org/maven2/jfree/jfreechart/1.0.13/jfreechart-1.0.13.jar
#    wget -U "Mozilla/5.0" http://repo1.maven.org/maven2/jfree/jcommon/1.0.16/jcommon-1.0.16.jar
#
#

import sys, math, operator, array, time, struct
from array import array

class VLAB:
  """VLAB contains conf. constants, static utility methods, and test methods"""

  COPYRIGHT_INFO     = 'Copyright (C) 2010-2013 Netcetera Switzerland (info@netcetera.com)'
  PROCESSOR_NAME     = 'BEAM VLab Processor'
  PROCESSOR_SNAME    = 'beam-vlab'
  REQUEST_TYPE       = 'VLAB'
  UI_TITLE           = 'VLab - Processor'
  VERSION_STRING     = '1.0 (3 Nov 2013)'
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

  DBG                = 'debug' 
  INF                = 'info'
  ERR                = 'error'

  plst               = []

  if sys.platform.startswith('java'):
    from java.util.logging import Logger
    logger = Logger.getLogger(LOGGER_NAME)
  else:
    import logging
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)
    logch = logging.StreamHandler()
    logch.setLevel(logging.DEBUG)
    logger.addHandler(logch)
    #logfh = logging.FileHandler('%s.log' % LOGGER_NAME)
    #logfh.setLevel(logging.DEBUG)
    #logger.addHander(logfh)

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
  def listdir(path):
    """list files in the directory given by path"""
    if sys.platform.startswith('java'):
      from java.io import File
      return File(path).list()
    else:
      import os
      return os.listdir(path)
  listdir = staticmethod(listdir)
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
      fp = open(fname, 'rw')
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
      if File(filename).createNewFile():
        return open(filename)
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
          self.fp = open(fName, 'w')
      def run(self):
        """helper class for slurping up child streams"""
        from java.io import BufferedReader
        from java.io import InputStreamReader
        from java.lang import System
        line = None; br = BufferedReader(InputStreamReader(self.strm))
        line = br.readLine()
        while (line != None):
          if self.fp != None:
            self.fp.write(line + System.lineSeparator())
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
      cmdLine = ['cmd', '/c']
    else:
      cmd=cmdrec['linux']
    exe = VLAB.expandEnv(cmd['exe'])
    if not VLAB.fileExists(exe):
      raise RuntimeError('Cannot find exe "%s"' % exe)
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
  def min_l_bfgs_b(f, initial_guess, args=(), bounds=None, epsilon=1e-8):
    """The `approx_grad' is not yet implemented, because it's not yet
used."""
    if sys.platform.startswith('java'):
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
      return result.point
  min_l_bfgs_b = staticmethod(min_l_bfgs_b)
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
      VLAB.P_3dScene             : 'Default RAMI', 
      VLAB.P_AtmosphereCO2       : '1.6', 
      VLAB.P_ViewingAzimuth      : '0.0', 
      VLAB.P_AtmosphereWater     : '0.0', 
      VLAB.P_OutputPrefix        : 'RAMI_', 
      VLAB.P_ViewingZenith       : '20.0', 
      VLAB.P_AtmosphereAerosol   : 'Rural', 
      VLAB.P_DHP_Zenith          : '20.0', 
      VLAB.P_SceneYW             : '100', 
      VLAB.P_DHP_3dScene         : 'Default RAMI', 
      VLAB.P_Bands               : '1, 2, 3, 4, 5, 6, 7, 8, 9, 10', 
      VLAB.P_OutputDirectory     : '', 
      VLAB.P_AtmosphereOzone     : '300', 
      VLAB.P_AtmosphereDay       : '214', 
      VLAB.P_SceneLocFile        : '', 
      VLAB.P_SceneYC             : '100', 
      VLAB.P_DHP_OutputDirectory : '', 
      VLAB.P_DHP_OutputPrefix    : 'RAMI00_', 
      VLAB.P_AtmosphereLat       : '47.4781', 
      VLAB.P_AtmosphereLong      : '8.3650', 
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
    std_dev = sqrt(sum / self.N)
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
  """A dummy processor for testing the VLAB plugin """
  def __init__(self):
    me=self.__class__.__name__ +'::'+VLAB.me()
    VLAB.logger.info('%s: constructor completed...' % me)
  def doProcessing(self, pm, args):
    """do processing for DUMMY processor"""
    me=self.__class__.__name__ +'::'+VLAB.me()

    VLAB.logger.info('%s: doExec() on %s' % (me, args))
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
      'cwd'     : '%HOMEDRIVE%%HOMEPATH%/.beam/beam-vlab/auxdata/dummy_win32',
      'exe'     : '%HOMEDRIVE%%HOMEPATH%/.beam/beam-vlab/auxdata/dummy_win32//dummy.exe',
      'cmdline' : [ '-e', '1', '-r', '5' ],
      'stdin'   : None,
      'stdout'  : None,
      'stderr'  : None,
      'env'     : None
    }
    }
    VLAB.doExec(cmd)

    if (pm != None):
      pm.beginTask("Computing BRF...", 10)
    # ensure at least 1 second to ensure progress popup feedback
    time.sleep(1)
    VLAB.logger.info('%s: finished running...' % me)

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
  dartLocal = VLAB.getenv('DART_LOCAL')
  
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

class Dart_DARTRootSimulationDirectory :
  def __init__(self) :
    pass
  
  def samefile(self, path1, path2) :
    return VLAB.path.normcase(VLAB.path.normpath(path1)) == VLAB.path.normcase(VLAB.path.normpath(path2))
  
  def getAbsolutePath(self) :
    return VLAB.path.join(Dart_DARTEnv.dartLocal, Dart_DARTEnv.simulationsDirectory)
  
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

  def getImagesBandsAsList( self, Dart_DartInfo, Dart_ImageInfo ) :

    simulation = Dart_DARTDao().getSimulation( Dart_DartInfo.simulationName )

    imagesList = []
    spectralBandsList = []
    
    if Dart_DartInfo.isSequence:
      sequencesList = simulation.listSequences( Dart_DartInfo.sequenceName )
      
      for sequence in sequencesList:
        # Recover the number of Spectral Band
        spectralBands = sequence.getSpectralBands()
    
        # Recover the Directions
        if Dart_ImageInfo.isUserDirection:
          directions = sequence.getUserDirections()
        else:
          directions = simulation.getDiscretizedDirection()
  
        # Recover the images in the defined direction for each spectral band
        for band in spectralBands:
          imagesList.append(sequence.getImageInDirection( directions[ Dart_ImageInfo.directionNumber ], band.index, Dart_ImageInfo.dataType, Dart_ImageInfo.imageLevel, Dart_ImageInfo.iteration, Dart_ImageInfo.projectionPlane ))
          spectralBandsList.append( band )
    else:
      # Recover the number of Spectral Band
      spectralBands = simulation.getSpectralBands()

      # Recover the Directions
      if Dart_ImageInfo.isUserDirection:
        directions = sequence.getUserDirections()
      else:
        directions = simulation.getDiscretizedDirection()

      # Recover the images in the defined direction for each spectral band
      for band in spectralBands:
        imagesList.append(simulation.getImageInDirection( directions[ Dart_ImageInfo.directionNumber ], band.index, Dart_ImageInfo.dataType, Dart_ImageInfo.imageLevel, Dart_ImageInfo.iteration, Dart_ImageInfo.projectionPlane ))
        spectralBandsList.append( band )

    return imagesList, spectralBandsList
  
  def writeDataCube( self, Dart_DartInfo, Dart_ImageInfo, Dart_HeaderInfo ) :
    
    imagesList, spectralBandsList = self.getImagesBandsAsList( Dart_DartInfo, Dart_ImageInfo )
    
    # write BSQ binary file
    fout = open( Dart_DartInfo.outputFilename + '.bsq', 'wb')
    flatarray = array('f', self.flatten( imagesList ))
    flatarray.tofile(fout)
    fout.close()

    # ENVI header information, more infos on: http://geol.hu/data/online_help/ENVI_Header_Format.html
    samples = len( imagesList[0][0] )
    lines = len( imagesList[0] )
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
    fout = open( Dart_DartInfo.outputFilename + '.hdr', 'w')
    fout.writelines( 'ENVI ' + '\n' )
    fout.writelines( 'description = { ' + Dart_HeaderInfo.description + ' }' + '\n' )
    fout.writelines( 'samples = ' + str( samples ) + '\n' )
    fout.writelines( 'lines = ' + str( lines ) + '\n' )
    fout.writelines( 'bands = ' + str( bands ) + '\n' )
    fout.writelines( 'header offset = ' + str( headerOffset ) + '\n' )
    fout.writelines( 'file type = ' + fileType + '\n' )
    fout.writelines( 'data type = ' + str( dataType ) + '\n' )
    fout.writelines( 'interleave = ' + interleave + '\n' )
    fout.writelines( 'sensor type = ' + Dart_HeaderInfo.sensorType + '\n' )
    fout.writelines( 'byte order = ' + str( byteOrder ) + '\n' )
    fout.writelines( 'x start = ' + str( xStart ) + '\n' )
    fout.writelines( 'y start = ' + str( yStart ) + '\n' )
    fout.writelines( 'map info = {' + Dart_HeaderInfo.projectionName + ', ' + str( Dart_HeaderInfo.xReferencePixel ) + ', ' + str( Dart_HeaderInfo.yReferencePixel ) + ', ' + str( Dart_HeaderInfo.xReferenceCoordinate ) + ', ' + str( Dart_HeaderInfo.yReferenceCoordinate ) + ', ' + str( Dart_HeaderInfo.xPixelSize ) + ', ' + str( Dart_HeaderInfo.yPixelSize ) + ', ' + Dart_HeaderInfo.pixelUnits + ' }' + '\n' )
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


class Dart_DartInfo :
  
  simulationName = 'DartSimulation30m_Laegeren' # name of the DART simulation
  isSequence = False            # options: True = images shall be restored from a sequence // False = images shall be restored from the simulation output only
  sequenceName = 'sequence_apex'      # name of the sequence within the simulation (if there is one)
  outputFilename = 'DartOutput'     # name of the output file that is written

class Dart_ImageInfo :

  imageLevel = Dart_DataLevel.SENSOR         # options: BOA = bottom of atmosphere // SENSOR = at sensor // TOA = top of atmosphere // ATMOSPHERE_ONLY
  isUserDirection = False             # options: True = images of a user defined direction // False = images of a discretisized direction
  directionNumber = 0               # number of the direction starting at 0, e.g. 0 = first direction
  dataType = Dart_DataUnit.RADIANCE          # options: BRF_TAPP = bidirectional reflectance factor [0 1] // RADIANCE = radiance [W/m2]
  iteration = 'last'                # last iteration product
  projectionPlane=Dart_ProjectionPlane.SENSOR_PLANE  # options: SENSOR_PLANE = image in the sensor plane // ORTHOPROJECTION = orthorectified image // BOA_PLANE = non-projected image on the BOA plane

# see more information on http://geol.hu/data/online_help/ENVI_Header_Format.html
class Dart_HeaderInfo :

  description = 'some text'       # description of the file
  sensorType = 'APEX'           # specific sensor type like IKONOS, QuickBird, RADARSAT  
  projectionName = 'Arbitrary'      # name of projection, e.g. UTM
  xReferencePixel = 1           # x pixel corresponding to the reference x-coordinate
  yReferencePixel = 1           # y pixel corresponding to the reference y-coordinate
  xReferenceCoordinate = 2669660.0000   # reference pixel x location in file coordinates
  yReferenceCoordinate = 1259210.0000   # reference pixel y location in file coordinates
  xPixelSize = 1							# pixel size in x direction
  yPixelSize = 1							# pixel size in y direction
  pixelUnits = 'units=Meters'


#
# End of Dart_* integration routines
#

class DART:
  """Integration glue for calling external DART programs"""
  def __init__(self):
    me=self.__class__.__name__ +'::'+VLAB.me()
    VLAB.logger.info('%s: constructor completed...' % me)
  def doProcessing(self, pm, args):
    """do processing for DART processor"""
    me=self.__class__.__name__ +'::'+VLAB.me()

    if (pm != None):
      pm.beginTask("Computing BRF...", 10)
    # ensure at least 1 second to ensure progress popup feedback
    time.sleep(1)

    #
    # collect into a consolidated data cube
    #
    # Dart_DartImages().writeDataCube( Dart_DartInfo, Dart_ImageInfo, Dart_HeaderInfo )
    VLAB.logger.info('%s: done...' % me)

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
      'result_image'    : 'result.hips',
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
      cdata += ' %s = %s;\n' %('geometry.fov', q['fov'])
    if 'lidar' in q:
      if q['lidar']:
        cdata += ' %s = %s;\n' %('lidar.binStep', q['binStep']) \
               + ' %s = %s;\n' %('lidar.binStart', q['binStart']) \
               + ' %s = %s;\n' %('lidar.nBins', q['nBins'])
    cdata += '}'
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
    if key in q: ldata += '%s = %s\n' %('geometry.ideal', ', '.join(map(str, map('%.1f'.__mod__, q[key]))))
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
   + ' ' \
   + VLAB.getFullPath(camFile) \
   + ' ' \
   + VLAB.getFullPath(lightFile)
    fp = open(inpFile, 'w')
    try:
      fp.write(idata)
    finally:
      fp.close()

  def _writeGrabFile(self, grabFile, args):
    gFilePath = VLAB.getFullPath(grabFile)
    # 'cwd'     : '$HOME/.beam/beam-vlab/auxdata/librat_scenes',
    gdata = """cmd = {
  'linux' : {
    'cwd'     : '$HOME/.beam/beam-vlab/auxdata/librat_scenes',
    'exe'     : '$HOME/.beam/beam-vlab/auxdata/librat_lin64/src/start/start',
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
    gdata += 'VLAB.doExec(cmd)\n'
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
      sys.stderr.write("%s: wrong number of fields (%i) in %s - should be 4\n"%(me, len(ang[1]), q['anglefile']))
      sys.exit([True])

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
          execfile(grabme)
    VLAB.logger.info('done')

#############################################################################
class Librat_dolibradtran:
  def defaultLRT(self, fp, solar_file, dens_column, correlated_k, rte_solver, rpvfile, deltam, nstr, zout, output_user, quiet):
    fp.write('solar_file ' + solar_file + '\n')
    fp.write('dens_column ' + dens_column)
    fp.write('correlated_k ' + correlated_k)
    fp.write('rte_solver ' + rte_solver)
    fp.write('rpv_file ' + rpvfile + '\n')
    fp.write('deltam ' + deltam)
    fp.write('nstr ' + nstr)
    fp.write('zout ' + zout)
    fp.write('output_user ' + output_user)
    fp.write(quiet)
  def main(self, args):
    me=self.__class__.__name__ +'::'+VLAB.me()
    VLAB.logger.info('======> %s' % me)
    for a in args:
      VLAB.logger.info("%s -> %s" % (a, args[a]))

    q = {
      'LIBRADTRAN_PATH' : '/data/geospatial_07/mdisney/ESA/3Dveglab/libRadtran-1.7/',
               'ipfile' : 'libradtran.ip',
               'opfile' : 'libradtran.ip.op',
                'opdir' : 'libradtran',
               'wbfile' : 'wb.MSI.dat',
            'anglefile' : 'angles.MSI.dat',
              'rpvfile' : 'rpv.laegeren.libradtran.dat',
                 'root' : 'libradtran',
                  'lat' : False,
                  'lon' : False,
                 'time' : False,
             'dartflag' : True,
                'solar' : 'data/solar_flux/NewGuey2003.dat',
          'dens_column' : 'O3 300.\n',
         'correlated_k' : 'LOWTRAN\n',
           'rte_solver' : 'cdisort\n',
               'deltam' : 'on\n',
                 'nstr' : '6\n',
                 'zout' : 'TOA\n',
          'output_user' : 'lambda uu\n',
                'quiet' : 'quiet\n',
           'plotfilefp' : False,
                    'v' : False,
             'plotfile' : False
    }

    for a in args:
      if a == 'lrtp':
        q['LIBRADTRAN_PATH']  = args[a]
      elif a == 'plot':
        q['plotfile'] = args[a]
      elif a == 'rpv':
        q['rpvfile'] = args[a]
      else:
        q[a] = args[a]

    LIBRADTRAN = q['LIBRADTRAN_PATH'] + 'bin/uvspec'
    solar_file = q['LIBRADTRAN_PATH'] + q['solar']

    VLAB.mkDirPath('%s/%s' % (LIBRAT.SDIR, q['opdir']))

    # TODO prove that LIBRADTRAN_PATH dir exists

    angfp = VLAB.checkFile('%s/%s' % (LIBRAT.SDIR, q['anglefile']))
    wbfp = VLAB.checkFile('%s/%s' % (LIBRAT.SDIR, q['wbfile']))
    rpvfp = VLAB.checkFile('%s/%s' % (LIBRAT.SDIR, q['rpvfile']))

    rpv = VLAB.valuesfromfile('%s/%s' % (LIBRAT.SDIR, q['rpvfile']))
    if len(rpv[0]) != 4: # length of index 1 because index 0 is heading
      sys.stderr.write("%s: rpv file %s wrong no. of cols (should be 4: lambda (nm), rho0, k, theta\n" % (sys.argv[0], q['rpvfile']))
      sys.exit([True])

    angt = VLAB.valuesfromfile('%s/%s' % (LIBRAT.SDIR, q['anglefile']))
    wb = [i[1] for i in VLAB.valuesfromfile('%s/%s' % (LIBRAT.SDIR, q['wbfile']))]

    nbands = len(wb)
    wbstep = 1
    if q['v']:
      sys.stderr.write('%s: wbmin = %i, wbmax = %i, wbstep = %i\n'%(sys.argv[0],min(wb),max(wb),wbstep))

    if q['v']:
      # only do all angles if time not specified, if time specified use that to get sza and phi0
      if q['lat'] and ['lon'] and ['time']:
        sys.stderr.write("%s: doing lat lon time, not using sun angles in file %s\n" % (sys.argv[0], q['anglefile']))

    # check for op file if required
    if not VLAB.fileExists('%s/%s' % (LIBRAT.SDIR, q['plotfile'])):
      plotfilefp = VLAB.openFileIfNotExists('%s/%s' % (LIBRAT.SDIR, q['plotfile']))
    else:
      sys.stderr.write('%s: plotfile %s already exists - move/delete and re-run\n'%(sys.argv[0],q['plotfile']))
      sys.exit(1)

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

      umu = math.cos(vzz)
      angstr = str(vzz) + '_' + str(vaa) + '_' + str(szz) + '_' + str(saa)
      
      libradtran_ip = VLAB.fPath('%s/%s' % (LIBRAT.SDIR, q['opdir']), 'ip.' + q['root'] + '.' + q['wbfile'] + '_' + angstr)
      libradtran_op = VLAB.fPath('%s/%s' % (LIBRAT.SDIR, q['opdir']), 'op.' + q['root'] + '.' + q['wbfile'] + '_' + angstr)

      if not VLAB.fileExists(libradtran_ip):
        libradtranfp = VLAB.openFileIfNotExists(libradtran_ip)
        defaultLRT(libradtranfp, solar_file, dens_column, correlated_k, rte_solver, rpvfile, deltam, nstr, zout, output_user, quiet)

        if q['v']:
          sys.stderr.write('%s: doing ip file %s\n'%(sys.argv[0],libradtran_ip))
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
        libradtranfp.write('umu ' + ' '.join(map(str, umu)) + '\n')
        libradtranfp.write('phi ' + ' '.join(map(str, vaa)) + '\n')

        # add sz angles
        if lat and lon and time:
          libradtranfp.writelines('latitude ' + q['lat'] + '\n')
          libradtranfp.writelines('longitude ' + q['lon'] + '\n')
          libradtranfp.writelines('time ' + q['time'] + '\n')
        else:
          # print out sun angles
          libradtranfp.write('sza ' + ' '.join(map(str, szz)) + '\n')
          libradtranfp.write('phi0 ' + ' '.join(map(str, saa)) + '\n')

          # write out wavelengths i.e. min and max. Step is determined by step in solar file i.e. 1nm default
          libradtranfp.write('wavelength ' + np.str(np.int(wb.min())) + ' ' + np.str(np.int(wb.max())) + '\n')
          libradtranfp.flush()

          cmd = LIBRADTRAN + ' < ' + libradtran_ip + ' > ' + libradtran_op

          if q['v']:
            sys.stderr.write('%s: doing cmd %s\n'%(sys.argv[0],cmd))

          # run the libradtran command
          raise Exception("os.system(cmd)")

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

      for n, va in enumerate(data['vaa']):
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

      # FIXME: temporarily set a particular seed for reproducibility
      rState = VLAB.rndInit(17)

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
      'angfile' : 'angles.OLCI.dat',
       'wbfile' : 'wb.MSI.dat',
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
    opdat = root + '.brdf.dat'
    opplot = root + '.brdf.png'
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
    for b in [3, 7]:
      VLAB.plot(dataset, ang[0], [i[b] for i in result],
           "waveband: %.1f" % wb [b])
    chart = VLAB.make_chart("plot.py out", "view zenith angle (deg.)",
                            u"\u03A1", dataset)
    sys.stderr.write('%s: plotting brdf to: %s\n'%(sys.argv[0], opplot))
    sys.stderr.write('%s: saving brdf data to: %s\n'%(sys.argv[0], opdat))
    outdata = [[0. for i in xrange(len(result[0]) + len(ang))]
               for j in xrange(len(result))]
    VLAB.replacerectinarray(outdata, zip(*ang), 0, 0, len(result), len(ang))
    VLAB.replacerectinarray(outdata, zip(*ang), 0, len(ang), len(result), len(result) + len(ang))
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

    wb = VLAB.valuesfromfile('%s/%s' (LIBRAT.SDIR, q['wbfile']), transpose=True)[1]
    data = VLAB.valuesfromfile('%s/%s' (LIBRAT.SDIR, q['dataf']), transpose=True)

    # check shape of 2 data files i.e. that there are same no. of wbs on each line of datafile ( + 4 angles)
    if len(wb) != len(data) - 4:
      sys.stderr.write('%s: no of wavebands different in brdf file %s and wb file %s\n'%(sys.argv[0],q['dataf'],q['wbfile']))
      sys.exit(1)

    rho0, k, bigtet, rhoc = 0.03, 1.2, 0.1, 0.2

    if q['three']:
      params = [rho0, k, bigtet]
    else:
      params = [rho0, k, bigtet, rhoc]

    if args['paramfile']:
      opdat = args['paramfile']
    else:
      opdat = q['dataf'] + '.params.dat'

    if q['verbose']: sys.stderr.write('%s: saving params to %s\n'%(sys.argv[0], opdat))

    # create the file if it doesn't exist
    dfp = VLAB.openFileIfNotExists('%s/%s' % (LIBRAT.SDIR, opdat))
    if dfp != None:
      dfp.close()

    # open the previously created file
    opfp = open('%s/%s' % (LIBRAT.SDIR,  opdat), 'w')

    if q['three']:
      opfp.write('# wb rho0 k bigtet\n')
    else:
      opfp.write('# wb rho0 k bigtet rhoc\n')

    ymin, ymax = (0, 0.25)
    xmin, xmax = (-75., 75)

    for wbNum, band in enumerate(wb):
      if q['verbose']: sys.stderr.write('%s: doing band %i (%f)\n'%(sys.argv[0], wbNum, band))

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
          opplot = q['plotfile'] + '.inv.wb.' + str(wbNum) + '.png'
        else:
          opplot = dataf + '.inv.wb.' + str(wbNum) + '.png'

        if q['verbose']: sys.stderr.write('%s: plotting to %s\n' % (sys.argv[0], opplot))

        dataset = VLAB.make_dataset()
        VLAB.plot(dataset, invdata[0], invdata[4], "original")
        VLAB.plot(dataset, invdata[0], r, "inverted")
        chart = VLAB.make_chart("", "vza (deg)", u"\u03A1", dataset)
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
    f2 = map(lambda x : {True : (1.0 - bgthsq) * 1e20, False : (1.0 - bgthsq) / x}
             [x == 0.], relphi)
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
      'exe'     : '$HOME/.beam/beam-vlab/auxdata/librat_lin64/src/start/start',
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
    VLAB.doExec(cmd)

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
       'fov' : 150,
       'rpp' : 8,
   'npixels' : 4000000,
     'opdir' : 'DHP_TEST'
    }
    # dobrdf.main(args)
    VLAB.logger.info('%s: Done...' % me)

  def doProcessing(self, pm, args):
    """do processing for LIBRAT processor"""
    me=self.__class__.__name__ +'::'+VLAB.me()

    # defaults
    q = {
       'angles' : 'angle.rpv.cosDOM.dat',
        'bands' : (250, 450),
         'boom' : 786000, 
         'brdf' : True,
        'dataf' : 'dart.rpv.laegeren/result.laegeren.obj.lai.1.brdf.dat',
          'dhp' : True,
          'fov' : 150,
         'hips' : True,
        'ideal' : (300., 300.),
          'lat' : 50, 
          'lon' : 0,
         'look' : (150., 150., 710.),
     'lookFile' : 'dhp.locations.ondem.dat',
            'n' : 1000,
         'nice' : 19,
      'npixels' : 10000,
          'obj' : 'HET01_DIS_UNI_NIR_20.obj',
        'opdir' : 'dart.rami.TOA',
    'paramfile' : 'dart.rpv.rami/result.HET01_DIS_UNI_NIR_20.obj.brdf.dat.3params.dat',
         'plot' : 'dart.rami.TOA/rpv.rami.libradtran.dat.all',
     'plotfile' : 'rpv.rami.2/result.HET01_DIS_UNI_NIR_20.obj.brdf.3params',
         'plot' : 'rami.TOA/rpv.rami.libradtran.dat.all',
       'random' : True,
         'root' : 'rpv.rami/result.HET01_DIS_UNI_NIR_20.obj',
          'rpp' : 4, 
          'rpv' : 'dart.rpv.rami/result.HET01_DIS_UNI_NIR_20.obj.brdf.dat.3params.dat',
          'rpv' : 'rpv.rami.2/result.HET01_DIS_UNI_NIR_20.obj.brdf.dat.3params.dat' ,
'samplingPattern' : 'circular',
        'three' : True,
         'time' : '2013 06 01 12 00 00',
            'v' : True,
       'wbfile' : 'wb.full_spectrum.1nm.dat',
           'wb' : 'wb.full_spectrum.1nm.dat'
    }

    # overwrite defaults
    for a in args:
      if a == 'wb':
        if args[a] == VLAB.K_SENTINAL2:
          q['wb'] = 'wb.MSI.dat'
        elif args[a] == VLAB.K_SENTINAL3:
          q['wb'] = 'wb.OLCI.dat'
        else:
          q['wb'] = 'wb.full_spectrum.1nm.dat'
      elif a == 'anotherexample':
        if args[a] == 'somethingtobetranslated':
          q['thingy'] = 'translatedthingy'
        else:
          q['thingy'] = 'defaultthingy'

    drivers      = Librat_drivers()
    dobrdf       = Librat_dobrdf()
    plot         = Librat_plot()
    rpv_invert   = Librat_rpv_invert()
    dolibradtran = Librat_dolibradtran()

    if (pm != None):
      pm.beginTask("Computing BRF...", 10)
    # ensure at least 1 second to ensure progress popup feedback
    time.sleep(1)

    # not needed because we are using the dart angles
    # drivers.main()

    dobrdf.main(q)
    plot.main(q)
    rpv_invert.main(q)
    dolibradtran.main(q)

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
        myargs = {
        }
        rtProcessor.doProcessing(pm, myargs)

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
            VLAB.lof('to be implemented!!!')
          elif (parameterName.endsWith(VLAB.P_CONDITION)):
            VLAB.lof('to be implemented!!!')
          elif (parameterName.endsWith(VLAB.P_OUTPUT)):
            VLAB.lof('to be implemented!!!')
  
        if (paramProps == None):
          raise IllegalArgumentException("Invalid parameter name '" + parameterName + "'.")
        return paramProps
  
      def createStringParamProperties(self):
        return self._defaultFactory.createStringParamProperties()
