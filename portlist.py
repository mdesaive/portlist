"""
Usage: portlist.py [-o outputfile] [filename]

This script extracts relevant information from netstat output and
formats it the way it should be for displaying in the medneo
documentation server list.

netstat should be called as:
    Data collection with:
    ( LANG=C netstat --version; LANG=C netstat --inet -anp )| ssh <user>@<external host for scripting> tee <path on host>/netstat.$(uname -n).txt

    Process data with
    cat netstat.mel01wiki01.txt | python3 portlist.py | sort -k3 -k2n -k1 | uniq

If a filename is provided, the file should contain the netstat output.
If no filename is provided, portlist.py reads from stdin.

If a filename is provided with the parameter "-o" then the formatted
list of ports is written to that file.
If the parameter "-o" is omitted, the list of ports is written to
stdout.
"""



import argparse
import sys
import re
import pdb


parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input_file", help="input file") 
parser.add_argument("-o", "--output_file", help="output file")
args = parser.parse_args()

if args.output_file is None:
    output_file = sys.stdout
else:
    # TODO: check if file exists"
    output_file = open(args.output_file,"a")

if args.input_file is None:
    input_file = sys.stdin
else:
    # TODO: check if file exists!"
    input_file = open(args.input_file,"a")

# Check netstat version
netstat_versions = {'1.42':'default'}
re_version = re.compile('^netstat (\d*\.\d*) .*')
for line in input_file:
    match_version = re_version.match(line)
    if match_version is not None:
        netstat_actual_version = match_version.group(1)
        break
else:
    netstat_actual_version = '0'

if netstat_actual_version not in netstat_versions:
    print('Netstat version: ' + netstat_actual_version + ' not supported.')
    sys.exit(2)

if netstat_versions[netstat_actual_version] == 'default':
    # Read socket lines from netstat output
    re_socket_no_pid = re.compile('^(tcp|udp|raw)\s*\d*\s*\d*\s*([\d\.\*]*):([\d\*]*)\s*([\d\.\*]*):([\d\*]*)\s*(\w*)\s*-\s*\n')
    re_socket_with_pid = re.compile('^(tcp|udp|raw)\s*\d*\s*\d*\s*([\d\.\*]*):([\d\*]*)\s*([\d\.\*]*):([\d\*]*)\s*(\w*)\s*(\d*)\/([\w\-]*)\s*\n')
    for line in input_file:
        is_socket_line = False
        match_socket_with_pid = re_socket_with_pid.match(line)
        if match_socket_with_pid is not None:
            if match_socket_with_pid.group(1) == 'tcp':
                protocol = match_socket_with_pid.group(1)
                local_ip = match_socket_with_pid.group(2)
                local_port = match_socket_with_pid.group(3)
                remote_ip = match_socket_with_pid.group(4)
                remote_port = match_socket_with_pid.group(5)
                state = match_socket_with_pid.group(6)
                pid = match_socket_with_pid.group(7)
                program = match_socket_with_pid.group(8)
                is_socket_line = True
            if match_socket_with_pid.group(1) == 'udp':
                protocol = match_socket_with_pid.group(1)                        
                local_ip = match_socket_with_pid.group(2)                        
                local_port = match_socket_with_pid.group(3)                      
                remote_ip = match_socket_with_pid.group(4)                       
                remote_port = match_socket_with_pid.group(5)                     
                state = match_socket_with_pid.group(6)                           
                pid = match_socket_with_pid.group(7)                             
                program = match_socket_with_pid.group(8)
                is_socket_line = True
        else: 
            match_socket_no_pid = re_socket_no_pid.match(line)
            if match_socket_no_pid is not None:
                protocol = match_socket_no_pid.group(1)                         
                local_ip = match_socket_no_pid.group(2)                         
                local_port = match_socket_no_pid.group(3)                       
                remote_ip = match_socket_no_pid.group(4)                        
                remote_port = match_socket_no_pid.group(5)                      
                state = match_socket_no_pid.group(6)                              
                is_socket_line = True
                pid = ""
                program = ""
        if is_socket_line and program != "": 
            output_file.write(protocol +  " " +                               
            local_port + " " )                                           
#            state + " " )
            if local_ip == "127.0.0.1":
                output_file.write(program + " (lo)\n")
            else:
                output_file.write(program + "\n" ) 

if input_file is not sys.stdin:
    output_file.close()
if output_file is not sys.stdout:    
    input_file.close()
