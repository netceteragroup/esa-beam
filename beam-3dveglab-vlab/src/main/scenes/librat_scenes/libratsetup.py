import numpy as np
import sys

class geom:
	"""
	geometry class
	"""
	def __init__(self,zen,az):
		self.zen = zen
		self.az = az


class cam:
	"""camera definition: librat camera defintion class, including methods to initialise camera name, result_image, result_integral_mode, result_integral, geom_azimuth, geom_zenith, geom_twist, geom_lookfrom (x, y, z), geom_lookat (x, y, z), geom_idealArea (x, y), geom_boomlength, samplingCharacteristics_nPixels, samplingCharacteristics_rpp, samplingPattern
	"""

	def __init__(self,**kwargs):
	
		# defaults
		self.camera = 'simple camera'
		self.perspective = False
		self.result_image = 'result.hips'
		self.result_integral_mode = 'scattering order'
		self.result_integral = 'result'
		self.vz = 0.
		self.va = 0.
		self.twist = 0.
		self.look = 0., 0., 0.
		self.location = 0., 0., 1.
		self.ideal = False
		self.location = False
		self.fov = False
		self.boom = 1000.
		self.samplingCharacteristics_nPixels = 100000
		self.samplingCharacteristics_rpp = 1
		
		if 'vz' in kwargs: self.vz = kwargs['vz']
		if 'va' in kwargs: self.va = kwargs['va']
		self.g = geom(self.vz,self.va)
		
		if 'camera' in kwargs: self.camera = kwargs['camera']
		if 'image' in kwargs: self.result_image = kwargs['image']
		if 'integral_mode' in kwargs: self.result_integral_mode = kwargs['integral_mode']
		if 'integral' in kwargs: self.result_integral = kwargs['integral']
		if 'nPixels' in kwargs: self.samplingCharacteristics_nPixels = kwargs['nPixels']
		if 'rpp' in kwargs: self.samplingCharacteristics_rpp = kwargs['rpp']
		if 'boom' in kwargs: self.boom = kwargs['boom']
		if 'look' in kwargs:
			self.look = kwargs['look']
			if np.size(self.look) != 3:
				sys.stderr.write("camera class: look has %i values - should be 3\n"%(np.size(self.look)))
				sys.exit([True])
		if 'location' in kwargs:
			self.location = kwargs['location']
			#if np.size(self.location) != 2:
			#	sys.stderr.write("camera class: location has %i values - should be 3\n"%(np.size(self.location)))
			#	sys.exit([True])
		else:
			self.location = False
					
		if 'ideal' in kwargs: 
			self.ideal = kwargs['ideal']
			if np.size(self.ideal) != 2:
				self.ideal = False
		else:
			self.ideal = False
			
		if 'twist' in kwargs: self.twist = kwargs['twist']				
		if 'lidar' in kwargs:
			self.lidar = True
			if np.size(np.array(kwargs['lidar'])) != 3:
				sys.stderr.write("camera class: lidar has %i values - should be 3\n"%(np.size(np.array(kwargs['lidar']))))
				sys.exit([True])
			else:
				self.binStart = np.array(kwargs['lidar'])[0]
				self.binStep = np.array(kwargs['lidar'])[1]
				self.nBins = np.array(kwargs['lidar'])[2]
		else:
			self.lidar = False
			
		if 'fov' in kwargs:
			self.fov = kwargs['fov']
		else:
			self.fov = False
		
		
		# check if fov and ideal set
		if self.fov == True  and self.ideal[0] == True:
			sys.stderr.write("camera class: both ideal area and fov set\n")
			sys.exit([True])
		
		if 'fov' not in kwargs and 'ideal' not in kwargs:
			sys.stderr.write("camera class: neither ideal area or fov set: setting ideal = (100, 100)\n")
			self.ideal = (100, 100)
		
		if 'samplingPattern' in kwargs:
			self.samplingPattern = kwargs['samplingPattern']
		else:
			self.samplingPattern = False

	def printer(self, **kwargs):
		
		msg = ' camera { \n' \
	    	+ ' camera.name = "{0:}";\n'.format(self.camera) \
			+ ' geometry.zenith = {0:};\n'.format(self.vz) \
			+ ' geometry.azimuth = {0:};\n'.format(self.va) \
			+ ' result.integral.mode = "{0:}";\n'.format(self.result_integral_mode) \
			+ ' result.integral = "{0:}";\n'.format(self.result_integral) \
			+ ' samplingCharacteristics.nPixels = {0:};\n'.format(self.samplingCharacteristics_nPixels) \
			+ ' samplingCharacteristics.rpp = {0:};\n'.format(self.samplingCharacteristics_rpp) \
			+ ' geometry.lookat = {0:}, {1:}, {2:};\n'.format(self.look[0], self.look[1], self.look[2]) \
			+ ' geometry.boomlength = {0:};\n'.format(self.boom)
		
		if np.size(self.ideal) == 2: msg += ' geometry.idealArea = {0:}, {1:};\n'.format(self.ideal[0], self.ideal[1])
		if np.size(self.location) == 3: msg += ' geometry.location = {0:}, {1:}, {2:};\n'.format(self.location[0], self.location[1], self.location[2])
		if self.perspective: msg += ' geometry.perspective 0:};\n'.format(self.perspective)
		if self.result_image: msg += ' result.image = "{0:}";\n'.format(self.result_image)
		if self.twist: msg += ' geometry.twist = {0:};\n'.format(self.twist)  
		if self.fov: msg += ' geometry.fieldOfView = {0:};\n'.format(self.fov)
		if self.samplingPattern: msg += ' samplingPattern.form = "{0:}";\n'.format(self.samplingPattern)
		if self.lidar:
			msg += ' lidar.binStep = {0:};\n'.format(self.binStep)
			msg += ' lidar.binStart = {0:};\n'.format(self.binStart)
			msg += ' lidar.nBins = {0:};\n'.format(self.nBins)
			
		msg += '}'
		
		
		if 'file' in kwargs:
			opfile = open(kwargs['file'],'w')
			opfile.write(msg)
			opfile.close()
		else:
			print msg


