#!/usr/bin/python
# Author Dario Clavijo 2017
# GPLv3

import imghdr 
import sys
import zbar
import Image
import ImageFilter
import os
import threading
import time

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
		try:
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
			del image 
			del raw
		except:
			pass
	
		return ret

	ct = "[" + threading.currentThread().getName() + "]"

	r = from_pil(scanner,pil)
	if len(r) > 0:
		ret += r
		print ct,filename,"Found: Normal"

	sharpen = True
	if sharpen:
		pil2 = pil
		#for i in xrange(0,9):
		pil2 = pil2.filter(ImageFilter.SHARPEN)
		r = from_pil(scanner,pil2)
		if len(r) > 0:
			ret += r
			print ct,filename,"Found: sharpen!"
		del pil2

	rotate = True
	if rotate:
		i = 0
		for angle in xrange(1,181):
			pil3 = pil.rotate(angle, resample=Image.BICUBIC, expand=0)
			r = from_pil(scanner,pil3)
			if len(r) >0:
				ret += r
				print ct,filename,"Found: Rotated: %d" % angle
				i+=1
			if i > 9:
				break
		del pil3
	del scanner
	del pil	

	return ret

def is_image(filename):
	try:
		res = imghdr.what(filename)
	except:
		return False
	return (res is not None)


def loadfile(filename):
	data = []
	fp = open(filename,'rw+')
	for line in fp:
		data.append(line.rstrip())
	fp.close
	return fp,data

def savefile(data,filename):
	fp2 = open(filename,'w')
	for line in data:
		fp2.write(line+"\n")
	fp2.close()

threads = []

max_threads=20

def wait_for_child(max_t):
	while threading.activeCount() > max_t:
		time.sleep(5)

def new_thread(target,args):
    	at = threading.activeCount()
	def _new_thread(target,args):
		t = threading.Thread(target=target,args=(args,))
		threads.append(t)
		t.start()
    	if at <= max_threads:
		_new_thread(target,args)
    	else:
		wait_for_child(max_threads)
		_new_thread(target,args)

def walk(cachefile,datafile,fdir):

	fp_cache,cache = loadfile(cachefile)
	fp_data,data = loadfile(datafile)

	for root, d, files in os.walk(fdir):
        	#for items in fnmatch.filter(files, "*"):
		
		for fname in files:
			f = root + "/"  + fname
			if f not in cache:
				if os.path.isfile(f) == True and is_image(f):
					cache.append(f)
					def proc_file(f):
						#try:
						ret = scan_image(f)
						if ret is not None and len(ret) > 0:
							for i in ret:
								if i[1] not in data:
									
									print f,i
									data.append(i[1])
									fp_data.write(i[1].encode('hex')+"\n")
									fp_cache.write(f+"\n")
									fp_data.flush()
									fp_cache.flush()
						#except:
						#	print ""
						
					new_thread(proc_file,f)
					sys.stdout.flush()


	wait_for_child(1)
	fp_cache.close()
	fp_data.close()	

def main():
	walk('.hash_cache',sys.argv[1],sys.argv[2])


if __name__ == "__main__":
    main()


