#!/usr/bin/python
# Author Dario Clavijo 2017
# GPLv3

import imghdr 
import sys
import zbar
import Image

import os
import fnmatch

def scan_image(filename):
	ret = []
	# create a reader
	scanner = zbar.ImageScanner()

	# configure the reader
	scanner.parse_config('enable')

	# obtain image data
	pil = Image.open(filename).convert('L')
	width, height = pil.size
	raw = pil.tobytes()

	# wrap image data
	image = zbar.Image(width, height, 'Y800', raw)

	# scan the image for barcodes
	scanner.scan(image)

	# extract results
	for symbol in image:
	    # do something useful with results
	    ret.append((symbol.type, symbol.data))

	# clean up
	del(image)
	return ret

def is_image(filename):
	try:
		res = imghdr.what(filename)
	except:
		return False
	return (res is not None)

def walk(fdir)
	for root, d, files in os.walk(fdir):
        	#for items in fnmatch.filter(files, "*"):
		for fname in files:
			f = root + "/"  + fname
			if os.path.isfile(f) == True and is_image(f):
				ret = scan_image(f)
				if ret is not None and len(ret) > 0:
					print f,ret

walk(sys.argv[1])
