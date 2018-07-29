#!/usr/bin/evn python
#-*- coding: utf8 -*-

import paramiko
import time
import getpass
import sys
import re
import socket

username = raw_input("Username: ")
password = raw_input("Password: ")
iplist = open('ip_list.txt','r+')

switch_upgraded = []
switch_not_upgraded = []
switch_with_tacacs_issue = []
switch_not_reachable = []

for line in iplist.readlines():
    try:
        ip_address = line.strip()
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=ip_address,username=username,password=password,look_for_keys=False)
        print "Successfully connect to ", ip_address
        command = ssh_client.invoke_shell(width=300)
        command.send("show ver | b SW Version\n")
        time.sleep(0.5)
        output = command.recv(65535)
        print output
        ios_version = re.search(r'\d{2}.\d\(\d{1,2}\)\w{2,4}', output)
        print boot_system.group()
        print ios_version.group()
        if ios_version.group() == '12.2(55)SE12':
            switch_upgraded.append(ip_address)
        elif ios_version.group() == '15.2(2)E8':
            switch_upgraded.append(ip_address)
        elif ios_version.group() == '15.0(2)SE11':
            switch_upgraded.append(ip_address)
        else:
            switch_not_upgraded.append(ip_address)
    except paramiko.ssh_exception.AuthenticationException:
        print "TACACS is not working for " + ip_address + "."
        switch_with_tacacs_issue.append(ip_address)
    except socket.error:
        print ip_address +  " is not reachable."
        switch_not_reachable.append(ip_address)   

iplist.close()
ssh_client.close

print '\nTACACS is not working for below switches: '
for i in switch_with_tacacs_issue:
    print i

print '\nBelow switches are not reachable: '
for i in switch_not_reachable:
    print i

print '\nBelow switches IOS version are up-to-date: '
for i in switch_upgraded:
    print i

print '\nBelow switches IOS version are not updated yet: '
for i in switch_not_upgraded:
    print i