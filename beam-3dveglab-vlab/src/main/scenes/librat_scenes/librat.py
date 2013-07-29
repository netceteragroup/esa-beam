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
# This is a (subset of) jython re-implementation of python code written by Mat Disney - for original code see
#  https://github.com/netceteragroup/esa-beam/tree/master/beam-3dveglab-vlab/src/main/scenes/librat_scenes
# 

import sys

from java.util import Random
from java.lang import Math

################
# to be merged into VLAB class...
class VLAB:
  def me():
    nm = ''
    try:
      raise ZeroDivisionError
    except ZeroDivisionError:
      nm = sys.exc_info()[2].tb_frame.f_back.f_code.co_name
    return nm+'()'
  me = staticmethod(me)
  def checkFile(self, fname):
    try:
      fp = open(fname, 'rw')
      return fp
    except IOError, e:
      # for 3.2 print("({})".format(e))
      # print("%s: ({0})".format(e)%(sys.argv[0]))
      print("({})".format(e))
      sys.exit(1)
  checkFile = staticmethod(checkFile)
  def frange(end, start=0, inc=0):
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
    True
  def savetxt(a,b,fmt):
    fh = open(a, 'w')
    if not fmt:
      fmt = '%s'
    for row in b:
      for element in row:
        fh.write(fmt % element + ' ') 
      fh.write('\n')
    fh.close()
  savetxt = staticmethod(savetxt)

