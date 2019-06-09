import os
import socket
import argparse
import struct
import timeit
from functools import reduce

class Parsing :
	ether = None
	reply_ip = None # 응답 ip헤더
	send_ip = None # 내가 보낸 ip헤더
	reply_icmp	= None # 응답 icmp	
	reply_ip_header_len = 0
	reply_msg = ''
	reply_udp = None

	def __init__(self, raw_data, msg_len) :
		self.ip_header(raw_data[0:])
		self.icmp_header(raw_data[self.reply_ip_header_len:], msg_len)

	def ethernet_header(self, raw_data):
		self.ether = struct.unpack('!6B6BH', raw_data)

	def ip_header(self, raw_data) :
		self.reply_ip_header_len = (raw_data[0] & 0x0F) * 4
		ip_data = raw_data[0:self.reply_ip_header_len]
		ipOptionLen = self.reply_ip_header_len - 20
		if ipOptionLen == 0 :
			unpackType = '!BBHHHBBH4B4B'
		else :
			unpackType = '!BBHHHBBH4B4B' + str(ipOptionLen) + 'B'
		self.reply_ip = struct.unpack(unpackType, ip_data)

	def icmp_header(self, raw_data, msg_len) :
		self.reply_icmp = struct.unpack('!BBHHH', raw_data[0:8])
		# icmp[0] = type
		# icmp[1] = code
		# icmp[2] = checksum
		# icmp[3] = id
		# icmp[4] = seq
		if self.reply_icmp[0] == 0 and self.reply_icmp[1] == 0 :
			if msg_len > 64 :
				msg_len = 64
			self.reply_msg = str(struct.unpack('!'+ str(msg_len) + 's', raw_data[8:msg_len+8]))
			self.reply_msg = str(self.reply_msg[3:msg_len+3])
			pass
		elif self.reply_icmp[0] == 3 and self.reply_icmp[1] == 3 :
			self.send_ip = struct.unpack('!BBHHHBBH4B4B', raw_data[8:28])
			self.udp_header(raw_data[28:])
		else :
			self.send_ip = struct.unpack('!BBHHHBBH4B4B', raw_data[8:28])

	def udp_header(self, raw_data) :
		self.reply_udp = struct.unpack('!4H', raw_data)

class IP :
	version = 4 # 4bit
	header_len = 5 # 4bit
	tos = 0 # 1byte
	total_len = 0 # 2byte
	_id = 25252 # 2byte
	flag = 0 # 3bit
	offset = 0 # 13bit
	ttl = 1 # 1byte
	protocol = 0 # 1byte / 1 = ICMP / UDP = 17
	checksum = 0 # 2byte
	source = socket.inet_aton('0.0.0.0') # 4byte
	dest = None # 4byte
	header = None

	def __init__ (self, destination, data_len, hops, proto) :
		self.dest = socket.inet_aton(destination)
		self.ttl = hops
		self.protocol = proto
		self.set_total_len(data_len)
		self.assemble()
		len(self.header)

	def set_total_len(self, data_len) :
		self.total_len = 20 + data_len

	def assemble (self) :
		ver_hlen = (self.version << 4) + self.header_len
		flag_offset = (self.flag << 13) + self.offset
		self.header = struct.pack('!BBHHHBBH4s4s', ver_hlen, self.tos, self.total_len, 
		self._id, flag_offset, self.ttl, self.protocol, self.checksum, 
		self.source, self.dest)

