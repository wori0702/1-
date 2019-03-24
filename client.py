import socket
import argparse
import glob
import os

def run(host, port, file):
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(file.encode())
        
        data= s.recv(1024)
        if not data:
                print("file no exist")
                return
        with open('./' + file, 'wb') as f:
                file_size = int(data.decode())
                data = s.recv(file_size)
                try:
                        f.write(data)
                except Exception as e:
                        print(e)

if __name__=='__main__':
    parser = argparse.ArgumentParser(description="Echo Client -p port -i host")
    parser.add_argument('-p', help="port_number", required = True)
    parser.add_argument('-i', help="host_name", required = True)
    parser.add_argument('-f', help="file_name",required = True)

    args = parser.parse_args()
    run(host=args.i,port=int(args.p),file=args.f)
