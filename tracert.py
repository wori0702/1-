import os
import socket
import argparse
import struct
import timeit
from functools import reduce

class IP:
    

    def __init__(self,size,dst='127.0.0.1',protocol = 1):
        self.src = socket.inet_aton('0.0.0.0')
        self.dst = socket.inet_aton(dst)
        self.ip_ver = 4
        self.ip_hl = 5
        self.tos =0
        self.tol=size
        self.fid=25252
        self.f_rsv=0
        self.f_dtf=0
        self.f_mrf=0
        self.f_offset=0
        self.ttl=1
        self.checksum=0
        self.proto = protocol

    def make_IP_header(self):
        self.V_HL = self.ip_ver<<4 | self.ip_hl
        self.mrf_offset = self.f_mrf<<13 | self.f_offset
        pack = struct.pack('!2B3H2BH',self.V_HL,self.tos,self.tol,self.fid,self.mrf_offset,self.ttl,self.proto,self.checksum)
        return pack + self.src + self.dst

class ICMP:

    def __init__(self,data='Hi'):
        self.type = 8
        self.code = 0
        self.checksum=0
        self.id=0
        self.seq = 1
        self.data = data if isinstance(data,bytes)else data.encode()

    def setchecksum(self,chk):
        self.checksum= chk
    
    def make_ICMP_header(self):
        return struct.pack('!BBHHH',self.type,self.code,self.checksum,self.id,self.seq)+self.data

class UDP:
    
    def __init__(self,port, data='Hi'):
        self.src_port = 6000
        self.dst_port = port
        self.length =8 + len(data)
        self.checksum=0
        self.data = data if isinstance(data,bytes)else data.encode()
    
    def make_UDP_header(self):
        return struct.pack('!4H',self.src_port,self.dst_port,self.length,self.checksum) + self.data


 
def make_checksum(header):
    size = len(header)
    if (size %2) ==1:
        header += b'\x00'
        size +=1
    size = size//2
    header = struct.unpack('!'+str(size) + 'H',header)
    sum = reduce(lambda x,y:x+y,header)
    chksum = (sum>>16)+(sum& 0xffff)
    chksum += chksum>>16
    chksum = (chksum ^ 0xffff)
    
    return chksum

def send_msg(MSG,ip):
    with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW) as trace_sock:

        trace_sock.sendto(MSG,(ip,8888))

def get_msg(time):
    
    with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP) as back_sock:
    
        back_sock.settimeout(time)
        try:
            data, _ = back_sock.recvfrom(65535)
            return data
        except :
            return None

def icmproute(address,hop_cnt,recv_time,size):
    print("USING PROTOCOL : ICMP")
    
    data = 'F'*(size - 28)
    ip = socket.gethostbyname(address)
    ip_header = IP(size,ip)
    icmp_header = ICMP(data)
    switch = False
    Name=""
    addr=""
    for i in range (1,hop_cnt+1):

        chk = make_checksum(icmp_header.make_ICMP_header())
        icmp_header.setchecksum(chk)
        MSG=ip_header.make_IP_header()+icmp_header.make_ICMP_header()
        
        if switch == True:
            break
        
        print('\n%02d' %i , end="  ")

        for three in range(0,3):
            send_msg(MSG,ip)
            start = timeit.default_timer()  
            recv_data = get_msg(recv_time)           #정보 가지고오기
            end = timeit.default_timer()
            
            if recv_data ==  None:
                print("*",end = " ")
            else:


                recv_type =struct.unpack("!BB",recv_data[20:22])
                middle_ip =struct.unpack("!4B",recv_data[12:16])
                Name = socket.gethostbyaddr('%s.%s.%s.%s'%middle_ip[0:4])[0]                #11왔을때 ip패킷 비교하는거 짜야함.
                addr = '%s.%s.%s.%s' %middle_ip[0:4]
                if recv_type[0] ==0 and recv_type[1] == 0 :
                    print('%.2f ms' %((end-start)*1000), end = "  ")

                    recv_id = struct.unpack("!H",recv_data[24:26])       

                    if icmp_header.id == recv_id[0] and icmp_header.data == recv_data[28:]:        
                        if three ==2:
                            switch= True
                            break

                elif recv_type[0] == 11 and recv_type[1] ==0:                                   #timeeceeded 부분
                    packet = struct.unpack("!BBHHHBBH4B",recv_data[28:44])
                    
                    if  (packet[0]==ip_header.V_HL and packet[1] == ip_header.tos and packet[2] == ip_header.tol                #여기 지금 문제있디
                    and packet[3]==ip_header.fid and packet[4] == ip_header.mrf_offset 
                    and packet[5] == ip_header.ttl and packet[6] == ip_header.proto and ip_header.dst == recv_data[44:48]):
                        print('%.2f ms' %((end-start)*1000), end = "  ")

        if Name != None and addr != None:
            print("["+Name+","+addr+"]",end="")
            Name=None
            addr=None
        
        ip_header.ttl += 1
        
    if switch == True:
        print("\nrouting complete")
    else :
        print("\nroting failed")