class ICMP :
	pType = 8 # 1byte
	code = 0 # 1byte
	checksum = 0 # 2byte
	_id = 0 # 2byte
	sequence = 0 # 2byte
	header = None
	msg = ''
	total_len = 0 # icmp 패킷 총 길이
	max_hop = 0
	ip = None
	tout = 0
	next_proto = 0

	def __init__(self, destination, size, timeout, hops, proto) :
		self.msg = 'F' * (size - 28) # ip헤더 + icmp헤더 = 28byte
		self.tout = timeout
		self.max_hop = hops
		self.set_checksum()
		self.assemble()
		self.next_proto = proto
		self.icmp_request(destination)

	def set_checksum(self) :
		type_code = (self.pType << 8) + self.code
		_sum = type_code + self.checksum + self._id + self.sequence
		data = self.msg.encode()
		size = len(data)
		self.total_len = size + 8 
		if (size % 2) == 1 :
			data += b'\x00'
			size += 1
		size = size // 2
		data = struct.unpack('!' + str(size) + 'H', data)
		_sum += reduce(lambda x, y : x+y, data)
		self.checksum = (_sum >> 16) + (_sum & 0xFFFF)
		self.checksum += self.checksum >> 16
		self.checksum = (self.checksum ^ 0xFFFF)

	def assemble (self) :
		self.header = struct.pack('!BBHHH', self.pType, self.code, self.checksum,
			self._id, self.sequence)

	def icmp_request (self, dest) :
		with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW) as sock :
			arrive_flag = False # 목적지 도착시 True로 변환 -> 반복문 탈출
			for i in range(1, self.max_hop+1) :
				self.ip = IP(dest, self.total_len, i, self.next_proto)
				total_packet = self.ip.header + self.header + self.msg.encode()
				my_ip_header = struct.unpack('!BBHHHBBH4B4B', self.ip.header)
				print('%02d' %i, end = "  ")
				for j in range(0, 3) :
					start = timeit.default_timer()
					sock.sendto(total_packet, (args.d, 8888))
					self.icmp_recv()
					end = timeit.default_timer()
					if self.reply is None :
						print(' * ', end = "  ")
					else :
						packet = Parsing(self.reply, len(self.msg))
						addr = {'reply' : '%d.%d.%d.%d' %packet.reply_ip[8:12]}
						if packet.reply_icmp[0] == 11 and packet.reply_icmp[1] == 0 :
							if ( packet.send_ip[0] == my_ip_header[0] # checksum, source는 0으로 채워 보내므로 제외
								and (packet.send_ip[1] == my_ip_header[1] or packet.send_ip[1] == 128)
								and packet.send_ip[2] == my_ip_header[2]
								and packet.send_ip[3] == my_ip_header[3]
								and packet.send_ip[4] == my_ip_header[4]
								and packet.send_ip[5] == 1
								and packet.send_ip[6] == my_ip_header[6]
								and packet.send_ip[12:] == my_ip_header[12:]) :
								print('%.2f ms' %((end-start)*1000), end = "  ")
								if j == 2 :
									try :
										name = socket.gethostbyaddr(addr['reply'])[0]
										p_addr = str(socket.gethostbyaddr(addr['reply'])[2])
										print('[', name, end = ", ")
										print(p_addr.strip('[]'), ']', end = " ")
									except :
										print('[', addr['reply'].strip('[]'), ']', end = " ")
						elif packet.reply_icmp[0] == 0 and packet.reply_icmp[1] == 0 :
							if len(self.msg) > 64 : # 목적지 도착시 응답 패킷의 데이터 길이가 최대 64byte이다.
								self.msg = 'F' * 64
							if packet.reply_icmp[3] == 0 and packet.reply_msg == self.msg :
								print('%.2f ms' %((end-start)*1000), end = "  ")
								if j == 2 :
									try :
										name = socket.gethostbyaddr(addr['reply'])[0]
										p_addr = str(socket.gethostbyaddr(addr['reply'])[2])
										print('[', name, end = ", ")
										print(p_addr.strip('[]'), ']')
										print('Destination arrive')	
									except :
										print('[', addr['reply'].strip('[]'), ']')
										print('Destination arrive')
									arrive_flag = True
									print('전송 메세지 : ', packet.reply_msg, end = "")
									break
				print("")
				if arrive_flag :
					break

	def icmp_recv (self) :
		with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP) as recv_sock :
			recv_sock.settimeout(self.tout)
			try :
				self.reply, _ = recv_sock.recvfrom(65535)
			except :
				self.reply = None