class light:
	"""light definition: librat light defintion class, including methods to initialise light file name, geom_azimuth, geom_zenith, geom_twist, geom_lookat (x, y, z), geom_idealArea (x, y), geom_boomlength
	"""

	def __init__(self,**kwargs):
	
		# defaults
		self.camera = 'simple illumination'
		self.sz = 0.
		self.sa = 0.
		self.twist = 0.
		
		if 'sz' in kwargs: self.sz = kwargs['sz']
		if 'sa' in kwargs: self.sa = kwargs['sa']
		self.g = geom(self.sz,self.sa)
		if 'camera' in kwargs: self.camera = kwargs['camera']
		if 'twist' in kwargs: self.twist = kwargs['twist']
			
		if 'boom' in kwargs:
			self.boom = kwargs['boom']
		else:
			self.boom = False
			
		if 'look' in kwargs:
			self.look = kwargs['look']
			if np.size(self.look) != 3:
				sys.stderr.write("camera class: look has %i values - should be 3\n"%(np.size(self.look)))
				sys.exit([True])
		else:
			self.look = False
			
		if 'ideal' in kwargs: 
			self.ideal = kwargs['ideal']
			if np.size(self.ideal) != 2:
				sys.stderr.write("camera class: ideal has %i values - should be 2\n"%(np.size(self.ideal)))
				sys.exit([True])
		else:
			self.ideal = False

		if 'fov' in kwargs:
			self.fov = kwargs['fov']
		else:
			self.fov = False
			
			
		if 'perspective' in kwargs:
			self.perspective = kwargs['perspective']
		else:
			self.perspective = False
						

	def printer(self, **kwargs):
	
		msg = ' camera { \n' \
	    	+ ' camera.name = "{0:}";\n'.format(self.camera) \
			+ ' geometry.zenith = {0:};\n'.format(self.sz) \
			+ ' geometry.azimuth = {0:};\n'.format(self.sa) \
			+ ' geometry.twist = {0:};\n'.format(self.twist)
		
		if self.ideal: msg += ' geometry.ideal = {0:};\n'.format(self.ideal[0], self.ideal[1])
		if self.look: msg += ' geometry.lookAt = {0:}, {1:}, {2:};\n'.format(self.look[0], self.look[1], self.look[2])
		if self.boom: msg += ' geometry.boom = {0:};\n'.format(self.boom)
		if self.perspective: msg += ' geometry.perspective 0:};\n'.format(self.perspective)
		if self.fov: msg += ' geometry.fov = {0:};\n'.format(self.fov)
			
		msg += '}'
		
		
		if 'file' in kwargs:
			opfile = open(kwargs['file'],'w')
			opfile.write(msg)
			opfile.close()
		else:
			print msg
