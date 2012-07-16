#!/usr/bin/python

import sys
import BaseHTTPServer
import SimpleHTTPServer
import SocketServer
import os
import cStringIO
import re
import socket
import fcntl
import struct
import mimetypes
import threading
import shutil
import random
import string
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtDeclarative import *

class centerClass(QObject):
	requestIPAuth = Signal(str)
	
	def __init__(self):
		QObject.__init__(self)
		self.approvedIP = list()
		self.blackListedIP = list()
		self.passwd = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for x in range(6))

	def checkBlackListed(self, ipAddr):
		if str(ipAddr) in self.blackListedIP:
			return True
		else:
			return False

	def checkIP(self, ipAddr):
		#print ipAddr
		if str(ipAddr) in self.approvedIP:
			return True
		else:
			return False

	@Slot(str)
	def addIP(self, okIP):
		#print okIP
		self.approvedIP.append(str(okIP))
		print self.approvedIP

	@Slot(str)
	def addBlackList(self, bIP):
		self.blackListedIP.append(str(bIP))
		print self.blackListedIP
		
	@Slot(result=unicode)
	def getPassword(self):
		return self.passwd

class HandlerClass(SimpleHTTPServer.SimpleHTTPRequestHandler):
	cc = centerClass()
	global approvedIP
	def __init__(self, req, addr, server):
		self.client_ip, self.client_port = addr
		SimpleHTTPServer.SimpleHTTPRequestHandler.__init__(self, req, addr, server)

	def listDirectory(self, dirpath):
		abspath = self.translate_path(dirpath) + '/'
		try:
			listing = os.listdir(abspath)
		except OSError:
			self.send_error(404, "File not found")
			return None
		
		listing = filter(lambda x: not x.startswith('.'), sorted(listing, key=lambda x: (0 if os.path.isdir(os.path.join(dirpath, x)) else 1, x.lower())))	
		#print listing
			
		if self.path != '/':
			listing.insert(0, '..')
			
		disp = cStringIO.StringIO()
		disp.write('<!DOCTYPE html>\n<html><head><title>%s</title>\n<link rel="stylesheet" href="/wifitrans/main.css" type="text/css" />\n</head>\n\
		<body>\n<header>\n<div id="title">\n<h1>%s</h1>\n</div>\n</header>\n<article>\n<ul>\n' % (dirpath,dirpath))
		for r in listing:
			mimetype, _ = mimetypes.guess_type(r)
			#print r
			if os.path.isdir(os.path.join(abspath,r)):
				#directory
				disp.write('<li>\n<a href="%s">\n<div class="item">\n<img class="thumb" src="/wifitrans/inode-directory.png" width="180">\n<div class="filename">%s</div>\n</div>\n</a>\n</li>\n' % (r,r) )
				#print os.path.join(abspath,r)
			elif r == '..':
				# ..
				disp.write('<li>\n<a href="%s">\n<div class="item">\n<img class="thumb" src="/wifitrans/inode-directory.png" width="180">\n<div class="filename">%s</div>\n</div>\n</a>\n</li>\n' % (r,r) )
			elif mimetype is None:
				#none mimetype
				disp.write('<li>\n<a href="%s">\n<div class="item">\n<img class="thumb" src="/wifitrans/unknown.png" width="180">\n<div class="filename">%s</div>\n</div>\n</a>\n</li>\n' % (r,r) )
			elif mimetype.startswith('image'):
				#image file
				disp.write('<li>\n<a href="%s">\n<div class="item">\n<img class="thumb" src="/wifitrans/image-x-generic.png" width="180">\n<div class="filename">%s</div>\n</div>\n</a>\n</li>\n' % (r,r) )
			elif mimetype.startswith('video'):
				#video file
				disp.write('<li>\n<a href="%s">\n<div class="item">\n<img class="thumb" src="/wifitrans/video-x-generic.png" width="180">\n<div class="filename">%s</div>\n</div>\n</a>\n</li>\n' % (r,r) )
			elif mimetype.startswith('audio'):
				#audio file
				disp.write('<li>\n<a href="%s">\n<div class="item">\n<img class="thumb" src="/wifitrans/audio-x-generic.png" width="180">\n<div class="filename">%s</div>\n</div>\n</a>\n</li>\n' % (r,r) )
			elif mimetype.startswith('text'):
				disp.write('<li>\n<a href="%s">\n<div class="item">\n<img class="thumb" src="/wifitrans/text-x-generic.png" width="180">\n<div class="filename">%s</div>\n</div>\n</a>\n</li>\n' % (r,r) )
			elif mimetype.find('pdf') != -1:
				#pdf file
				disp.write('<li>\n<a href="%s">\n<div class="item">\n<img class="thumb" src="/wifitrans/application-pdf.png" width="180">\n<div class="filename">%s</div>\n</div>\n</a>\n</li>\n' % (r,r) )
			else:
				disp.write('<li>\n<a href="%s">\n<div class="item">\n<img class="thumb" src="/wifitrans/unknown.png" width="180">\n<div class="filename">%s</div>\n</div>\n</a>\n</li>\n' % (r,r) )
		disp.write('</ul>\n</article>\n</body>\n</html>')
		disp.seek(0)
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()
		self.wfile.write(disp.read())
		self.wfile.close()
		return 

	def do_GET(self):
		authorized = False
		user = 'n9user'
		passwod = cc.getPassword()
		
		auth_header = self.headers.getheader('authorization', '')
		m = re.match(r'^Basic (.*)$', auth_header)
		
		#print self.client_ip
        
		if m is not None:
			auth_data = m.group(1).decode('base64').split(':', 1)
			if len(auth_data) == 2:
				username, password = auth_data
				if username == user and password == passwod:
					authorized = True
		if authorized:
			if cc.checkBlackListed(self.client_ip):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				self.wfile.write('<div align="center"><h2>Not permitted</h2></div>')
				self.wfile.close()
			elif cc.checkIP(self.client_ip):
				#print self.client_ip
				if self.path.endswith('/'):
					self.listDirectory(self.path)
				else:
					SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)	
			else:
				cc.requestIPAuth.emit(self.client_ip)
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				self.wfile.write('<div align="center"><h2>Not permitted. Please refresh the browser if you have allowed this IP address.</h2></div>')
				self.wfile.close()
		else:
			self.send_response(401)
			self.send_header('WWW-Authenticate', 'Basic realm="Home Server"')
			self.send_header('Content-type', 'text/html')
			self.end_headers()
			self.wfile.write('401 Access denied')
			self.wfile.close()
			return

