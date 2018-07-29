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
        command.send("show inventory | i PID: WS\n")
        time.sleep(0.5)
        command.send("show flash: | i c2960\n")
        time.sleep(0.5)
        command.send("show boot | i BOOT path\n")
        time.sleep(0.5)
        output = command.recv(65535)
        command.send("wr mem\n")
        switch_model = re.search(r'WS-C2960\w?-\w{4,5}-L', output)
        ios_version = re.search(r'c2960\w?-\w{8,10}\d?-mz.\d{3}-\d{1,2}.\w{2,4}(.bin)?', output)
        boot_system = re.search(r'flash:.+mz.\d{3}-\d{1,2}\.\w{2,4}\.bin', output)
        if switch_model.group() == "WS-C2960-24PC-L" and ios_version.group() == "c2960-lanbasek9-mz.122-55.SE12.bin" and boot_system.group() == 'flash:c2960-lanbasek9-mz.122-55.SE12.bin' or boot_system.group() == 'flash:/c2960-lanbasek9-mz.122-55.SE12.bin':
            switch_upgraded.append(ip_address)
        elif switch_model.group() == "WS-C2960S-F24PS-L" and ios_version.group() == "c2960s-universalk9-mz.150-2.SE11.bin" and boot_system.group() == 'flash:c2960s-universalk9-mz.150-2.SE11.bin' or boot_system.group() == 'flash:/c2960s-universalk9-mz.150-2.SE11.bin':
            switch_upgraded.append(ip_address)
        elif switch_model.group() == "WS-C2960X-24PS-L" and ios_version.group() == "c2960x-universalk9-mz.152-2.E8.bin" and boot_system.group() == 'flash:c2960x-universalk9-mz.152-2.E8.bin' or boot_system.group() == 'flash:/c2960x-universalk9-mz.152-2.E8.bin':
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