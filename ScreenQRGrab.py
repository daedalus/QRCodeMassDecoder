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

	ret = [(symbol.type, symbol.data) for symbol in image]
	# clean up
	del(image)
	return ret




def loadfile(filename):
	with open(filename,'r') as fp:
		data = [base64.urlsafe_b64decode(line.rstrip()) for line in fp]
	return data

def screen_grab(col,filename):
	with open(filename,'a+') as fp:
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


filename = sys.argv[1]
data = loadfile(filename)
screen_grab(data,filename)
