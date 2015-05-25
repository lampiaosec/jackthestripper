#!/usr/bin/ruby
# Script to perform MITM (Man In The Middle) attacks using ARP poisoning to intercept all messages going between two targets.
# @depends iptables; ettercap; sslstrip.
#
# @authors 
# Cascudo <lucas.redeaberta.com.br>; 
# Elfotux <elfotux@gmail.com>;
# Neko <nekoone@riseup.net>;
# UserX <user_x@riseup.net>;
# @born 2014-10-19

require 'getoptlong'
require 'rake'
require 'open3'
require 'socket'


class String
def green;          "\033[32m#{self}\033[0m" end
end

def splash()
    print "    ____.              __     ___________.__            \n".green
    print "   |    |____    ____ |  | __ \\__    ___/|  |__   ____  \n".green
    print "   |    \\__  \\ _/ ___\\|  |/ /   |    |   |  |  \\_/  __ \\ \n".green
    print "/\__|    |/ __ \\\\  \\___|    <    |    |   |   Y  \   ___ / \n".green
    print "\________(____  /\\___  >__|_ \\   |____|   |___|  /\\___  >\n".green
    print "             \\/     \\/     \\/                 \\/     \\/ \n".green
    print "  _________ __         .__                               \n".green
    print " /   _____//  |________|__|_____ ______   ___________    \n".green
    print ' \_____  \\\\   __\\_  __ \\  \\____ \\\\____ \\_/ __ \\_  __ \\   \n'.green
    print " /        \\|  |  |  | \\/  |  |_> >  |_> >  ___/|  |\\/   \n".green
    print "/_______  /|__|  |__|  |__|   __/|   __/ \___  >__|      \n".green
    print "       \\/                |__|   |__|        \\/          \n".green
end


$storage = ARGV.clone

def introduceYourself()
    #Examples
    print "Example 1: jackthestripper\n"
    print "Example 2: jackthestripper -i wlan0 --ap 10.0.0.1 --t 10.0.0.3 --http-dos --dns-spoof --remote-browser\n"
    exit(0)
end

def checkCompliance(requirements)
    #Looks for broken dependencies
    isCompliant = true 
    userid = ENV['USER']

    #getting UserName
    if userid != "root"
        isCompliant = false;
        print "Sorry, an error occured, are you sure that your are root? (UserID: #{userid})\n"
    end
    # Testing system requirements.
    requirements.each do |required|
        system(required)
        if $?.success? != true
            isCompliant = false
            print "#{required} is not installed, please install it before proceed [!!]\n"
        end
    end
    if !isCompliant
        exit(2)
    end
end

def setParams()
    #Sets necessary parameters

    $networkInterface = ""
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
        [ '--t', GetoptLong::REQUIRED_ARGUMENT ])
    
    opts.each do |opt, arg| 
        if opt == '-h' or opt == "--help" 
            introduceYourself()
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

def getIpAddress()
    Socket::getaddrinfo(Socket.gethostname,"echo",Socket::AF_INET)[0][3]

end

def block()
    #Replaces all browsed pages with a pirate flag
    $networkInterface
    wwwroot = " "
    if File.directory?("/var/www/html")
	wwwroot = "/var/www/html"
    elsif File.directory?("/var/www")
	wwwroot = "/var/www"
    else wwwroot == " "
	print "Could not find a valid Apache path, please install apache2 or httpd before proceed"
    end
end

splash()
#checkCompliance (requirements)
#requirements = ["ls", "asdad", "ls"]
#setParams()
