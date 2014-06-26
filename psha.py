#!/usr/bin/env python2

"""Finds duplicate files using sha1 and writes them to 'clashes' file in 'digest:file1,file2...' format"""

import hashlib
import os

DEBUG = 0

def shadircontents(filetypes=None, directory = '.'):
	"""Walk through a directory creating sha1 sums of the contents of all the files that match the provided list of filetypes"""
	filehashes = {}
	clashes = {}
	if DEBUG:
		print "starting the loop"
	for root, dirs, files in os.walk(str(directory)):
		for name in files:
			filepath = os.path.join(root, name)
			filetype = name[name.find('.'):]
			if filetypes == None or filetype.lower() in filetypes:
				file = open(filepath, 'rb').read()
				hash = hashlib.sha1(file).hexdigest()
				if hash in filehashes:
					if hash not in clashes:
						clashes[hash] = [filehashes[hash][0]]
					clashes[hash].append(filepath)
					#clashes.append(','.join((hash, filehashes[hash], filepath + '\n')))
					#clashes.append((filehashes[hash],',',hash,'\n'))
					if DEBUG:
						print "filepath:", filepath, hash
						print "filehash:", filehashes[hash], hash
						print
				else:
					filehashes[hash] = [filepath,]
	if DEBUG:
		print "filehashes:", filehashes
		print
		print "clashes:", clashes
	return (filehashes, clashes)

def shaimages(directory = '.', imagetypes = ('.jpeg','.jpg', '.png', '.gif','.bmp')):
	"""Creates a sha1 sum of images"""
	pass

if __name__ == "__main__":
	import time
	import os
	if DEBUG:
		print "going into the function"
	#filehashes, clashes = shadircontents('.jpg')
	#file = open(os.environ.get('HOME')+"/Desktop/clashes"+str(int(time.time())), 'w')
	filehashes, clashes = shadircontents()
	output=map(':'.join, map(lambda kv: (kv[0], ','.join(kv[1]) + '\n'), clashes.items()))
	with open("clashes-py", "w") as f:
		map(f.writelines, output)