def udproute(address,hop_cnt,recv_time,use_port,size):
    print("USING PROTOCOL : UDP")
    data = 'F'*(size - 28)
    ip = socket.gethostbyname(address)
    ip_header = IP(size,ip,17)
    udp_header = UDP(use_port,data)
    switch = False

    for i in range(1,hop_cnt+1):

        if switch == True:
            break
        MSG = ip_header.make_IP_header()+udp_header.make_UDP_header()
        
        print('\n%02d' %i , end="  ")

        for three in range(0,3):

            send_msg(MSG,ip)
            start = timeit.default_timer()
            recv_data = get_msg(recv_time)
            end = timeit.default_timer()    
            if recv_data ==  None:
                print("*     ",end = " ")
            else:
                recv_type =struct.unpack("!BB",recv_data[20:22])
                middle_ip =struct.unpack("!4B",recv_data[12:16])
                try:
                    Name = socket.gethostbyaddr('%s.%s.%s.%s'%middle_ip[0:4])[0] 
                    addr = '%s.%s.%s.%s' %middle_ip[0:4]
                except(socket.herror):
                    print("??")

                if recv_type[0] == 11 and recv_type[1] == 0:
                    packet = struct.unpack("!BBHHHBBH4B",recv_data[28:44])
                    
                    if  (packet[0]==ip_header.V_HL and packet[1] == ip_header.tos and packet[2] == ip_header.tol
                    and packet[3]==ip_header.fid and packet[4] == ip_header.mrf_offset 
                    and packet[5] == ip_header.ttl and packet[6] == ip_header.proto and ip_header.dst == recv_data[44:48]):
                        print('%.2f ms' %((end-start)*1000), end = "  ")


                elif recv_type[0] == 3 and recv_type[1] ==3:
                    print('%.2f ms' %((end-start)*1000), end = "  ")
                    
                    recv_id = struct.unpack("!H",recv_data[10:12])  #IP의 id
                    recv_port = struct.unpack("!H",recv_data[50:52]) #UDP의 port
                    
                    if ip_header.fid == recv_id[0] and udp_header.dst_port == recv_port[0] :
                        if three ==2:
                            switch=True
                    

        if Name != None and addr != None:
            print("["+Name+","+addr+"]",end="")
            Name=None
            addr=None

        ip_header.ttl +=1
    
    if switch == True:
        print("\nrouting complete")
    else :
        print("\nroting failed")




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Do the tracert")
    group = parser.add_mutually_exclusive_group()
    parser.add_argument('-d', type=str, required=True, metavar='Destiny ip|Domain', help='Destiny ip|Domain')
    parser.add_argument('-c', type=int, required=False, default=30, metavar='max hops')
    parser.add_argument('-t', type=int, required=False,default= 1.0, metavar='recv_time')
    parser.add_argument('-s', type=int, required=False,default=30,metavar='size')
    group.add_argument('-I', '--icmp', action='store_true')
    group.add_argument('-U', '--udp', action='store_false')
    parser.add_argument('-p',type=int, required=False, default=33434,metavar='udp_port')
    
    args = parser.parse_args()

    print("traceroute to" + args.d + "(" +socket.gethostbyname(args.d) + ")," + str(args.c) + "hops max")
    if args.icmp:
        icmp = icmproute(args.d,args.c,args.t,args.s)
    else:
        udp = udproute(args.d,args.c,args.t,args.p,args.s)
    
