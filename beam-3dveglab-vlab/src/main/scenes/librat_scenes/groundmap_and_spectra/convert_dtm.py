#!/usr/bin/env python

import numpy as np
import sys
from gdalconst import *
import struct
import datetime, argparse


def read_pbm(fname):
    with open(fname) as f:
        data = [x for x in f if not x.startswith('#')] #remove comments
    p_whatever = data.pop(0)  #P4 ... don't know if that's important...
    dimensions = map(int,data.pop(0).split())
    arr = []
    col_number = 0
    for c in data.pop(0):
        integer = struct.unpack('B',c)[0]
        col_number += 8
        bits = map(int,bin(integer)[2:])
        arr.extend(bits[:min(8,dimensions[0]-col_number)])
        if(col_number > dimensions[0]):
            col_number = 0 

    return (dimensions, arr)

def read_txt(fname):
	with open(fname,'r') as f:
		for line in f:
			if line.startswith('#'):
				r = np.int(line.split()[-1].split(',')[0])
				c = np.int(line.split()[-1].split(',')[0])
				data = np.zeros((r,c),dtype='int')
			else:
				rr = np.int(line.split()[0].split(',')[1].split(':')[0])
				cc = np.int(line.split()[0].split(',')[0])
				data[rr,cc] = np.int(line.split()[3].split(',')[0])
	return (r,c,data)



class hips_header:
	"""
	HIPS image header: looks like
	"""
	def __init__(self,**kwargs):
		
		codes = {'PFBYTE':0, 'PFSHORT':1, 'PFINT':2, 'PFFLOAT':3, 'PFCOMPLEX':4, 'PFASCII':5, 'PFUSHORT':6}

		# defaults
		self.name = 'HIPS \n'
		self.frames = 1
		self.rows = 512
		self.cols = 512
 		self.bpp = 0
		self.format = codes['PFBYTE']
		
		if 'frames' in kwargs: self.frames = kwargs['frames']
		if 'rows' in kwargs: self.rows = kwargs['rows']
		if 'cols' in kwargs: self.cols = kwargs['cols']
		if 'bpp' in kwargs: self.bpp = kwargs['bpp']
		if 'format' in kwargs: self.format = codes[kwargs['format']]
		
		self.history = '%s "%s" \n'%(sys.argv,datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
		#self.history = 'genheader -t 5 1 150 150 "-D Tue Feb 26 14:54:51 2013" '
		
		self.header = self.name + '\n' + '%i\n'%self.frames + '\n' + \
		'%i\n'%self.rows + '%i\n'%self.cols + '%i\n'%self.bpp + '0\n' + '%i\n'%self.format + '%s'%self.history + '\x00' + '\n.\n'
		
		#def write_head(self,**kwargs):
		#	msg = self.name + '\n' + self.frames
	



def main():
	#ip = 'ground_map.pbm'
	#dim, arr = read_pbm(ip)
	#ip2 = ip.split('.')[0] + '.txt'
	#dat = []
	ip = 'ground_map.txt'
	op = ip.split('.')[0] + '.hips'
	
	
	if options.ip: ip = options.ip
	if options.op: op = options.op
	
	c, r, dat = read_txt(ip)
	h = hips_header(format='PFASCII',rows=r, cols=c)
	ofile = open(op,'w+')
	ofile.write(h.header)
	np.savetxt(ofile,dat,fmt='%i')
	ofile.close()


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-i", dest="ip", help="ip file")
	parser.add_argument("-o", dest="op", help="op file")
	options = parser.parse_args()
	main()


