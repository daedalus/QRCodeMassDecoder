#!/usr/bin/python
# Author Dario Clavijo 2017
# GPLv3

import imghdr 
import sys
import zbar
import Image
import ImageFilter
import os
#import fnmatch
import threading

hex_fp = open(sys.argv[1],'rw+')

def scan_image(filename):
	ret = []

	#print filename

	# create a reader
	# configure the reader
	scanner = zbar.ImageScanner()
	scanner.parse_config('enable')

	# obtain image data
	pil = Image.open(filename).convert('L')

	def from_pil(scanner,pil):
		ret = []
		#pil = pil.convert('L')
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
		#del(image)
		return ret

	r = from_pil(scanner,pil)
	if len(r) > 0:
		ret += r
		print filename,"Found: Normal"

	sharpen = True
	if sharpen:
		pil2 = pil
		#for i in xrange(0,9):
		pil2 = pil2.filter(ImageFilter.SHARPEN)
		r = from_pil(scanner,pil2)
		if len(r) > 0:
			ret += r
			print filename,"Found: sharpen!"

	rotate = True
	if rotate:
		i = 0
		for angle in xrange(1,181):
			pil3 = pil.rotate(angle, resample=Image.BICUBIC, expand=0)
			r = from_pil(scanner,pil3)
			if len(r) >0:
				ret += r
				print filename,"Found: Rotated: %d" % angle
				i+=1
			if i > 9:
				break
	return ret

def is_image(filename):
	try:
		res = imghdr.what(filename)
	except:
		return False
	return (res is not None)


def loadfile2(filename):
	data = []
	fp2 = open(filename,'r')
	for line in fp2:
		data.append(line.rstrip())
	fp2.close
	return data

def savefile(data,filename):
	fp2 = open(filename,'w')
	for line in data:
		fp2.write(line+"\n")
	fp2.close()

def loadfile(fp):
        data = []
        for line in fp:
                data.append(line.rstrip().decode('hex'))
        return data

threads = []
consumed_by_threads = 0
consumed_by_main = 0

def new_thread(target,args):
	global consumed_by_threads
	global consumed_by_main
    	at = threading.activeCount()
    	if at <= 30:
        	t = threading.Thread(target=target,args=(args,))
        	threads.append(t)
        	consumed_by_threads += 1
        	t.start()
    	else:
        	print "active threads:", at
        	consumed_by_main += 1
		target(args)

def walk(cache,data,fp,fdir):
	for root, d, files in os.walk(fdir):
        	#for items in fnmatch.filter(files, "*"):
		for fname in files:
			f = root + "/"  + fname
			if f not in cache:
				if os.path.isfile(f) == True and is_image(f):
					#try:
					def proc_file(f):
						ret = scan_image(f)
						if ret is not None and len(ret) > 0:
							for i in ret:
								if i[1] not in data:
									print f,i
									data.append(i[1])
									fp.write(i[1].encode('hex')+"\n")
									fp.flush()
					#proc_file(f)
					new_thread(proc_file,f)
					#os.flush()
					sys.stdout.flush()
					#except:
					#	print "error"
				cache.append(f)




        		#target(args)

cache = loadfile2('.hash_cache')
data = loadfile(hex_fp)
walk(cache,data,hex_fp,sys.argv[2])
fp.close()
savefile(cache,'.hash_cache')