class UDP :
	# Traceroute를 돌린 source / dest port를 참고하였음
	s_port = 52131 # 2byte
	d_port = 33434 # 2byte
	length = 0 # 2byte
	checksum = 0 # 2byte
	msg = ''
	tout = 0
	max_hop = 0
	header = None
	ip = None
	next_proto = 0

	def __init__(self, destination, size, timeout, hops, port, proto) :
		self.msg = 'F' * (size - 28) # ip(20) + udp(8) 28byte
		self.d_port = port
		self.length = 8 + len(self.msg)
		self.tout = timeout
		self.max_hop = hops
		self.assemble()
		self.next_proto = proto
		self.udp_request(destination)

	def assemble(self) :
		self.header = struct.pack('!4H', self.s_port, self.d_port, self.length, self.checksum)
	
	def udp_request (self, dest) :
		with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW) as sock :
			arrive_flag = False # 목적지 도착시 True로 변환 -> 반복문 탈출
			for i in range(1, self.max_hop+1) :
				self.ip = IP(dest, self.length, i, self.next_proto)
				total_packet = self.ip.header + self.header + self.msg.encode()
				my_ip_header = struct.unpack('!BBHHHBBH4B4B', self.ip.header)
				print('%02d' %i, end = "  ")
				for j in range(0, 3) :
					start = timeit.default_timer()
					sock.sendto(total_packet, (args.d, 0))
					self.udp_recv()
					end = timeit.default_timer()
					if self.reply is None :
						print(' * ', end = "  ")
					else :
						packet = Parsing(self.reply, len(self.msg))
						addr = {'reply' : '%d.%d.%d.%d' %packet.reply_ip[8:12]}
						if packet.reply_icmp[0] == 11 and packet.reply_icmp[1] == 0 :
							if (packet.send_ip[0] == my_ip_header[0]  # checksum, source는 0으로 채워 보내므로 제외
								and (packet.send_ip[1] == my_ip_header[1] or packet.send_ip[1] == 128) # ToS 0 or 48 return
								and packet.send_ip[2] == my_ip_header[2]
								and packet.send_ip[3] == my_ip_header[3]
								and packet.send_ip[4] == my_ip_header[4]
								and packet.send_ip[5] == 1
								and packet.send_ip[6] == my_ip_header[6]
								and packet.send_ip[12:] == my_ip_header[12:]) :
								print('%.2f ms' %((end-start)*1000), end = "  ")
								if j == 2 :
									try :
										name = socket.gethostbyaddr(addr['reply'])[0]
										p_addr = str(socket.gethostbyaddr(addr['reply'])[2])
										print('[', name, end = ", ")
										print(p_addr.strip('[]'), ']', end = " ")
									except :
										print('[', addr['reply'].strip('[]'), ']', end = " ")
						if packet.reply_icmp[0] == 3 and packet.reply_icmp[1] == 3 :
							if (packet.send_ip[3] == my_ip_header[3]
								and packet.reply_udp[1] == self.d_port) :
								print('%.2f ms' %((end-start)*1000), end = "  ")
								if j == 2 :
									try :
										name = socket.gethostbyaddr(addr['reply'])[0]
										p_addr = str(socket.gethostbyaddr(addr['reply'])[2])
										print('[', name, end = ", ")
										print(p_addr.strip('[]'), ']')
										print('Destination arrive', end = "")	
									except :
										print('[', addr['reply'].strip('[]'), ']')
										print('Destination arrive', end = "")	
									arrive_flag = True			
				print("")
				self.d_port += 1
				self.assemble()
				if(arrive_flag == True) :
					break

	def udp_recv (self) :
		with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP) as recv_sock :
			recv_sock.settimeout(self.tout)
			try :
				self.reply, _ = recv_sock.recvfrom(65535)
			except :
				self.reply = None

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='This is traceroute')
	group = parser.add_mutually_exclusive_group()
	parser.add_argument('d', type=str, metavar='[Domain address]')
	parser.add_argument('s', type=int, metavar='[packet size]')
	parser.add_argument('-t', type=int, required=False, default=1, metavar='[recv time]')
	parser.add_argument('-c', type=int, required=False, default=30, metavar='[max hops]')
	group.add_argument('-I', '--icmp', action='store_true')
	group.add_argument('-U', '--udp', action='store_true')
	parser.add_argument('-p', type=int, required=False, default=33434, metavar='[UDP PORT]')
	args = parser.parse_args()
	ip_addr = socket.gethostbyname(args.d)
	print('Traceroute to', args.d, '(', ip_addr, '),', args.c, 'hops max,', args.s, 'byte packets')
	if args.udp :
		print('Protocol : UDP')
		udp = UDP(ip_addr, args.s, args.t, args.c, args.p, 17)
	else :
		print('Protocol : ICMP')
		icmp = ICMP(ip_addr, args.s, args.t, args.c, 1)