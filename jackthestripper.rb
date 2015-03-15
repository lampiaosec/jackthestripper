#!/usr/bin/ruby
# Script to perform MITM (Man In The Middle) attacks using ARP poisoning to intercept all messages going between two targets.
# @depends iptables; ettercap; sslstrip.
#
# @authors 
# Cascudo <lucas.redeaberta.com.br>; 
# Elfotux <elfotux@gmail.com>;
# Neko <nekoone@riseup.net>;
# UserX <user_x@riseup.net>;
# Code <code@riseup.net>.
# Music0 <musico@riseup.net>
# @born 2014-10-19

require 'getoptlong'
require 'rake'
require 'open3'


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
	

$storage = ARGV.clone

def introduceYourself()
    #Examples
    print "Example 1: jackthestripper"
    print "Example 2: jackthestripper -i wlan0 --ap 10.0.0.1 --t 10.0.0.3 --http-dos --dns-spoof --remote-browser"
    exit(0)
end

def checkCompliance(requirements)
    #Looks for broken dependencies
    isCompliant = true
    userid = %x<echo $UID>
    if userid != 0
        isCompliant = false;
        print "Sorry, an error occured, are you sure that your are root? (UserID: #{userid})\n"
    end
    requirements.each do |required|
    
        #p = Open3.popen3 (required) do |stdin, stdout, stderr, wait_thr|
        
        print "#{required} is not installed, please install it before proceed [!!]\n"
        
    end

=begin
    if isCompliant == false
        exit(2)
    end
=end
end

def setParams()
    #Sets necessary parameters

    $inetworkInterface = ""
    $useRemoteBrowser = ''
    $useDnsSpoof = ''
    $HTTPDPS = ''
    $ap = ""
    $target = ""
    opts = GetoptLong.new(
        [ '--help', '-h', GetoptLong::NO_ARGUMENT ],
        [ '--iface', '-i', GetoptLong::REQUIRED_ARGUMENT ],
        [ '--http-dos', GetoptLong::NO_ARGUMENT ],
        [ '--dns-spoof', GetoptLong::NO_ARGUMENT ],
        [ '--remote-browser', GetoptLong::NO_ARGUMENT ],
        [ '--ap', GetoptLong::REQUIRED_ARGUMENT ],
        [ '--t', GetoptLong::REQUIRED_ARGUMENT ]
    )
    
    opts.each do |opt, arg| 
        if opt == '-h' or opt == "--help" 
            print "--help typed!\n"
        elsif opt == '-i' or opt == "--iface"
            print "Network typed #{arg}\n"
            $networkInterface = arg 
        elsif opt == "--remote-browser"
            print "Network typed #{arg}\n"
            $useRemoteBrowser = 'y'
        elsif opt == "--dns-spoof"
            print "Network typed #{arg}\n"
            $useDnsSpoof = 'y'
        elsif opt == "http-dos"
            print "Network typed #{arg}\n"
            $HTTPDOS = 'y'
        elsif opt == "--ap"
            print "Network typed #{arg}\n"
            $ap = arg 
        elsif opt == "--t"
            $target = arg 
        end
    end
    
    while $networkInterface == ""
        print "Choose a network interface: "
        $networkInterface = gets.chomp
    end

    while $ap == ""
            print "Enter with AP ip number: "
            $ap = gets.chomp
    end

    while $target == ""
        print "Enter with IP target number: "
        $target = gets.chomp
    end
    while $useRemoteBrowser == ""
            print "Enable Remote Browser plugin?(y/n):  "
            $useRemoteBrowser = gets.chomp
    end
    while $HTTPDOS == ""
        print "HTTP DOS (y/n): "
        $HTTPDOS = gets.chomp
    end
    if $HTTPDOS == 'y'
            $useDnsSpoof = $HTTPDOS
    end
        
    while $useDnsSpoof == ""
        print "DNS-SPOOF (y/n): "
        $useDnsSpoof = gets.chomp
    end
    
end

requirements = ["ls", "ps", "ls"]
checkCompliance (requirements)

