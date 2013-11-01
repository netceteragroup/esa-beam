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
  VERSION_STRING     = '1.0 (29 Oct 2013)'
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
  def checkFile(fname):
    """open a file if it exists, otherwise die"""
    try:
      fp = open(fname, 'rw')
      return fp
    except IOError, e:
      raise RuntimeException(e)
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
          raise RuntimeExecption('failed to mkdir %s' % path)
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
      raise RuntimeException('Cannot find exe "%s"' % exe)
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
              raise RuntimeException('Cannot find stdin "%s"' % cmd['cwd'])
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
    values = [line.strip().split() for line in open(path)
              if not line.startswith('#')]
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
      raise RuntimeException('unknown processor: <%s>' % params[VLAB.P_RTProcessor])
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

    if (pm != None):
      pm.beginTask("Computing BRF...", 10)
    # ensure at least 1 second to ensure progress popup feedback
    time.sleep(1)
    VLAB.logger.info('%s: finished running...' % me)

#### DUMMY end ###############################################################

#### DART start ##############################################################

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
    VLAB.logger.info('%s: running...' % me)

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
    'cwd'     : None,
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
    'cwd'     : None,
    'exe'     : '%HOMEDRIVE%%HOMEPATH%\\.beam\\beam-vlab\\auxdata\\librat_win32\\src\\start\\ratstart.exe',
    'cmdline' : ['-RATv', '-m', '%s', '-RATsensor_wavebands', '%HOMEDRIVE%%HOMEPATH%\\.beam\\beam-vlab\\auxdata\\librat_scenes\\%s', '%HOMEDRIVE%%HOMEPATH%\\.beam\\beam-vlab\\auxdata\\librat_scenes\\%s' ],
    'stdin'   : '%s',
    'stdout'  : '%s',
    'stderr'  : '%s',
    'env'     : {
      'BPMS'  : '%HOMEDRIVE%%HOMEPATH%\\.beam\\beam-vlab\\auxdata\\librat_win32'
   }}
}
"""
    # hack to allow replacing only %s
    escaped = gdata.replace("%%","\x81\x81").replace("%H","\x81H").replace("%\\","\x81\\")
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
      'nice'            : '',
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

    VLAB.mkDirPath(q['opdir'])

    angfp = VLAB.checkFile(q['anglefile'])
    wbfp  = VLAB.checkFile(q['wbfile'])
    objfp = VLAB.checkFile(q['objfile'])

    # vz va sz sa
    ang = VLAB.valuesfromfile(q['anglefile'])

    if 'lookFile' in q:
      lookfp = VLAB.checkFile(q['lookFile'])
      q['look_xyz'] = VLAB.valuesfromfile(q['lookFile'])

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
        lightfile = VLAB.fPath(q['opdir'], q['light_root'] + '_sz_' + str(q['sz']) + '_sa_' + str(q['sa']) + '_dat')
        ligfp = VLAB.openFileIfNotExists(lightfile)
        if ligfp != None:
          nq = {
            'sz' : q['sz'],
            'sa' : q['sa'],
          }
          self._writeLightFile(lightfile, nq)

        rooty = q['objfile'] + '_vz_' + str(q['vz']) + '_va_' + str(q['va']) + '_sz_' + str(q['sz']) + '_sa_' + str(q['sa']) + '_xyz_' + str(look[0]) + '_' + str(look[1]) + '_' + str(look[2]) + '_wb_' + q['wbfile']
        grabme = VLAB.fPath(q['opdir'], q['grabme_root'] + '.' + rooty)
        if 'dhp' in q:
          location = look.copy()
          look[2] = q['INFINITY']
          sampling = 'circular'

        if not VLAB.fileExists(grabme):
          grabfp = VLAB.openFileIfNotExists(grabme)
          q['grabme_log'] = grabme + '.log'
          q['camfile'] = VLAB.fPath(q['opdir'], q['camera_root'] + '.' + rooty)
          q['oproot'] = VLAB.fPath(q['opdir'], q['result_root'] + '.' + rooty)
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

    VLAB.mkDirPath(q['opdir'])

    # TODO prove that LIBRADTRAN_PATH dir exists

    angfp = VLAB.checkFile(q['anglefile'])
    wbfp = VLAB.checkFile(q['wbfile'])
    rpvfp = VLAB.checkFile(q['rpvfile'])

    rpv = VLAB.valuesfromfile(q['rpvfile'])
    if len(rpv[0]) != 4: # length of index 1 because index 0 is heading
      sys.stderr.write("%s: rpv file %s wrong no. of cols (should be 4: lambda (nm), rho0, k, theta\n" % (sys.argv[0], q['rpvfile']))
      sys.exit([True])

    angt = VLAB.valuesfromfile(q['anglefile'])
    wb = [i[1] for i in VLAB.valuesfromfile(q['wbfile'])]

    nbands = len(wb)
    wbstep = 1
    if q['v']:
      sys.stderr.write('%s: wbmin = %i, wbmax = %i, wbstep = %i\n'%(sys.argv[0],min(wb),max(wb),wbstep))

    if q['v']:
      # only do all angles if time not specified, if time specified use that to get sza and phi0
      if q['lat'] and ['lon'] and ['time']:
        sys.stderr.write("%s: doing lat lon time, not using sun angles in file %s\n" % (sys.argv[0], q['anglefile']))

    # check for op file if required
    if not VLAB.fileExists(q['plotfile']):
      plotfilefp = VLAB.openFileIfNotExists(q['plotfile'])
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
      
      libradtran_ip = VLAB.fPath(q['opdir'], 'ip.' + q['root'] + '.' + q['wbfile'] + '_' + angstr)
      libradtran_op = VLAB.fPath(q['opdir'], 'op.' + q['root'] + '.' + q['wbfile'] + '_' + angstr)

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
	
      for f in [f for f in VLAB.listdir(q['opdir']) if f.startswith('op.')]:
        vzz = f.split('_')[-4]
        vaa = f.split('_')[-3]
        szz = f.split('_')[-2]
        saa = f.split('_')[-1]
        d = VLAB.valuesfromfile(f,transpose=True)
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
    wbspec_contents = VLAB.valuesfromfile(wbspec, transpose=True)

    wb = wbspec_contents[1];
    op1 = spec + '.plot.png'

    data = wbspec_contents
    refl = data[1:,].sum(axis=1)
    # TODO Implement rest of function
    raise Exception("spec_plot()")
  def brdf_plot(self,root,angfile,wbfile):
    opdat = root + '.brdf.dat'
    opplot = root + '.brdf.png'
    ang = VLAB.valuesfromfile(angfile, transpose=True)
    wb = VLAB.valuesfromfile(wbfile, transpose=True)[1]

    result = [[0. for i in range(len(wb))] for i in range(len(ang[0]))]

    ff = [root.split('/')[0] + '/' + f for f in VLAB.listdir(root.split('/')[0])
          if f.endswith('.direct') and f.startswith(root.split('/')[1])]
    for f in ff:
      fsplit = f.split('_')
      vz = f.split('_')[fsplit.index('vz') + 1]
      va = f.split('_')[fsplit.index('va') + 1]
      sz = f.split('_')[fsplit.index('sz') + 1]
      sa = f.split('_')[fsplit.index('sa') + 1]

      data = VLAB.valuesfromfile(f, transpose=True)
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

    wb = VLAB.valuesfromfile(q['wbfile'], transpose=True)[1]
    data = VLAB.valuesfromfile(q['dataf'], transpose=True)

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
    VLAB.openFileIfNotExists(opdat)

    # open the previously created file
    opfp = open(opdat, 'w')

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
      p_est = nelmin.minimize(self.obj, params, args=(invdata,))[0]
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
  """Integration glue for calling external LIBRAT programs"""
  def __init__(self):
    me=self.__class__.__name__ +'::'+VLAB.me()
    VLAB.logger.info('%s: constructor completed...' % me)
  def doProcessing(self, pm, args):
    """do processing for LIBRAT processor"""
    me=self.__class__.__name__ +'::'+VLAB.me()

    if (pm != None):
      pm.beginTask("Computing BRF...", 10)
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
      'cwd'     : '%HOMEDRIVE%%HOMEPATH%\\.beam\\beam-vlab\\auxdata\\librat_windows\\src\\start',
      'exe'     : '%HOMEDRIVE%%HOMEPATH%\\.beam\\beam-vlab\\auxdata\\librat_windows\\src\\start\\ratstart.exe',
      'cmdline' : [
        '-sensor_wavebands', 'wavebands.dat', '-m', '100',
        '-sun_position', '0', '0', '10', 'test.obj'],
      'stdin'   : '%HOMEDRIVE%%HOMEPATH%\\.beam\\beam-vlab\\auxdata\\librat_windows\\src\\start\\starttest.ip',
      'stdout'  : None,
      'stderr'  : None,
      'env'     : {
        'BPMS'  : '%HOMEDRIVE%%HOMEPATH%\\.beam\\beam-vlab\\auxdata\\librat_windows'
     }}
    }
    VLAB.doExec(cmd)

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

    args = {
            'v' : True,
         'nice' : '19',
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

    args = {
         'brdf' : True,
       'angles' : 'angles.rpv.2.dat',
       'wbfile' : 'wb.MSI.dat',
        'bands' : (4., 7.),
         'root' : 'rpv.rami/result.HET01_DIS_UNI_NIR_20.obj'
    }
    # plot.main(args)

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
      'opdir' : 'rami.TOA',
          'v' : True,
        'rpv' : 'rpv.laegeren/result.laegeren.obj.lai.1.brdf.dat.3params.dat',
       'plot' : 'rami.TOA/rpv.rami.libradtran.dat.all',
        'lat' : 50,
        'lon' : 0,
       'time' : "2013 0601 12 00 00"
    }
    # dolibradtran.main(args)

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
    from java.lang         import RuntimeException
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
          raise RuntimeException('unknown processor: <' + processor + '>')
  
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
