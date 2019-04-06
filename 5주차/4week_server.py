'''
import socket
import argparse



def run_server(port=4000):
    host = ''

    with socket.socket(family=socket.AF_INET, type = socket.SOCK_STREAM) as s:
        s.bind((host,port))
        s.listen(1)
        
        conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Echo server -p port")
    parser.add_argument('-p', help="port_number", required = True)

    args = parser.parse_args()
    run_server(port=int(args.p))

'''

import socket
import threading
import argparse

def socket_handler(conn,addr):
    msg = conn.recv(1024)
    print("ip :" ,addr[0] ,"client port num = ", addr[1],"insert MSG :",msg.decode(),end=' ')
    msg = msg[::-1]
    print("return MSG : ",msg.decode())
    conn.sendall(msg)
    conn.close()
    # 여기에 클라이언트 소켓에서 데이터를 받고, 보내는 코드 작성
    # ex) conn.recv(1024)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Thread server -p port")
    parser.add_argument('-p', help = "port_number", required = True)

    args = parser.parse_args()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', int(args.p)))
    server.listen(5)

    while True:
        conn, addr = server.accept()
        test_thread = threading.Thread(target=socket_handler,args=(conn,addr))
        test_thread.start()
        #socket_handler(conn,addr)
        # 여기에 socket.accept 후 리턴받은 클라이언트 소켓으로 스레드를 생성하는 코드 작성

    server.close()
