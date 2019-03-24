import socket
import argparse
import os
import glob

def run_server(port=4000,file_dir='*'):
    host = ''

    with socket.socket(family=socket.AF_INET, type = socket.SOCK_STREAM) as s:
        s.bind((host,port))
        s.listen(1)
        file_list_link = file_dir + "/*"
        file_list=glob.glob(file_list_link)
        for i in file_list:
                print(i)

        conn, addr = s.accept() 
        msg = conn.recv(1024)
        file_name = msg.decode()
        link = file_dir + "\\" + file_name
        if link in file_list:
                file_size= str(os.path.getsize(link))
                conn.sendall(file_size.encode())
                with open(link, 'rb')as f:
                        files = f.read(int(file_size))
                        conn.send(files)
        else:
                print("file no exist")

        conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Echo server -p port -d direct")
    parser.add_argument('-p', help="port_number", required = True)
    parser.add_argument('-d',help="file_dir", required = True)

    args = parser.parse_args()
    run_server(port=int(args.p),file_dir = args.d)