#!/usr/bin/python3

import eyed3
import eyed3.id3
import os
import re
import argparse

eyed3.log.setLevel("ERROR")

P1 = re.compile("^(.*) +- +(.*)$")
P2 = re.compile("^(.*): +[‘'](.*)[’']$")
P3 = re.compile("^(.*): +[‘'](.*)[’'] (.*)$")

G_NONE    = eyed3.id3.Genre()

def save(self, filename=None, version=None, encoding=None, backup=False, preserve_file_time=False, max_padding=None):
	if (self.artist and self.title and hasattr(self, 'dirty')):
		self.oldsave(filename, version, encoding,backup, preserve_file_time, max_padding)
		delattr(self, 'dirty')

eyed3.id3.tag.Tag.oldsave = eyed3.id3.tag.Tag.save
eyed3.id3.tag.Tag.save = save

def process_song(fname, name = None):
	a = eyed3.load(fname)

	if(not a or not a.tag):
		return

	a.tag.fname = os.path.basename(fname)
	if(a.tag.artist == "KEXP" or a.tag.artist == "KCRW" or a.tag.artist == "MPR"):
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
	elif(a.tag.artist and a.tag.title.startswith(a.tag.artist)):
		a.tag.title = a.tag.title.replace(a.tag.artist + " - " , "")
		a.tag.dirty = True
	else:
		print("NO PARSED", a.tag.fname)

	a.tag.genre  = G_NONE
	a.tag.save()

def onError(e):
	print("OnError:",e)

def dir_path(string):
	if os.path.isdir(string):
		return string
	else:
		raise NotADirectoryError(string)

def setup_args():
	parser = argparse.ArgumentParser(description='Id3 tags seter')
	parser.add_argument("directory", nargs='1', type=dir_path, help='Directory where files are', required=True)
	args = parser.parse_args()
	return args

def traverse(path):
	for dirName, subdirList, fileList in os.walk(path, onerror=onError):
		for fname in fileList:
			process_song("/".join([dirName, fname]),fname)


if __name__ == "__main__":
	args = setup_args()
	traverse(args.directory)

