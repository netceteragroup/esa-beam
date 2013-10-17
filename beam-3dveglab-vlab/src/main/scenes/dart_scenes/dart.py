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

import sys, math

class VLAB:
  def me():
    nm = ''
    try:
      raise ZeroDivisionError
    except ZeroDivisionError:
      nm = sys.exc_info()[2].tb_frame.f_back.f_code.co_name
    return nm+'()'
  me = staticmethod(me)

class dobrdf:
  def main(self, args):
    me=self.__class__.__name__+'::'+VLAB.me()
    print '=======> ', me
    for a in args:
      print a, " -> ", args[a]

class plot:
  def main(self, args):
    me=self.__class__.__name__+'::'+VLAB.me()
    print '=======> ', me
    for a in args:
      print a, " -> ", args[a]

class rpv_invert:
  def main(self, args):
    me=self.__class__.__name__+'::'+VLAB.me()
    print '=======> ', me
    for a in args:
      print a, " -> ", args[a]

class dolibradtran:
  def main(self, args):
    me=self.__class__.__name__+'::'+VLAB.me()
    print '=======> ', me
    for a in args:
      print a, " -> ", args[a]

# Test

dobrdf = dobrdf()
plot = plot()
rpv_invert = rpv_invert()
dolibradtran = dolibradtran()

args = {
         'v' : True,
        'wb' : 'Sequence_MSI.xml',
    'outdir' : 'outdir'
}
dobrdf.main(args)

args = {
         'v' : True,
        'wb' : 'Sequence_MSI.xml',
    'angles' : 'angle.rpv.cosDOM.dat',
   'rootdir' : 'rpv.rami/result.HET01_DIS_UNI_NIR_20'
}
plot.main(args)

args = {
         'v' : True,
     'three' : True,
      'plot' : True,
  'datafile' : 'datafile',
 'paramfile' : 'paramfile',
  'plotfile' : 'plotfile'
}
rpv_invert.main(args)

args = {
         'v' : True,
  'plotfile' : 'plotfile',
       'lat' : 50,
       'lon' : 0,
      'time' : '2013 0601 12 00 00',
    'outdir' : 'outdir'
}
dolibradtran.main(args)
