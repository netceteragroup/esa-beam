#!/usr/bin/env python

import sys, os, argparse
import numpy as np

def main():


	# sun angles for eg UK (lat 51' 0" 0' 0") 1 Jun 2013 10:30 am
	# sun_position -lat 51 -lon 0 -date 01:05:2013 -t 10:30:00
	# va, sz, sa = 0, 34, 141 
	
	vz, va, sz, sa = 0, 0, 34, 141
	nsamples = 1000
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
	if options.sz: sz = options.sz
	if options.sa: sa = options.sa
	if options.nsamples: nsamples = np.float(options.nsamples)

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
		vz, sz, sa = 70., 30, 90
		angles = np.zeros((vaa.size,4))
		vaa = np.arange(vamin,vamax+vastep,vastep)
		angles[:,0] = vz
		angles[:,1] = vaa
		angles[:,2]= sz
		angles[:,3]= sa
	elif options.multiple:
		# this one for multiple vz, va angles
		vzmin, vzmax, vzstep = -70, 70, 10
		vamin, vamax, vastep = 0, 340, 20
		vzz = np.arange(vzmin,vzmax+vzstep,vzstep)
		vaa = np.arange(vamin,vamax+vastep,vastep)
		angles = np.zeros((vzz.size*vaa.size,4))
		for n, va in enumerate(vaa):
			angles[n*vzz.size:(n+1)*vzz.size,0] = vzz
			angles[n*vzz.size:(n+1)*vzz.size,1] = va
			angles[n*vzz.size:(n+1)*vzz.size,2] = sz
			angles[n*vzz.size:(n+1)*vzz.size,3] = sa
	elif options.random:
		# random n samples of COSINE-WEIGHTED view and illum angles
		# In order that we get the required number, nsamples,  AND can disregard all those with
		# vz > 70 and vz < -70 (not valid for RPV) do twice as many as you need, discard
		# all those outside the angle range and then take the first n.
		nn = nsamples*2
		# view angles first
		u1 = np.random.rand(nn)
		r = np.sqrt(u1)
		theta = 2. * np.pi * np.random.rand(nn)
        
		x = r * np.cos(theta)
		y = r * np.sin(theta)
		z = np.sqrt(1 - u1)
                
		vz = np.arccos(z)
		va = np.arctan(y/x)
		
		# if x -ve then vz -ve
		vz[np.where(x<0)] *= -1.
		
		# sun angles
		
		u1 = np.random.rand(nn)
		r = np.sqrt(u1)
		theta = 2. * np.pi * np.random.rand(nn)
        
		x = r * np.cos(theta)
		y = r * np.sin(theta)
		z = np.sqrt(1 - u1)
		#np.savetxt('rpv.angles.test.plot',np.transpose([x,y,z]),fmt='%.6f')
		sz = np.arccos(z)
		sa = np.arctan(y/x)

		
		# if x -ve then sz -ve
		sz[np.where(x<0)] *= -1.
				
		angles = [np.rad2deg(vz), np.rad2deg(va), np.rad2deg(sz), np.rad2deg(sa)]
		angles = np.transpose(np.array(angles))
		angles = angles[ np.where((angles[:,0] >-70) & (angles[:,0]<=70) & (angles[:,2] >-70) & (angles[:,2]<=70))]
		
		# now take the first n
		angles = angles[0:nsamples,]
		x = np.sin(np.deg2rad(angles[:,0])) * np.cos(np.deg2rad(angles[:,1]))
		y = np.sin(np.deg2rad(angles[:,0])) * np.sin(np.deg2rad(angles[:,1]))
		z = np.cos(np.deg2rad(angles[:,0]))
		#np.savetxt('rpv.angles.test',angles,fmt='%.6f')
		#np.savetxt('rpv.angles.test.plot',np.transpose([x,y,z]),fmt='%.6f')
		
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
	parser.add_argument("-multiple", action="store_true", help="multiple")
	parser.add_argument("-random", action="store_true", help="random")
	parser.add_argument("-n", dest="nsamples", help="random")
	parser.add_argument("-xdims", dest="xdims", nargs=3, help="xdims")
	parser.add_argument("-ydims", dest="ydims", nargs=3, help="ydims")
	parser.add_argument("-z", dest="z", help="z")
	parser.add_argument("-sz", dest="sz", help="sz")
	parser.add_argument("-sa", dest="sa", help="sa")
	options = parser.parse_args()
	main()
