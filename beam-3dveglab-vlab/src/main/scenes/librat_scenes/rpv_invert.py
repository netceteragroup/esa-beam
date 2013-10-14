#!/usr/bin/env python

import sys, os, argparse, glob
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize


# objective function - requires params, x (array of angles) and y (array of obs)
def obj(p,x):
	#return((((rpv(p,x)-y)**2).sum()))
	fwd = rpv(p, x)
	obs = x[4,:]
	sse = ( (obs-fwd )**2).sum()
	#plt.plot ( x[0,:],fwd, '-ko', lw=0.2)
	return sse

def rpv(params,data):

	# assumes data format is:
	# vz va sa sa and ignores rest

	if np.shape(params)[0] == 4:
		rho0, k, bigtet, rhoc = params
	else:
		rhoc = 1.
		rho0, k, bigtet = params
	cosv = np.cos(np.deg2rad(data[0]))
	coss = np.fabs(np.cos(np.deg2rad(data[2])))
	cosv[np.where(cosv == np.float(0))] = 1e-20
	coss[np.where(coss == np.float(0))] = 1e-20
	sins = np.sqrt(1. - coss*coss)
	sinv = np.sqrt(1. - cosv*cosv)
	relphi = np.deg2rad(data[1]) - np.deg2rad(data[3])
	relphi[np.where(relphi > np.pi)] = 2*np.pi - relphi[np.where(relphi > np.pi)]
	cosp = -1.*np.cos(relphi)
	tans = sins/coss
	tanv = sinv/cosv
	csmllg = coss * cosv + sins * sinv * cosp
	bigg = np.sqrt(tans * tans + tanv * tanv -  2.0 * tans * tanv * cosp)
	bgthsq = bigtet * bigtet
	expon = k - 1.0
	if expon != 0.0:
		f1 = pow(coss * cosv,expon) * pow(coss + cosv,expon)
	else:
		f1 = 0.*(coss) + 1.0
	
	denom = pow(1.0 + bgthsq + 2.0 * bigtet * csmllg,1.5)
	f2 = np.copy(denom)
	f2[np.where(denom != 0.)] = (1.0 - bgthsq) / denom[np.where(denom != 0.)]
	f2[np.where(denom == 0.)] = (1.0 - bgthsq)*1e20
	f3 = (1.0 + ((1 - rhoc) / (1.0 + bigg)))
	return(rho0 * f1 * f2 * f3)


