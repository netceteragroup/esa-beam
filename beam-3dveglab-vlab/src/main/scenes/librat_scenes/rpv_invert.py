#!/usr/bin/env python

import sys, os, argparse, glob
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize
from math import sqrt

debug = True


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

#-----------------------------------------------------------------------

class VLAB:

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
  
#-----------------------------------------------------------------------
# Use a class to keep the data tidy and conveniently accessible...

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
  
#--------------------------------------------------------------------
  
def test_fun_1(x):
  """
  Test objective function 1.

  x is expected to be a list of ccordinates.
  Returns a single float value.
  """
  n = len(x)
  sum = 0.0
  for i in range(n):
    sum += (x[i] - 1.0) * (x[i] - 1.0)
  return sum
  
def test_fun_2(x):
  """
  Test objective function 2.
  
  Example 3.3 from Olsson and Nelson.
  """
  x1, x2 = x   # rename to match the paper
  if (x1 * x1 + x2 * x2) > 1.0:
    return 1.0e38
  else:
    yp = 53.69 + 7.26 * x1 - 10.33 * x2 + 7.22 * x1 * x1 \
       + 6.43 * x2 * x2 + 11.36 * x1 * x2
    ys = 82.17 - 1.01 * x1 - 8.61 * x2 + 1.40 * x1 * x1 \
       - 8.76 * x2 * x2 - 7.20 * x1 * x2
    return -yp + abs(ys - 87.8)
  
def test_fun_3(z):
  """
  Test objective function 3.

  Example 3.5 from Olsson and Nelson; least-squares.
  """
  from math import exp
  x = [0.25, 0.50, 1.00, 1.70, 2.00, 4.00]
  y = [0.25, 0.40, 0.60, 0.58, 0.54, 0.27]
  a1, a2, alpha1, alpha2 = z
  sum_residuals = 0.0
  for i in range(len(x)):
    t = x[i]
    eta = a1 * exp(alpha1 * t) + a2 * exp(alpha2 * t)
    r = y[i] - eta
    sum_residuals += r * r
  return sum_residuals
  
def nelmintests():
  print "Begin nelmin self-test..."

  print "---------------------------------------------------"
  print "test 1: simple quadratic with zero at (1,1,...)"
  x, fx, conv_flag, nfe, nres = VLAB.Minimize_minimize(test_fun_1, [0.0, 0.0, 0.0])
  print "x=", x
  print "fx=", fx
  print "convergence-flag=", conv_flag
  print "number-of-fn-evaluations=", nfe
  print "number-of-restarts=", nres

  print "---------------------------------------------------"
  print "test 2: Example 3.3 in Olsson and Nelson f(0.811,-0.585)=-67.1"
  x, fx, conv_flag, nfe, nres = VLAB.Minimize_minimize(test_fun_2,
                       [0.0, 0.0], [0.5, 0.5],
                       1.0e-4)
  print "x=", x
  print "fx=", fx
  print "convergence-flag=", conv_flag
  print "number-of-fn-evaluations=", nfe
  print "number-of-restarts=", nres

  print "---------------------------------------------------"
  print "test 3: Example 3.5 in Olsson and Nelson, nonlinear least-squares"
  print "f(1.801, -1.842, -0.463, -1.205)=0.0009"
  x, fx, conv_flag, nfe, nres = VLAB.Minimize_minimize(test_fun_3,
                       [1.0, 1.0, -0.5, -2.5],
                       [0.1, 0.1, 0.1, 0.1],
                       1.0e-9, 800)
  print "x=", x
  print "fx=", fx
  print "convergence-flag=", conv_flag
  print "number-of-fn-evaluations=", nfe
  print "number-of-restarts=", nres

  print "---------------------------------------------------"
  print "Done."


#--------------------------------------------------------------------


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

                nm = None
                if debug:
                        nm = VLAB.Minimize_minimize(obj, params, args=(invdata,))[0]
		p_est = scipy.optimize.fmin(obj,params,args=(invdata,))
                if debug:
                        print " scipy.optimize.fmin (old) | nelmin.minimize (new)"
                        print "-------------------------------------------------------"
                        for values in zip(p_est, nm):
                                print "% 0.23f | % 0.23f" % values
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
	nelmintests()
	main()
