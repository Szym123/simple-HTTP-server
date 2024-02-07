#!/usr/bin/env python3
# -*- coding: utf8 -*-

import os,sys,getopt,time,stat,re
from http.server import HTTPServer,BaseHTTPRequestHandler
from urllib.parse import urlparse

#global variables
Directory=""
File="plik.htm"
Tab=""

def print_help():
	print("Usage: ./httpServer.py [OPTION]...")
	print("sets up an HTTP server")
	print("directories should be opened at the same level of the directory tree than the script file")
	print()
	print("-a[=NUMBER]	set the network card, by default 0")
	print("-d[=DIRECTORY]	select DIRECTORY, there is no predefined one")
	print("-h	display help")
	print("-i[=FILE]	select a FILE, by defalt plik.htm")
	print("-p[=NUMBER]	set the port NUMBER, default is 9000")
	print()
	exit()

def check_file():#Check whether the file path is correct
	if os.path.exists(File):
		print("This file is ok")
	else:
		print("This file does not exist")
		exit()

def check_catalog():#Check whether the directory path is correct
	if os.path.exists(Directory):
		print("This directory is ok")
	else:
		print("This directory does not exist")
		exit()

def check_option(Tab):#Check whether 'i' and 'd' do not occur together
	if "d" in Tab and "i" in Tab:
		print("'i' and 'd' cannot apper together")
		exit()

def check(Tab):#Check if the input is correct
	check_option(Tab)
	for Key in Tab:
		if Key=="i":
			check_file()
		elif Key=="d":
			check_catalog()

def downloud():#Reading command line Option
	Port=9000
	Adress="0"
	global Tab
	global Directory
	global File

	opts,args=getopt.getopt(sys.argv[1:],"p:a:d:i:h")
	for o,b in opts:
		if o in("-p"):
			Tab+='p'
			Port=int(b)
		elif o in("-a"):
			Tab+='a'
			Adress=int(b)
		elif o in("-d"):
			Tab+='d'
			Directory=b   
		elif o in("-i"):
			Tab+='i'
			File=b
		elif o in("-h"):
			print_help()

	check(Tab)

	return Port,Adress

def check_mode(Info):#check whether it is a file, or a directory
	Mode=stat.S_ISDIR(Info.st_mode)
	if Mode==1:
		return 'C'
	else:
		return 'F'

def check_type(Key):#checks whaat extension the file has
	Word=re.search('\.[a-zA-Z0-9]+',Key)
	try:
		if Word.group()==".txt":
			return "text/plain"
		elif Word.group() in [".htm",".html"]:
			return "text/html"
		elif Word.group()==".PDF":
			return "application/pdf"
	except:
		return ""

def list_file(Directory,self):#display the directory
	List=os.listdir(Directory)

	self.send_response(200)
	self.send_header("Content-type", "text/html")
	self.end_headers()

	self.wfile.write(bytes("<html><head>","utf-8"))
	self.wfile.write(bytes("<style>.tab {display: inline-block; margin-left: 15px;}</style></head>","utf-8"))
	self.wfile.write(bytes("<body><h1>%s</h1><ul>" %Directory,"utf-8"))
	for Key in List:
		Info=os.stat(Directory+"/"+Key)
		Date=time.strftime("%b %d %H:%M",time.gmtime(Info.st_mtime))

		self.wfile.write(bytes('<li>%s<span class="tab"></span>' %check_mode(Info),"utf-8"))
		self.wfile.write(bytes('%s<span class="tab"></span>' %Info.st_size,"utf-8"))
		self.wfile.write(bytes('%s<span class="tab"></span>' %Date,"utf-8"))
		self.wfile.write(bytes('<a href=%s>' %(form_path(Directory)+"/"+Key),"utf-8"))
		self.wfile.write(bytes('%s</a><span class="tab"></span>' %Key,"utf-8"))
		self.wfile.write(bytes('%s</li>' %check_type(Key),"utf-8"))
	self.wfile.write(bytes("</ul></body></html>","utf-8"))

def print_file(File,self):#display the file
	self.send_response(200)
	self.send_header("Content-type", check_type(File))
	self.end_headers()

	with open(File,'rb')as file:
			self.wfile.write(file.read())

class MyServer(BaseHTTPRequestHandler):#Server class

	def do_GET(self):
		Url=urlparse(str(self.path))
		if 'd' in Tab:
			if Url.path=='/':
				list_file(Directory,self)
			else:
				if check_mode(os.stat(Directory+Url.path))=='C':
					list_file(Directory+Url.path,self)
				elif check_mode(os.stat(Directory+"/"+Url.path))=='F':
					print_file(Directory+Url.path,self)
		elif not('d' in Tab):
				print_file(File,self)

def main():
	Source=downloud()

	WebServer=HTTPServer((Source[1],Source[0]),MyServer)
	print("Start on the port:",Source[0])

	try:
		WebServer.serve_forever()
	except KeyboardInterrupt:
		pass

	WebServer.server_close()#when program is turn off, it turn off the servere
	print("Stop")

if __name__=="__main__":
	main()