def main():

	dataf = 'rpv.rami.2/result.HET01_DIS_UNI_NIR_20.obj.brdf.dat'


	wbfile = 'wb.MSI.dat'
	wbNum = 3 # 665 nm in this case

	verbose = 1
	plot = 1
	show = 0
	
	if options.dataf: dataf = options.dataf
	if options.wbfile: wbfile = options.wbfile
	if options.wb: wbNum = options.wb
	if options.v: verbose = 1

	wb = np.genfromtxt(wbfile,comments='#',unpack=True)[1]	
	data = np.genfromtxt(dataf,comments='#',unpack=True)

	# check shape of 2 data files i.e. that there are same no. of wbs on each line of datafile ( + 4 angles)
	if wb.shape[0] != data.shape[0]-4:
		sys.stderr.write('%s: no of wavebands different in brdf file %s and wb file %s\n'%(sys.argv[0],dataf,wbfile))
		sys.exit(1)
	
	# rpv params
	rho0, k, bigtet, rhoc = 0.03, 1.2, 0.1, 0.2
	
	if options.three:
		params = [rho0, k, bigtet]
	else:
		params = [rho0, k, bigtet, rhoc]
	
	# test
	#r = rpv(params,data)
	#plt.plot(data[0,:15],data[5,:15],'ko')
	#plt.plot(data[0,:15],r[0:15],'r-')
	#plt.show()
	#plt.close()
	
	# RAMI test: see http://rami-benchmark.jrc.ec.europa.eu/HTML/DEFINITIONS/DEFINITIONS.php#RPV
	#rho0, k, bigtet, rhoc = 0.075, 0.55, -0.25, 0.075
	#params = [0.075, 0.55, -0.25, 0.075]
	#angles = np.array([np.arange(-80,80,2), np.zeros((80,)), np.ones((80,))*20.,np.ones((80,))*180.])
	#angles = np.array([np.arange(-80,80,2), np.zeros((80,)), np.ones((80,))*50.,np.ones((80,))*180.])
	#angles[3,np.where(angles[0]>0)] = 0.
	#res = rpv(params,angles)
	#plt.plot(angles[0], res)
	#plt.show()
	#plt.close()
	
	
	if options.paramfile:
		opdat = options.paramfile
	else:
		opdat = dataf + '.params.dat'
	
	if verbose: sys.stderr.write('%s: saving params to %s\n'%(sys.argv[0], opdat))

	fd = os.open(opdat, os.O_CREAT | os.O_WRONLY | os.O_TRUNC)
	opfp = os.fdopen(fd,'w')
	if options.three:
		#opfp.write('# wb RMSE rho0 k bigtet\n')
                opfp.write('# wb rho0 k bigtet\n')
	else:
		#opfp.write('# wb RMSE rho0 k bigtet rhoc\n')
                opfp.write('# wb rho0 k bigtet rhoc\n')

	ymin, ymax = (0, 0.25)
	xmin, xmax = (-75., 75)
	
	#invert test
	#which wband?
	# do per band

	# test
	#np.savetxt('xxxtest.in.dat',data.T)
	
	for wbNum, band in enumerate(wb):
		if verbose: sys.stderr.write('%s: doing band %i (%f)\n'%(sys.argv[0], wbNum, band))
	
		invdata = np.zeros((5,data.shape[1]))
		invdata[0:4] = np.copy(data[0:4])
		invdata[4] = np.copy(data[4 + wbNum])
	
		#invdata = np.zeros((5,15))
		#invdata[0:4] = np.copy(data[0:4,0:15])
		#invdata[4] = np.copy(data[4 + wbNum,0:15])
		
		# now do inversion
		porig = params
		p_est = params
		p_est = scipy.optimize.fmin(obj,params,args=(invdata,))
		#p_est = scipy.optimize.fmin_l_bfgs_b(obj,params,args=(invdata,),approx_grad=1, disp=1)
		#p_est = scipy.optimize.fmin_l_bfgs_b(obj,p_est,args=(invdata,),approx_grad=1)
		if options.three:
			p_est = scipy.optimize.fmin_l_bfgs_b(obj,p_est,args=(invdata,),approx_grad=1, bounds=((0., None), (0., None),(None, None)))
		else:
			# set param ranges for rho0, k, bigtet, rhoc
			#p_est = scipy.optimize.fmin_l_bfgs_b(obj,p_est,args=(invdata,),approx_grad=1, bounds=((0., None), (0., None),(None, None),(0., 20.)))
			p_est = scipy.optimize.fmin_l_bfgs_b(obj,p_est,args=(invdata,),approx_grad=1, bounds=((0., None), (0., None),(None, None),(None, None)))

		# r is fwd-modelled refl based on rpv params
		r = rpv(p_est[0],invdata)
		rmse = np.sqrt(((r - invdata[4])**2).sum())

		# test o/p
		#np.savetxt('xxxtest.orig.dat',invdata.T)
		#np.savetxt('xxxtest.fwd.dat',r.T)
		#sys.exit(1)

		if options.three:
			#opfp.write('%.1f %.8f %.8f %.8f %.8f\n'%(band, rmse, p_est[0][0],p_est[0][1],p_est[0][2]))
                        opfp.write('%.1f %.8f %.8f %.8f\n'%(band, p_est[0][0],p_est[0][1],p_est[0][2]))
		else:
			#opfp.write('%.1f %.8f %.8f %.8f %.8f %.8f\n'%(band, rmse, p_est[0][0],p_est[0][1],p_est[0][2],p_est[0][3]))
                        opfp.write('%.1f %.8f %.8f %.8f %.8f\n'%(band, p_est[0][0],p_est[0][1],p_est[0][2],p_est[0][3]))

	
		#plt.plot(data[0,:15],data[5,:15],'ko')
		#plt.plot(data[0,:15],r[0:15],'r-')

		if options.plot:
			if options.plotfile:
				opplot = options.plotfile + '.inv.wb.' + str(wbNum) + '.png'
			else:
				opplot = dataf + '.inv.wb.' + str(wbNum) + '.png'
			
			if verbose: sys.stderr.write('%s: plotting to %s\n'%(sys.argv[0], opplot))

			fig = plt.figure()
			ax = fig.add_subplot(111)
			ax.set_xlabel('vza (deg)',fontsize=14)
			ax.set_ylabel(r'$\rho$',fontsize=20)
			ax.set_ylim((ymin, ymax))
			ax.set_xlim((xmin, xmax))
			ax.text(0.05,0.85,'rmse  = %.6f'%(rmse), transform = ax.transAxes)
			ax.text(0.05,0.8,'rho0   = %.4f'%(p_est[0][0]),transform = ax.transAxes)
			ax.text(0.05,0.75,'k      = %.4f'%(p_est[0][1]),transform = ax.transAxes)
			ax.text(0.05,0.7,'bigtet = %.4f'%(p_est[0][2]),transform = ax.transAxes)
			if not options.three:
				ax.text(0.05,0.65,'rhoc   = %.4f'%(p_est[0][3]),transform = ax.transAxes)
			ax.plot(invdata[0],invdata[4],'ko',label='original')
			ax.plot(invdata[0],r,'rx',label='inverted')
			ax.legend(loc=1)
			if show:
				plt.show()
			plt.savefig(opplot)
			#plt.close()	
	

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-data", dest="dataf", help="data file", metavar="FILE")
	parser.add_argument("-wbfile", dest="wbfile", help="data file", metavar="FILE")
	parser.add_argument("-plotfile", dest="plotfile", help="plot file", metavar="FILE")
	parser.add_argument("-paramfile", dest="paramfile", help="param file", metavar="FILE")
	parser.add_argument("-wb", dest="wb", help="wb no.")
	parser.add_argument("-plot", action="store_true", help="plot on")
	parser.add_argument("-v", action="store_true", help="verbose on")
	parser.add_argument("-three", action="store_true", help="3 params only")
	options = parser.parse_args()
	main()
