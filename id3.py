#!/usr/bin/python3

import eyed3
import eyed3.id3
import os
import re
import gc
import psutil

import sys
import argparse

eyed3.log.setLevel("ERROR")

PATH = "/home/jose/Music/tmp"
#PATH = '/home/jose/Downloads/Podcast'

P1 = re.compile("^(.+): (.+)$")
P2 = re.compile("^(00 - )?(.+) ?- ?(.+)(\.mp3)?$")
P3 = re.compile("^(.+): (?:[\"\“]?)([^\"\”]+)(?:[\"\”]?)(.*)$")
P4 = re.compile("^(.+) ??- ?(.+)(?:\.mp3)$")
P5 = re.compile("^\\d{8}_[a-z_]+_128.mp3$")

G_PODCAST = eyed3.id3.Genre("Podcast")
G_SLASH   = eyed3.id3.Genre("/")
G_BLANK   = eyed3.id3.Genre("")
G_NONE    = eyed3.id3.Genre()
SKIP = [ "/home/jose/Music/London After Midnight/Oddities",
	]

i = 0
N = 0
M = 20

def save(self, filename=None, version=None, encoding=None, backup=False, preserve_file_time=False, max_padding=None):
	try:
		self.oldsave(filename, version, encoding,backup, preserve_file_time, max_padding)
	except:
		try:
			if(self.version):
				version = self.version
			else:
				version = eyed3.id3.ID3_ANY_VERSION
			self.oldsave(filename, version, encoding, backup, preserve_file_time, max_padding)
		except Exception as e:
			print(";(", e, version) 

eyed3.id3.tag.Tag.oldsave = eyed3.id3.tag.Tag.save
eyed3.id3.tag.Tag.save = save

def process_song(fname, name = None):
	a = eyed3.load(fname)

	if(not a or not a.tag):
		print(1)
		return

	a.tag.fname = fname

	if(a.tag.genre and a.tag.genre == G_PODCAST and a.tag.artist):
		m = P1.match(a.tag.artist)
		if(m):
			a.tag.artist = m.group(1)
			a.tag.title  = m.grou(2)
			a.tag.genre  = G_NONE
			a.tag.save()
			return
		print(2)
	if((a.tag.genre and a.tag.genre == G_PODCAST and a.tag.title) or
		(a.tag.genre and not a.tag.genre == G_NONE and a.tag.title)):
		m = P2.match(a.tag.title)
		if(m):
			print(1, m.group())
			a.tag.artist = m.group(1)
			a.tag.title  = m.group(2)
			a.tag.genre  = G_NONE
			a.tag.save()
			return
		print(3)
	if(a.tag.artist and (a.tag.artist == "KCRW" or a.tag.artist == "KEXP") and a.tag.title):
		m = P3.match(a.tag.title)
		if(m):
			a.tag.artist = m.group(1)
			if(m.group(3)):
				a.tag.title = m.group(2) + " (" + m.group(3) + ")"
			else:
				a.tag.title  = m.group(2)
			a.tag.save()
			return
		print(4)
	if(a.tag.artist and a.tag.artist == "KEXP" and a.tag.title):
		m = P4.match(a.tag.title)
		if(m):
			a.tag.artist = m.group(1)
			a.tag.title  = m.group(2)
			a.tag.genre  = G_NONE
			a.tag.save()
			return
		print(5)
	if(a.tag.artist and a.tag.artist == "MPR" and a.tag.title):
		m = P4.match(a.tag.title)
		if(m):
			a.tag.artist = m.group(1)
			a.tag.title  = m.group(2)
			a.tag.genre  = G_NONE
			a.tag.save()
			return
		print(6)
	if(name and P5.match(name)):
		#print(7)
		pass
	else:
		print(8, a.tag.fname)

def onError(e):
	print("OnError:",e)

def dir_path(string):
	if os.path.isdir(string):
		return string
	else:
		raise NotADirectoryError(string)

def setup_args():
	parser = argparse.ArgumentParser(description='Id3 tags parser')
	parser.add_argument("directory", nargs='?', type=dir_path, default="/home/jose/Music/tmp", help='Directory where files to parse are')
	args = parser.parse_args()
	return args

def traverse(path):
	i = 0
	for dirName, subdirList, fileList in os.walk(path, onerror=onError):
		if(dirName in SKIP):
			print(dirName, dirName in SKIP)
		else:
			for fname in fileList:
				i = i + 1
				if(i>N):
					process_song("/".join([dirName, fname]),fname)
				if(i % M == 0):
					print(psutil.Process().num_fds(), gc.get_stats(), i)


if __name__ == "__main__":
	args = setup_args()
	traverse(args.directory)

