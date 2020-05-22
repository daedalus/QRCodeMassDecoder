#!/usr/bin/python
# Author Dario Clavijo 2017
# GPLv3

import sys
import zbar
#import Image
from PIL import Image
import time
import pyscreenshot as ImageGrab
import base64

#fp = open(sys.argv[1],'rw+')


def scan_file(filename):
	pil = Image.open(filename).convert('L')
	return scan_image(pil)

def scan_image(pil):
	ret = []
	# create a reader
	scanner = zbar.ImageScanner()

	# configure the reader
	scanner.parse_config('enable')

	width, height = pil.size

	#print width,height

	raw = pil.tobytes()

	#fp = open('/home/dclavijo/raw','w+')
	#fp.write(raw)
	#fp.close

        # wrap image data
	image = zbar.Image(width, height, 'Y800', raw)

	#print image

	# scan the image for barcodes
	scanner.scan(image)

	# extract results
	for symbol in image:
	    # do something useful with results
		ret.append((symbol.type, symbol.data))
	    #print symbol

	# clean up
	del(image)
	return ret




def loadfile(filename):
	fp = open(filename,'r')
	data = []
	for line in fp:
		#data.append(line.rstrip().decode('hex'))
		data.append(base64.urlsafe_b64decode(line.rstrip()))

	fp.close()
	return data

def screen_grab(col,filename):
	fp = open(filename,'a+')
	while True:
		time.sleep(0.5)
		img=ImageGrab.grab().convert('L')
		ret = scan_image(img)
		if ret is not None and len(ret) > 0:
			for i in ret:
				if len(i) >1 and  i[1] not in col:
					print (i[0],i[1])
					col.append(i[1])
					b64 = base64.urlsafe_b64encode(i[1].encode("utf-8")).decode('utf-8')
					fp.write(b64+"\n")
					sys.stderr.write(i[1]+"\n")
					#sys.stdout.write(base64.urlsafe_b64encode(i[1])+"\n")
		sys.stderr.flush()
		#sys.stdout.flush()                        
		fp.flush()
	fp.close()


filename = sys.argv[1]
data = loadfile(filename)
screen_grab(data,filename)
