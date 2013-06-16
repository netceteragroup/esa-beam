#!/usr/bin/env python

import sys, os, argparse
import numpy as np

def main():


	# sun angles for eg UK (lat 51' 0" 0' 0") 1 Jun 2013 10:30 am
	# sun_position -lat 51 -lon 0 -date 01:05:2013 -t 10:30:00
	# va, sz, sa = 0, 34, 141 
	
	vz, va, sz, sa = 0, 0, 34, 141
	
	xdims = (0, 300, 30)
	ydims = (0, 300, 30)
	z = 0
	
	angFile = 'angles.dat'
	lookFile = 'look.dat'

	if options.lookFile: lookFile = options.lookFile
	if options.angFile: angFile = options.angFile
	if options.xdims: xdims = np.array(options.xdims,dtype=float)
	if options.ydims: ydims = np.array(options.ydims,dtype=float)
	if options.z: z = options.z

	if options.msi:
		# across whole swath
		# zmin, vzmax, vzstep = -22, 54, 4
		angles = np.zeros(4)
		angles = (vz, va, sz, sa)
	elif options.olci:
		vzmin, vzmax, vzstep = -22, 54, 4
		vzz = np.arange(vzmin,vzmax+vzstep,vzstep)
		angles = np.zeros((vzz.size,4))
		angles[:,0] = vzz
		angles[:,1] = va
		angles[:,2]= sz
		angles[:,3]= sa	
	elif options.around:
		vamin, vamax, vastep = 0, 360, 10
		vaa = np.arange(vamin,vamax+vastep,vastep)
		vz, sz, sa = 0., 30, 90
		angles = np.zeros((vaa.size,4))
		vaa = np.arange(vamin,vamax+vastep,vastep)
		angles[:,0] = vz
		angles[:,1] = vaa
		angles[:,2]= sz
		angles[:,3]= sa
	elif options.multiple:
		# this one for multiple vz, va angles
		vzmin, vzmax, vzstep = -70, 70, 5
		vamin, vamax, vastep = 0, 180, 30
		vzz = np.arange(vzmin,vzmax+vzstep,vzstep)
		vaa = np.arange(vamin,vamax+vastep,vastep)
		angles = np.zeros((vzz.size*vaa.size,4))
		for n, va in enumerate(vaa):
			angles[n*vzz.size:(n+1)*vzz.size,0] = vzz
			angles[n*vzz.size:(n+1)*vzz.size,1] = va
			angles[n*vzz.size:(n+1)*vzz.size,2] = sz
			angles[n*vzz.size:(n+1)*vzz.size,3] = sa
	else:
		# default
		vzmin, vzmax, vzstep = -70, 70, 5
		vzz = np.arange(vzmin,vzmax+vzstep,vzstep)
		angles = np.zeros((vzz.size,4))
		angles[:,0] = vzz
		angles[:,1] = va
		angles[:,2]= sz
		angles[:,3]= sa
	
	np.savetxt(angFile,angles,fmt='%.1f')
	
	
	if options.lookFile:
		x = np.arange(xdims[0],xdims[1],xdims[2])
		y = np.arange(ydims[0],ydims[1],ydims[2])
		look = np.zeros((x.size*y.size,3))
		for n, yy in enumerate(y):
			look[n*x.size:(n+1)*x.size,0] = x
			look[n*x.size:(n+1)*x.size,1] = yy
			look[n*x.size:(n+1)*x.size,2] = z
		np.savetxt(lookFile,look,fmt='%.1f')

		
if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-angles", dest="angFile", help="angles file", metavar="FILE")
	parser.add_argument("-look", dest="lookFile", help="lookFile file", metavar="FILE")
	parser.add_argument("-msi", action="store_true", help="msi flag")
	parser.add_argument("-olci", action="store_true", help="olci flag")
	parser.add_argument("-around", action="store_true", help="around")
	parser.add_argument("-multiple", action="store_true", help="around")
	parser.add_argument("-xdims", dest="xdims", nargs=3, help="xdims")
	parser.add_argument("-ydims", dest="ydims", nargs=3, help="ydims")
	parser.add_argument("-z", dest="z", help="z")
	options = parser.parse_args()
	main()
