#!/usr/bin/env python

import sys, os, argparse, glob
import numpy as np
import matplotlib.pyplot as plt
import itertools


def spec_plot(spec,wbspec):

	wb = np.genfromtxt(wbspec,unpack=True)[1]
	op1 = spec + '.plot.png'

	# whole spectrum
	data = np.genfromtxt(spec,unpack=True)
	refl = data[1:,].sum(axis=1)
	fig = plt.figure()
	ax = fig.add_subplot(1, 1, 1)
	ax.set_xlim((400, 2500))
	ax.set_ylim((0, 0.4))
	ax.set_xlabel('$\lambda$(nm)',fontsize=14)
	ax.set_ylabel(r'$\rho$',fontsize=20)
	ax.plot(wb,refl,'r-',linewidth=2)
	#plt.show()
	sys.stderr.write('%s: saving to: %s\n'%(sys.argv[0],op1))
	plt.savefig(op1,bbox_inches='tight')
	plt.close()
	
	
	# now to all the other ones
	for n, w in enumerate(wb):
		sys.stderr.write("%s: plotting band %i\n"%(sys.argv[0],n))
		op = spec + 'plot.band_' + np.str(n) + '_plot.png'
		fig = plt.figure()
		ax = fig.add_subplot(1, 1, 1)
		ax.set_xlim((400, 2500))
		ax.set_ylim((0, 0.4))
		ax.set_xlabel('$\lambda$(nm)',fontsize=14)
		ax.set_ylabel(r'$\rho$',fontsize=20)
		ax.plot(wb,refl,'r-',linewidth=2)
		ax.plot(w,refl[n],'ko',markersize=8)
		#plt.show()
		sys.stderr.write('%s: saving to: %s\n'%(sys.argv[0],op))
		plt.savefig(op,bbox_inches='tight')
		plt.close()		
	

def brdf_plot(root,angfile,wbfile):
	colours = itertools.cycle(['r','g','b','c','y','m','k'])
	markers = itertools.cycle(['o','s','v'])
	opdat = root + '.brdf.dat'
	opplot = root + '.brdf.png'
	ang = np.genfromtxt(angfile,unpack=True)
	wb = np.genfromtxt(wbfile,unpack=True)[1]
	result = np.zeros((ang.shape[1],wb.shape[0]))
	
	ff = root + '*.direct'
	
	for f in glob.glob(ff):
		fsplit = f.split('_')
		vz = f.split('_')[fsplit.index('vz')+1]
		va = f.split('_')[fsplit.index('va')+1]
		sz = f.split('_')[fsplit.index('sz')+1]
		sa = f.split('_')[fsplit.index('sa')+1]
		
		#print f, vz, np.where(ang==np.float(vz))[1][0]
		data = np.genfromtxt(f,unpack=True)
		refl = data[1:,].sum(axis=1)
		result[np.where(ang==np.float(vz))[1][0]] = refl
		result[np.where( (ang[0]==np.float(vz)) & (ang[1]==np.float(va)) & (ang[2]==np.float(sz)) & (ang[3]==np.float(sa)))] = refl

	fig = plt.figure()
	ax = fig.add_subplot(1, 1, 1)
	ax.set_xlim((ang[0].min()-2, ang[0].max()+2))
	ax.set_ylim((0, 0.4))
	ax.set_xlabel('view zenith angle (deg.)',fontsize=14)
	ax.set_ylabel(r'$\rho$',fontsize=20)
	for b in [3, 7]:
		ax.plot(ang[0],result[0:,b],c=colours.next(),marker=markers.next(),linestyle='None', label='waveband: %.1f'%wb[b])
		#ax.plot(ang[0],result[0:,b],'ko',markersize=5)
	
	ax.legend(loc=1)
	#plt.show()
	sys.stderr.write('%s: plotting brdf to: %s\n'%(sys.argv[0],opplot))
	sys.stderr.write('%s: saving brdf data to: %s\n'%(sys.argv[0],opdat))
	outdata = np.zeros((result.shape[0],result.shape[1]+ang.shape[0]))
	outdata[0:result.shape[0],0:ang.shape[0]] = ang.transpose()
	outdata[0:result.shape[0],ang.shape[0]:result.shape[1]+ang.shape[0]] = result
	np.savetxt(opdat,outdata,fmt='%.4f')
	plt.savefig(opplot)
	#plt.close()

def tree_plot():
	ifile = 'treereconstruction_and_spectra/treemodel/tree_model/crown_dist.dat'
	# $1, $3
	data = np.genfromtxt(ifile,unpack=True)
	op = ifile + '.png'
	fig = plt.figure()
	ax = fig.add_subplot(1, 1, 1)
	#ax.set_xlim((ang[0].min()-2, ang[0].max()+2))
	#ax.set_ylim((0, 0.4))
	ax.set_xlabel('Tree number',fontsize=14)
	ax.set_ylabel('log(Number in scene)',fontsize=14)
	ax.plot(data[0],np.log(data[2]),'ko',markersize=8)
	#plt.show()
	sys.stderr.write('%s: plotting brdf to: %s\n'%(sys.argv[0],op))
	plt.savefig(op)

	
def main():

	spec = 'SPECTRAL_TEST/result.laegeren.obj_vz_0.0_va_0.0_sz_34.0_sa_141.0_xyz_150.0_150.0_700.0_wb_wb.full_spectrum.dat.direct'
	wbfile = 'wb.full_spectrum.dat'
	
	root = 'OLCI_brdf.scene/result.laegeren.obj'
	angfile = 'angles.OLCI.dat'
	#wbfile = 'wb.OLCI.dat'
	wbfile = 'wb.MSI.dat'
	
	spec = False
	brdf = True
	
	if options.angFile: angfile = options.angFile
	if options.wbFile: wbfile = options.wbFile
	if options.root: root = options.root
	if options.spec: 
		spec = True
		spec_plot(spec,wbfile)
		
	if options.brdf:
		brdf = True
		brdf_plot(root,angfile,wbfile)

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-angles", dest="angFile", help="angles file", metavar="FILE")
	parser.add_argument("-wb", dest="wbFile", help="wb file", metavar="FILE")
	parser.add_argument("-root", dest="root", help="root", metavar="FILE")
	parser.add_argument("-brdf", action="store_true", help="do brdf plot")
	parser.add_argument("-spec", action="store_true", help="do spec plot")
	options = parser.parse_args()
	main()