################
class dobrdf:
  def _writeCamFile(self, camFile, args):
    cdata = 'camera {\n' \
   + ' camera.name                     = "%s";\n' % args['cam_camera'] \
   + ' geometry.zenith                 = %s;\n'   % args['vz'] \
   + ' geometry.azimuth                = %s;\n'   % args['va'] \
   + ' result.image                    = "%s";\n' % args['result_image'] \
   + ' result.integral.mode            = "%s";\n' % args['result_integral_mode'] \
   + ' result.integral                 = "%s";\n' % args['result_integral'] \
   + ' samplingCharacteristics.nPixels = %s;\n'   % args['npixels'] \
   + ' samplingCharacteristics.rpp     = %s;\n'   % args['rpp'] \
   + ' geometry.idealArea              = %s;\n'   % ', '.join(map(str, map('%.1f'.__mod__, args['ideal']))) \
   + ' geometry.lookat                 = %s;\n'   % ', '.join(map(str, map('%.1f'.__mod__, args['look_xyz']))) \
   + ' geometry.boomlength             = %s;\n'   % args['boom']
    if args['perspective']:
      cdata += ' geometry.perspective            = %s;\n' % args['perspective']
    if args['twist']:
      cdata += ' geometry.twist                  = %s;\n' % args['twist']
    if args['fov']:
      cdata += ' geometry.fov                    = %s;\n' % args['fov']
    if args['lidar']:
      cdata += ' lidar.binStep                   = %s;\n' % args['binStep']
      cdata += ' lidar.binStart                  = %s;\n' % args['binStart']
      cdata += ' lidar.nBins                     = %s;\n' % args['nBins']
    cdata += '}'
    writer = BufferedWriter(FileWriter(camFile.getCanonicalPath()))
    writer.write(cdata); writer.close()

  def _writeLightFile(self, lightFile, args):
    ldata = 'camera {\n' \
   + ' camera.name                     = "%s";\n' % args['light_camera'] \
   + ' geometry.zenith                 = %.1f;\n' % args['sz'] \
   + ' geometry.azimuth                = %.1f;\n' % args['sa'] \
   + ' geometry.twist                  = %.1f;\n' % args['twist']
    key = "sideal"
    if key in args:
      ldata += ' geometry.ideal                  = %s;\n' % ', '.join(map(str, map('%.1f'.__mod__, args[key])))
    key = "slook_xyz"
    if key in args:
      ldata += ' geometry.lookat                 = %s;\n' % ', '.join(map(str, map('%.1f'.__mod__, args[key])))
    key = "sboom"
    if key in args:
      ldata += ' geometry.boom                   = %s;\n' % args[key]
    key = "sperspective"
    if key in args:
      ldata += ' geometry.perspective            = %s;\n' % args[key]
    key = "sfov"
    if key in args:
      ldata += ' geometry.fov                    = %s;\n' % args[key]
    ldata += '}'
    writer = BufferedWriter(FileWriter(lightFile.getCanonicalPath()))
    writer.write(ldata); writer.close()

  def _writeInputFile(self, inpFile, lightFile, camFile):
    idata = '14' \
   + ' ' \
   + camFile.getCanonicalPath() \
   + ' ' \
   + lightFile.getCanonicalPath()
    writer = BufferedWriter(FileWriter(inpFile.getCanonicalPath()))
    writer.write(idata); writer.close()

  def _writeGrabFile(self, grabFile, args):
    gFilePath = grabFile.getCanonicalPath()
    gdata = """
cmd = {
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
    'cwd'     : '%HOMEDRIVE%%HOMEPATH%\\.beam\\beam-vlab\\auxdata\\librat_scenes',
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
   ('5', args['wbfile'], args['objfile'], gFilePath+'.inp', gFilePath+'.out.log', gFilePath+'.err.log', \
    '5', args['wbfile'], args['objfile'], gFilePath+'.inp', gFilePath+'.out.log', gFilePath+'.err.log')
    gdata = replaced.replace("\x81", "%")
    gdata += 'VLAB.doExec(cmd)\n'
    writer = BufferedWriter(FileWriter(gFilePath))
    writer.write(gdata); writer.close()

  def main(self, args):
    me=self.__class__.__name__ +'::'+VLAB.me()
    print '======> ', me
    for a in args:
      print a, " -> ", args[a]

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
      else:
        q[a] = args[a]

################
class dolibradtran:
  def main(self, args):
    me=self.__class__.__name__ +'::'+VLAB.me()
    print '======> ', me
    for a in args:
      print a, " -> ", args[a]

################
class dolibradtran:
  def defaultLRT(self, fp, solar_file, dens_column, correlated_k, rt_solver, rpvfile, deltam, nstr, zout, output_user, quiet):
    True
  def main(self, args):
    me=self.__class__.__name__ +'::'+VLAB.me()
    print '======> ', me
    for a in args:
      print a, " -> ", args[a]

################
class drivers:
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

      # deubg: a particular seed for reproducibility
      randgen = Random(17)

      # view angles first
      u1    = [randgen.nextFloat() for i in range(nn)]
      r     = [Math.sqrt(i)        for x in u1]
      theta = [2.*Math.PI*x for x in [randgen.nextFloat() for i in range(nn)]]


      x  = [r[i] * Math.cos(theta[i])   for i in range(nn)]
      y  = [r[i] * Math.sin(theta[i])   for i in range(nn)]
      z = [Math.sqrt(1 - u1[i])         for i in range(nn)]

      q['vz'] = [Math.acos(z[i])      for i in range(nn)]
      q['va'] = [Math.atan(y[i]/x[i]) for i in range(nn)]

      # if x -ve then vz -ve
      for i in range(nn):
        if (x[i]<0):
          q['vz'][i] = q['vz'][i] * -1.

      # sun angles
      u1    = [randgen.nextFloat() for i in range(nn)]
      r     = [Math.sqrt(i)        for x in u1]
      theta = [2.*Math.PI*x for x in [randgen.nextFloat() for i in range(nn)]]

      x  = [r[i] * Math.cos(theta[i])   for i in range(nn)]
      y  = [r[i] * Math.sin(theta[i])   for i in range(nn)]
      z = [Math.sqrt(1 - u1[i])         for i in range(nn)]

      #np.savetxt('rpv.angles.test.plot',np.transpose([x,y,z]),fmt='%.6f')
      q['sz'] = [Math.acos(z[i])      for i in range(nn)]
      q['sa'] = [Math.atan(y[i]/x[i]) for i in range(nn)]

      # if x -ve then sz -ve
      for i in range(nn):
        if (x[i]<0):
          q['sz'][i] = q['sz'][i] * -1.

      vzdeg = [Math.toDegrees(q['vz'][i]) for i in range(nn)]
      vadeg = [Math.toDegrees(q['va'][i]) for i in range(nn)]
      szdeg = [Math.toDegrees(q['sz'][i]) for i in range(nn)]
      sadeg = [Math.toDegrees(q['sa'][i]) for i in range(nn)]
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

class plot:
  def main(self, args):
    me=self.__class__.__name__ +'::'+VLAB.me()
    print '======> ', me
    for a in args:
      print a, " -> ", args[a]
  def spec_plot(self,spec,wbspec):
    True
  def brdf_plot(self,root,angfile,wbfile):
    True

class rpv_invert:
  def main(self, args):
    me=self.__class__.__name__ +'::'+VLAB.me()
    print '======> ', me
    for a in args:
      print a, " -> ", args[a]


################

# Test

drivers      = drivers()
dobrdf       = dobrdf()
plot         = plot()
rpv_invert   = rpv_invert()
dolibradtran = dolibradtran()

args = {
   'random' : True,
   'n'      : 1000,
   'angles' : 'angles.rpv.2.dat',
   'look'   : 'look.1.dat',
}
drivers.main(args)

args = {
        'v' : True,
     'nice' : 19, 
      'obj' : 'HET01_DIS_UNI_NIR_20.obj',
     'hips' : True,
       'wb' : 'wb.MSI.dat',
    'ideal' : '80 80',
     'look' : '0 0 0',
      'rpp' : 4,
  'npixels' : 10000,
     'boom' : 786000,
   'angles' : 'angles.rpv.2.dat',
    'opdir' : 'rpv.rami'
}
dobrdf.main(args)

args = {
     'brdf' : True,
    'angles': 'angles.rpv.2.dat',
     'root' : 'rpv.rami.2/result.HET01_DIS_UNI_NIR_20.obj'
}
plot.main(args)

args = {
    'three' : True,
        'v' : True,
     'plot' : True,
     'data' : 'rpv.rami.2/result.HET01_DIS_UNI_NIR_20.obj.brdf.dat',
'paramfile' : 'rpv.rami.2/result.HET01_DIS_UNI_NIR_20.obj.brdf.dat.3params.dat',
 'plotfile' : 'rpv.rami.2/result.HET01_DIS_UNI_NIR_20.obj.brdf.3params'
}
rpv_invert.main(args)

args = {
  'opdir' : 'rami.TOA',
      'v' : True,
    'rpv' : 'rpv.rami.2/result.HET01_DIS_UNI_NIR_20.obj.brdf.dat.3params.dat',
   'plot' : 'rami.TOA/rpv.rami.libradtran.dat.all'
}
dolibradtran.main(args)
