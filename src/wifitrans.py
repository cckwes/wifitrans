#!/usr/bin/python

import sys
import BaseHTTPServer
import SimpleHTTPServer
import SocketServer
import cgi
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
import urlparse
import zipfile
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtDeclarative import *

class centerClass(QObject):
	requestIPAuth = Signal(str)
	
	def __init__(self):
		QObject.__init__(self)
		self.approvedIP = list()
		self.blackListedIP = list()
		self.passwd = ""
		self.username = ""
		self.showPhotoThumb = False
		self.settings = QSettings("Linux4us", "WifiTrans")
		self.customUP = self.getUsePassSettings()
		self.enableDel = False
		if self.customUP:
			#custom user name and password
			self.username = self.loadCustomUsername()
			self.passwd = self.loadCustomPassword()
		else:
			self.username = "n9user"
			self.generatePassword()

	def checkDeleteEnabled(self):
		return self.enableDel

	@Slot(bool)
	def setDeleteEnabled(self, delen):
		self.enableDel = delen

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
		
	@Slot(result=unicode)
	def getUsername(self):
		return self.username
		
	@Slot(result=int)
	def getWhiteLength(self):
		return len(self.approvedIP)
		
	@Slot(result=int)
	def getBlackLength(self):
		return len(self.blackListedIP)
	
	def checkPhotoThumb(self):
		return self.showPhotoThumb
	
	@Slot(str)
	def setPhotoThumb(self, thumb):
		if (thumb == "true"):
			self.showPhotoThumb = True
		else:
			self.showPhotoThumb = False
		
	@Slot(int,result=unicode)
	def getWhiteItem(self, itemIndex):
		if itemIndex < self.getWhiteLength():
			return self.approvedIP[itemIndex]
		else:
			return
	
	@Slot(int,result=unicode)
	def getBlackItem(self, itemIndex):
		if itemIndex < self.getBlackLength():
			return self.blackListedIP[itemIndex]
		else:
			return
	
	@Slot(str)
	def removeWhiteItem(self, whiteItem):
		self.approvedIP.remove(whiteItem)
	
	@Slot(str)
	def removeBlackItem(self, blackItem):
		self.blackListedIP.remove(blackItem)
	
	@Slot()
	def generatePassword(self):
		self.passwd = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for x in range(6))
		
	def getUsePassSettings(self):
		return bool(self.settings.value("customUP"))
	
	def loadCustomUsername(self):
		if str(self.settings.value("username")) == "None":
			#custom username not yet set
			return "n9user"
		else:
			return str(self.settings.value("username"))
	
	def loadCustomPassword(self):
		if str(self.settings.value("password")) == "None":
			return "password"
		else:
			return str(self.settings.value("password"))
	
	@Slot(str, str)
	def storeUsernamePass(self, usern, passw):
		self.username = usern
		self.passwd = passw
		self.settings.setValue("username", usern)
		self.settings.setValue("password", passw)
	
	@Slot(str)
	def storeCustom(self, custom):
		if (custom == "true"):
			self.settings.setValue("customUP", True)
		else:
			self.settings.setValue("customUP", False)
		
	@Slot(bool)
	def setCustomUP(self, custom):
		self.customUP = custom
		
	@Slot(result=bool)
	def getCustomUP(self):
		return self.customUP
		
	@Slot()
	def loadCustom(self):
		self.username = self.loadCustomUsername()
		self.passwd = self.loadCustomPassword()
		
	@Slot()
	def unloadCustom(self):
		self.username = "n9user"
		self.generatePassword()

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
		disp.write('<!DOCTYPE html>\n<html><head><meta charset="utf-8" /><title>%s</title>\n<link rel="stylesheet" href="/.wifitrans/main.css" type="text/css" />\n<script language="javascript" type="text/javascript" src="/.wifitrans/jquery.min.js"></script>\n<script language="javascript" type="text/javascript" src="/.wifitrans/jquery.contextMenu.js"></script>\n<link rel="stylesheet" href="/.wifitrans/jquery.contextMenu.css" type="text/css">' % (dirpath))
		
		if cc.checkDeleteEnabled():
			disp.write('<script type="text/javascript">\n\
			$(document).ready( function() {\n\
			\n\
			    $(".item").contextMenu({\n\
				menu: "myMenu"\n\
			    },\n\
				function(action, el, pos) {\n\
					if (confirm("confirm delete file/folder " + $.trim($(el).text()) + "?")) {\n\
						console.log("confirm delete " + $.trim($(el).text()));\n\
						console.log("current location: " + window.location);\n\
						window.location += "?file=" + $.trim($(el).text()) + "&method=r";\n\
					} else\n\
						console.log("na");\n\
			    });\n\
			});\n\
			</script>\n')
		
		disp.write('</head>\n\
		<body>\n<header>\n<div id="title">\n<h1>%s</h1>\n</div>\n</header>\n<article>\n<section class="archive">\n<a href="?method=a">Download folder as a zip file</a>\n</section>\n<section class="archive">\n<form action="" method="get">\n<input type="text" name="directory" placeholder="directory">\n<input type="hidden" name="method" value="d">\n<input type="submit" value="Create Directory">\n</form>\n</section>\n<ul>\n' % (dirpath))
		for r in listing:
			mimetype, _ = mimetypes.guess_type(r)
			#print r
			if os.path.isdir(os.path.join(abspath,r)):
				#directory
				disp.write('<li>\n<a href="%s">\n<div class="item">\n<img class="thumb" src="/.wifitrans/inode-directory.png" width="180">\n<div class="filename">%s</div>\n</div>\n</a>\n</li>\n' % (r,r) )
				#print os.path.join(abspath,r)
			elif r == '..':
				# ..
				disp.write('<li>\n<a href="%s">\n<div class="item">\n<img class="thumb" src="/.wifitrans/inode-directory.png" width="180">\n<div class="filename">%s</div>\n</div>\n</a>\n</li>\n' % (r,r) )
			elif mimetype is None:
				#none mimetype
				disp.write('<li>\n<a href="%s">\n<div class="item">\n<img class="thumb" src="/.wifitrans/unknown.png" width="180">\n<div class="filename">%s</div>\n</div>\n</a>\n</li>\n' % (r,r) )
			elif mimetype.startswith('image'):
				#image file
				if cc.checkPhotoThumb():
					disp.write('<li>\n<a href="%s">\n<div class="item">\n<img class="thumb" src="%s" width="180">\n<div class="filename">%s</div>\n</div>\n</a>\n</li>\n' % (r,r,r) )
				else:
					disp.write('<li>\n<a href="%s">\n<div class="item">\n<img class="thumb" src="/.wifitrans/image-x-generic.png" width="180">\n<div class="filename">%s</div>\n</div>\n</a>\n</li>\n' % (r,r) )
			elif mimetype.startswith('video'):
				#video file
				disp.write('<li>\n<a href="%s">\n<div class="item">\n<img class="thumb" src="/.wifitrans/video-x-generic.png" width="180">\n<div class="filename">%s</div>\n</div>\n</a>\n</li>\n' % (r,r) )
			elif mimetype.startswith('audio'):
				#audio file
				disp.write('<li>\n<a href="%s">\n<div class="item">\n<img class="thumb" src="/.wifitrans/audio-x-generic.png" width="180">\n<div class="filename">%s</div>\n</div>\n</a>\n</li>\n' % (r,r) )
			elif mimetype.startswith('text'):
				disp.write('<li>\n<a href="%s">\n<div class="item">\n<img class="thumb" src="/.wifitrans/text-x-generic.png" width="180">\n<div class="filename">%s</div>\n</div>\n</a>\n</li>\n' % (r,r) )
			elif mimetype.find('pdf') != -1:
				#pdf file
				disp.write('<li>\n<a href="%s">\n<div class="item">\n<img class="thumb" src="/.wifitrans/application-pdf.png" width="180">\n<div class="filename">%s</div>\n</div>\n</a>\n</li>\n' % (r,r) )
			else:
				disp.write('<li>\n<a href="%s">\n<div class="item">\n<img class="thumb" src="/.wifitrans/unknown.png" width="180">\n<div class="filename">%s</div>\n</div>\n</a>\n</li>\n' % (r,r) )
		disp.write('</ul>\n<div class="form">\n\
		<form id="upload" action="" method="POST" enctype="multipart/form-data">\n\
		<fieldset>\n\
		<legend>Upload to this folder</legend>\n\
		<div>\n<label for="fileselect">Files to upload:</label>\n<input type="file" id="fileselect" name="fileselect[]" multiple="multiple" />\n<div id="filedrag">or drop files here</div>\n\
		</div>\n\
		<div id="submitbutton">\n<button type="submit">Upload Files</button>\n\
		</div>\n\
		</fieldset>\n\
		</form>\n\
		</div>\n<div id="progress"></div>\n<div id="messages">\n<p>Status Messages</p>\n</div>\n\
		</article>\n<script src="/.wifitrans/filedrag.js"></script><ul id="myMenu" class="contextMenu">\n<li class="delete"><a href="#delete">Delete</a></li>\n</ul>\n</body>\n</html>')
		disp.seek(0)
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()
		self.wfile.write(disp.read())
		self.wfile.close()
		return 

	def do_GET(self):
		authorized = False
		user = cc.getUsername()
		passwod = cc.getPassword()
		
		auth_header = self.headers.getheader('authorization', '')
		m = re.match(r'^Basic (.*)$', auth_header)
		
		#print self.client_ip
		#get the parameter of GET
		self.qs = {}
		self.showPath = self.path
		if '?' in self.showPath:
			self.showPath, tmp = self.showPath.split('?', 1)
			self.qs = urlparse.parse_qs(tmp)
		print self.showPath, self.qs
		
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
				try:
					if self.qs['method'] == ['a/']:
						#folder archive
						zipFilename = '.wifitrans/folder.zip'
						zip = zipfile.ZipFile(zipFilename, 'w')
						self.zipPath = "/home/user/MyDocs" + self.showPath
						#print self.zipPath
						for dirname, subdirs, files in os.walk(self.zipPath):
							zip.write(dirname)
							print dirname
							for filename in files:
								zip.write(os.path.join(dirname, filename))
						zip.close()
						filepath = "/home/user/MyDocs/.wifitrans/folder.zip"
						f = open(filepath, 'rb')
						self.send_response(200)
						self.send_header('Content-type', 'application/octet-stream')
						self.send_header('Content-Disposition', 'attachment; filename="folder.zip"')
						self.end_headers()
						self.wfile.write(f.read())
						f.close()
						#remove the folder.zip for space saving
						os.remove(filepath)
					elif self.qs['method'] == ['d/']:
						#create a directory
						mkdirname = str(self.qs['directory']).strip("['']")
						#print mkdirname
						mkdirpath = "/home/user/MyDocs" + self.showPath + mkdirname
						print mkdirpath
						try:
							os.mkdir(mkdirpath)
						except OSError:
							print "directory already exists?"
						except:
							print "fail to create directory " + mkdirpath
						finally:
							print "directory" + mkdirpath + " created"
							self.send_response(301)
							self.send_header("Location", (self.showPath + mkdirname))
							self.end_headers()
					elif self.qs['method'] == ['r/']:
						if cc.checkDeleteEnabled():
							rmname = str(self.qs['file']).strip("['']")
							fullrmPath = "/home/user/MyDocs" + self.showPath + rmname
							print fullrmPath
							if os.path.exists(fullrmPath):
								if os.path.isdir(fullrmPath):
									#remove directory recursively
									shutil.rmtree(fullrmPath)
									print fullrmPath + " removed"
									self.send_response(301)
									self.send_header("Location", self.showPath)
									self.end_headers()
								else:
									#remove file
									os.remove(fullrmPath)
									print fullrmPath + " removed"
									self.send_response(301)
									self.send_header("Location", self.showPath)
									self.end_headers()
							#else:
								#self.send_response(301)
								#self.send_header("Location", self.showPath)
								#self.end_headers()
					elif self.path.endswith('/'):
						self.listDirectory(self.showPath)
					else:
						SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
						
				except KeyError:
					if self.path.endswith('/'):
						self.listDirectory(self.showPath)
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
	
	def do_POST(self):
		if cc.checkIP(self.client_ip):
			try:
				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				
				if ctype == 'multipart/form-data':
					fs = cgi.FieldStorage( fp = self.rfile, headers = self.headers, environ={ 'REQUEST_METHOD':'POST' })
				else: raise Exception("Unexpected POST request")
				
				fs_up = fs['fileselect']
				#print fs_up
				filename = os.path.split(fs_up.filename)[1] # strip the path, if it presents
				currentPath = "/home/user/MyDocs" + self.path
				fullname = os.path.join(currentPath, filename)
				
				if os.path.exists( fullname ):
					fullname_test = fullname + '.copy'
					i = 0
					while os.path.exists( fullname_test ):
					    fullname_test = "%s.copy(%d)" % (fullname, i)
					    i += 1
					fullname = fullname_test
				if not os.path.exists(fullname):
					with open(fullname, 'wb') as o:
					    # self.copyfile(fs['upfile'].file, o)
					    o.write( fs_up.file.read() )
					    #print fullname
					    #print os.path.split(fullname)[1]
					    
				self.send_response(200)
				self.end_headers()
				SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
			except Exception as e:
				print e
		else:
			self.send_response(200)
			self.send_header('Content-type', 'text/html')
			self.end_headers()
			self.wfile.write('<div align="center"><h2>Not permitted.</h2></div>')
			self.wfile.close()
		

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
	if not os.path.exists("/home/user/MyDocs/.wifitrans"):
		os.makedirs("/home/user/MyDocs/.wifitrans")
		print("Directory /home/user/MyDocs/.wifitrans created")
	
	#copy files
	fileList = ['application-x-compress.png', 'audio-x-generic.png', 'inode-directory.png', 'text-x-generic.png', 'unknown.png', 'video-x-generic.png', 'main.css', 'application-pdf.png', 'image-x-generic.png', 'filedrag.js', 'progress.png', 'jquery.min.js', 'jquery.contextMenu.js', 'jquery.contextMenu.css', 'delete.png']
	for f in fileList:
		fullDestPath = '/home/user/MyDocs/.wifitrans/' + f
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