class serverControl(QObject):
	def __init__(self):
		QObject.__init__(self)
		self.httpd = None
		self.thread = None
		
		#self.httpd = ServerClass(server_address, HandlerClass)

		#sa = self.httpd.socket.getsockname()

	@Slot()
	def startServer(self):
		self.thread = threading.Thread(target=self.serverProcess)
		self.thread.setDaemon(True)
		self.thread.start()

	@Slot()
	def stopServer(self):
		self.httpd.shutdown()
		self.httpd = None
		
	def get_ip_address(self, ifname):
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		return socket.inet_ntoa(fcntl.ioctl(
		s.fileno(),
		0x8915,  # SIOCGIFADDR
		struct.pack('256s', ifname[:15])
		)[20:24])
		
	@Slot(result=unicode)
	def retrieveIP(self):
		try:
			ip = self.get_ip_address('wlan0')
			return ip
		except:
			return

	def serverProcess(self):
		os.chdir('/home/user/MyDocs/')
		ServerClass = BaseHTTPServer.HTTPServer
		Protocol = "HTTP/1.0"

		port = 8080

		server_address = (self.get_ip_address('wlan0'), port)

		HandlerClass.protocol_version = Protocol
		try:
			self.httpd = ServerClass(server_address, HandlerClass)
		except:
			print "Fail"
		
		self.httpd.serve_forever()
		self.thread = None



if __name__== "__main__":
	app = QApplication(sys.argv)
	sc = serverControl()
	cc = centerClass()
	view = QDeclarativeView()
	
	#create user directory
	if not os.path.exists("/home/user/MyDocs/wifitrans"):
		os.makedirs("/home/user/MyDocs/wifitrans")
		print("Directory /home/user/MyDocs/wifitrans created")
	
	#copy files
	fileList = ['application-x-compress.png', 'audio-x-generic.png', 'inode-directory.png', 'text-x-generic.png', 'unknown.png', 'video-x-generic.png', 'main.css', 'application-pdf.png', 'image-x-generic.png']
	for f in fileList:
		fullDestPath = '/home/user/MyDocs/wifitrans/' + f
		fullSourcePath = '/opt/wifitrans/file/' + f
		if not os.path.exists(fullDestPath):
			shutil.copyfile(fullSourcePath, fullDestPath)
			print("Copied %s to %s" % (fullSourcePath,fullDestPath))
	
	rootContext = view.rootContext()
	rootContext.setContextProperty('sControl', sc)
	rootContext.setContextProperty('cControl', cc)
	view.setSource('/opt/wifitrans/bin/main.qml')
	rootObject = view.rootObject()
	appPage = rootObject.findChild(QObject, "appWindow")
	cc.requestIPAuth.connect(appPage.showThing)
	view.showFullScreen()
	sys.exit(app.exec_())
