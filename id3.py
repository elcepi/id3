#!/usr/bin/python3

import eyed3
import eyed3.id3
import os
import re
import argparse

eyed3.log.setLevel("ERROR")

P1 = re.compile("^(.*) +- +(.*)$")
P2 = re.compile("^(.*): +[‘'\"”](.*)[’'\"”]$")
P3 = re.compile("^(.*): +[‘'\"”](.*)[’'\"”“] (.*)$")

G_NONE    = eyed3.id3.Genre()

def save(self, filename=None, version=None, encoding=None, backup=False, preserve_file_time=False, max_padding=None):
	if (self.artist and self.title and hasattr(self, 'dirty')):
		self.artist = self.artist.replace("\\", "")
		self.title = self.title.replace("\\", "")
		if(version==eyed3.id3.ID3_V2_2 or version==None):
			version = eyed3.id3.ID3_V2_3
		self.oldsave(filename, version, encoding,backup, preserve_file_time, max_padding)
#		delattr(self, 'dirty')

eyed3.id3.tag.Tag.oldsave = eyed3.id3.tag.Tag.save
eyed3.id3.tag.Tag.save = save
def process_song(fname):
	# print(fname)
	name = os.path.basename(fname)
	a = eyed3.load(fname)

	if(not a or not a.tag):
		print("No ID3 info found", fname)
		return

	if(a.tag.artist == "KEXP" or a.tag.artist == "KCRW" or a.tag.artist == "MPR" or a.tag.artist == "Minnesota Public Radio"):
		if(P1.match(a.tag.title)):
			m = P1.match(a.tag.title)
			a.tag.artist = m.group(1)
			a.tag.title  = m.group(2)
			a.tag.dirty = True
		elif(P2.match(a.tag.title)):
			m = P2.match(a.tag.title)
			a.tag.artist = m.group(1)
			a.tag.title  = m.group(2)
			a.tag.dirty = True
		elif(P3.match(a.tag.title)):
			m = P3.match(a.tag.title)
			a.tag.artist = m.group(1) + " " + m.group(3)
			a.tag.title  = m.group(2)
			a.tag.dirty = True
		else:
			print("No parsed", a.tag.title)
	elif(a.tag.artist and a.tag.title and a.tag.title.startswith(a.tag.artist)):
		a.tag.title = a.tag.title.replace(a.tag.artist + " - " , "")
		a.tag.dirty = True
	elif(a.tag.title and P1.match(a.tag.title)):
		m = P1.match(a.tag.title)
		a.tag.artist = m.group(1)
		a.tag.title = m.group(2)
		a.tag.dirty = True
	elif(P3.match(name)):
		m = P3.match(name)
		a.tag.artist = m.group(1)
		a.tag.title = m.group(2)
		a.tag.dirty = True
	elif(a.tag.genre == "KUTX Song of the Day" or (a.tag.artist and a.tag.title)):
		pass
	else:
		print("NO PARSED", fname)

	a.tag.images.remove('')
	a.tag.genre  = G_NONE

	a.tag.save(version=(2,3,0))
	a.tag.save(version=(2,4,0))
	a.tag.save()

def dir_path(string):
	if os.path.isdir(string):
		return string
	else:
		raise NotADirectoryError(string)

def setup_args():
	parser = argparse.ArgumentParser(description='Id3 tags seter')
	parser.add_argument("directory", nargs=1, type=dir_path, help='Directory where files are')
	args = parser.parse_args()
	return args

def traverse(path):
	for myfile in os.scandir(path):
		if myfile.is_file():
#			print(myfile.path)
			process_song(myfile.path)

if __name__ == "__main__":
	args = setup_args()
	traverse(args.directory[0])

