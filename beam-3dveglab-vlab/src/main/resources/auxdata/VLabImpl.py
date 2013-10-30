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
      def __init__(self, nm, strm):
        self.nm=nm; self.strm=strm
      def run(self):
        """helper class for slurping up child streams"""
        from java.io import BufferedReader
        from java.io import InputStreamReader
        line = None; br = BufferedReader(InputStreamReader(self.strm))
        line = br.readLine()
        while (line != None):
          VLAB.logger.info('%s %s' %(self.nm, line.rstrip()))
          line = br.readLine()
        br.close()
  else:
    def helper(nm, strm):
      """helper class for slurping up child streams"""
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
    cmdLine.append(VLAB.expandEnv(cmd['exe']))
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
      t1 = Thread(VLAB.Helper("out", proc.getInputStream()))
      t2 = Thread(VLAB.Helper("err", proc.getErrorStream()))
      t1.start(); t2.start()
      bw = BufferedWriter(OutputStreamWriter(proc.getOutputStream()))
      if 'stdin' in cmd and cmd['stdin'] != None:
        for line in open(VLAB.expandEnv(cmd['stdin']),'r'):
          bw.write(line)
        bw.close()
      exitCode = proc.waitFor()
      t1.join(); t2.join()
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
      from lbfgsb import DifferentiableFunction, FunctionValues, Bound
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
    f0 = f(*((xk,) + args))
    grad = [0. for i in xrange(len(xk))]
    ei = [0. for i in xrange(len(xk))]
    for k in xrange(len(xk)):
      ei[k] = 1.0
      d = map(lambda i : i * epsilon, ei)
      grad[k] = (f(*((xk + d,) + args)) - f0) / d[k]
      ei[k] = 0.0
    return grad
  approx_fprime = staticmethod(approx_fprime)


################################################################

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


class DUMMY:
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

class DART:
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

class LIBRAT:
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
    VLAB.logger.info('%s: running...' % me)
  
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
    # BEAM-specific code from here to the end...
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
