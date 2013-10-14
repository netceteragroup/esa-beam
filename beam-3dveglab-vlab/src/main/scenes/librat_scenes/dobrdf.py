#!/usr/bin/env python

import sys, os, argparse, datetime, stat
import numpy as np
from matplotlib.pyplot import *
import matplotlib.pyplot as plt

# need this module ~/bin/python: camera and light setups
import libratsetup as rat


def replace_all(text, dic):
	for i, j in dic.iteritems():
		text = text.replace(i,j)
	return text


def checkFile(fname):
	try:
		fp = open(fname, 'rw')
		return fp
	except IOError as e:
		# for 3.2 print("({})".format(e))
		# print("%s: ({0})".format(e)%(sys.argv[0]))
		print("({})".format(e))
		sys.exit(1)


def openFileIfNotExists(filename):
	# create if it doesn't exist, truncate of it does
	try:
		fd = os.open(filename, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_TRUNC)
	except:
		return None
	fobj = os.fdopen(fd,'w')
	return fobj


def main():

	# set up defaults
	_UNIX_ = 1
	INFINITY = 1000000
	lightfile = "light.dat"
	camfile = "camera.dat"
	wbfile = "wb.test.dat"
	anglefile = "angles.dat"
	objfile = "veglab_test.obj"

	blacksky = ''
	npixels = 1000000
	image = 1
	hips = 1
	rpp = 1
	fov = False
	sorder = 100
	nice = ''
	niceLevel = 19
	boom = 100000
	ideal = False
	samplingPattern = False
	mode = 'scattering order'
	opdir = "brdf"
	result_root = 'result'
	camera_root = 'camera'
	light_root = 'light'
	grabme_root = 'grabme'
	# top of canopy height so brdf simulations pivot about x, y, z
	look_xyz = (150, 150, 35)
	location = False
	vz, va, sz, sa = -1, -1, -1, -1

	if options.wbfile: wbfile = options.wbfile
	if options.anglefile: anglefile = options.anglefile
	if options.lookFile: lookFile = options.lookFile
	if options.objfile: objfile = options.objfile
	if options.opdir: opdir = options.opdir
	if options.npixels: npixels = options.npixels
	if options.rpp: rpp = options.rpp
	if options.boom: boom = options.boom
	if options.ideal: ideal = np.array(options.ideal,dtype=float)
	if options.fov: fov = options.fov
	if options.mode: mode = options.mode
	if options.look: look_xyz = np.array(options.look,dtype=float)
	if options.result: result_root = options.result
	if options.camera: camera_root = options.camera
	if options.light: light_root = options.light
	if options.grabme: grabme_root = options.grabme
	if options.sorder: sorder = options.sorder
	if options.blacksky:
		blacksky = '-blacksky'
	if options.niceLevel: 
		if _UNIX_:
			nice = 'nice +' + np.str(niceLevel)
                        # temporarily disable
			nice = ''
		else:
			nice = ''
	if options.samplingPattern:
		samplingPattern = options.samplingPattern
		if samplingPattern != 'circular':
			sys.stderr.write("%s: samplingPattern %s not supported - only circular currently\n"%(sys.argv[0],samplingPattern))
			sys.exit([True])
	
	try:
		os.stat(opdir)
	except:
		os.mkdir(opdir)
	
	angfp = checkFile(anglefile)
	wbfp = checkFile(wbfile)
	objfp = checkFile(objfile)
	

	# vz va sz sa
	ang = np.genfromtxt(anglefile,unpack=True).transpose()
	
	if options.lookFile:
		# use this as locations as well as loo at for DHP
		lookFile = options.lookFile
		lookfp = checkFile(lookFile)
		look_xyz = np.genfromtxt(options.lookFile,unpack=True).transpose()
	
	#if look_xyz.size == 3:
        if np.array(look_xyz).size == 3:
		look_xyz = ((look_xyz),)
	

	if ang.size < 4 or (ang.size > 4 and ang.shape[1] != 4):
		sys.stderr.write("%s: wrong number of fields (%i) in %s - should be 4\n"%(sys.argv[0], ang.shape[1], anglefile))
		sys.exit([True])
	
	
	if ang.size == 4:
		ang = ((ang),)
	

	for n, a in enumerate(ang):
		vz = a[0]
		va = a[1]
		sz = a[2]
		sa = a[3]
		
		
		for ll, look in enumerate(look_xyz):
			
			lightfile = os.path.join(opdir, light_root + '_sz_' + str(sz) + '_sa_' + str(sa) + '_dat')
			# does the file exist already? Only create if not
			ligfp = openFileIfNotExists(lightfile)
			if ligfp != None:
				l = rat.light(sz=sz,sa=sa)
				l.printer(file=lightfile)
			
			
			rooty = objfile + '_vz_' + np.str(vz) + '_va_' + np.str(va) + '_sz_' + np.str(sz) + '_sa_' + np.str(sa) + '_xyz_' + np.str(look[0]) + '_' + np.str(look[1]) + '_' + np.str(look[2]) + '_wb_' + wbfile
			grabme = os.path.join(opdir, grabme_root + '.' + rooty)
		
			if options.dhp:
				location = np.copy(look)
				look[2] = INFINITY
				sampling = "circular"
			
			# critical to see if it exists or not and only do the processing if it does
			if not os.path.exists(grabme):
				grabfp = openFileIfNotExists(grabme)
				logfile = grabme + '.log'
				camfile = os.path.join(opdir, camera_root + '.' + rooty)
				oproot = os.path.join(opdir, result_root + '.' + rooty)
				if options.image:
					# do image
					if options.hips: 
						imfile = oproot + '.hips'
					else:
						# default o/p is BEAM flat binary
						imfile = oproot + '.bim'
					c = rat.cam(name='simple camera', vz=vz, va=va, integral=oproot, integral_mode=mode, image=imfile, nPixels=npixels, rpp=rpp, boom=boom, ideal=ideal, look=look, location=location, fov=fov, samplingPattern=samplingPattern)
				else:
					# no image
					c = rat.cam(name='simple camera', vz=vz, va=va, integral=oproot, integral_mode=mode, nPixels=npixels, rpp=rpp, boom=boom, ideal=ideal, look=look, location=location, fov=fov, samplingPattern=samplingPattern)
				
				#c = rat.cam(name='simple camera', vz=vz, va=va, integral=oproot, integral_mode=mode, image=imfile, nPixels=npixels, rpp=rpp, boom=boom, ideal=ideal, look=look, fov=fov)
				c.printer(file=camfile)
				cmd = '(echo 14 ' + camfile + ' ' + lightfile + ' | ' + nice + ' start -RATv -m '+ np.str(sorder) + ' ' + blacksky +' -RATsensor_wavebands ' + wbfile + ' ' + objfile + ' > ' + logfile + ' 2>&1)\n'
				grabfp.write('#!/bin/sh\n')
				grabfp.write("#host: %s\n"%os.environ['HOSTNAME'])
				grabfp.write("# %s\n"%datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
				grabfp.write("PATH=%s:%s/.beam/beam-vlab/auxdata/librat_lin64/bin/x86_64;export PATH\n"%(os.environ['PATH'], os.environ['HOME']))
				grabfp.write("LD_LIBRARY_PATH=%s/.beam/beam-vlab/auxdata/librat_lin64/src/lib/;export LD_LIBRARY_PATH\n"%os.environ['HOME'])
				grabfp.write(cmd)
				grabfp.flush()
				os.chmod(grabme,stat.S_IRWXU|stat.S_IRGRP|stat.S_IROTH)
				grabfp.close()
				if options.v:
					sys.stderr.write('%s: doing file %s\n'%(sys.argv[0],grabme))
				#sys.stderr.write('%s: written grabme file %s\n'%(sys.argv[0],grabme))	
				#sys.exit()
				os.system(grabme)


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-opdir", dest="opdir", help="opdir")
	parser.add_argument("-obj", dest="objfile", help="obj file")
	parser.add_argument("-angles", dest="anglefile", help="angles file", metavar="FILE")
	parser.add_argument("-lookFile", dest="lookFile", help="look location file", metavar="FILE")
	parser.add_argument("-dhp", action="store_true", help="do DHP")
	parser.add_argument("-fov", dest="fov", help="fov")
	parser.add_argument("-c", "--camera",dest="camera", help="camera file", metavar="FILE")
	parser.add_argument("-l", "--light",dest="light", help="light file", metavar="FILE")
	parser.add_argument("-wb", dest="wbfile", help="wb file", metavar="FILE")
	parser.add_argument("-v", action="store_true", help="verbose on")
	parser.add_argument("-blacksky", action="store_true", help="blacksky on")
	parser.add_argument("-npixels", dest="npixels", help="npixels")
	parser.add_argument("-rpp", dest="rpp", help="rpp")
	parser.add_argument("-sorder", dest="sorder", help="sorder")
	parser.add_argument("-nice", dest="niceLevel", help="nice level")
	parser.add_argument("-boom", dest="boom", help="boom")
	parser.add_argument("-ideal", dest="ideal", nargs=2, help="ideal AREA")
	parser.add_argument("-samplingPattern", dest="samplingPattern", help="sampling pattern")
	parser.add_argument("-mode", dest="mode", help="mode")
	parser.add_argument("-look", dest="look", nargs=3, help="look XYZ")
	parser.add_argument("-result", dest="result", help="result root name")
	parser.add_argument("-light", dest="light", help="light root name")
	parser.add_argument("-camera", dest="camera", help="camera root name")
	parser.add_argument("-grabme", dest="grabme", help="grabme root name")
	parser.add_argument("-hips", action="store_true", help="HIPS image o/p")
	parser.add_argument("-image", action="store_true", help="do image o/p")
	options = parser.parse_args()
	main()
