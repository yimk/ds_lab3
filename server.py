import os,sys,socket,thread,threading
from chatroom import Chatroom

MAX_DATA_RECV = 9999 # max number of bytes we receive at once
BACKLOG = 50
chatroom = Chatroom()


def main():
	try:
		#start of the application
		server_port = int(sys.argv[1])

		#create the websocket
		server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		#get the local machine name
		host = ''

		#bind the socket
		server_socket.bind((host,server_port))

		#start to run the server
		print "Start Tracking!! server: %s" %server_port

		#wait for client, quene limited with backlog
		server_socket.listen(BACKLOG)
		run_server(server_socket,server_port )

	except socket.error, (value, message):
		if server_socket:
			server_socket.close()
		# print "Could not open socket:", message
		sys.exit(1)


def run_server(server_socket,server_port):

	while True:

		client_conn, client_addr = server_socket.accept()
		
		print "create new thread"
		thread.start_new_thread( connection_thread, (client_conn,client_addr,server_port ) )



def connection_thread(client_conn,client_addr,server_port ):

	#receive request from client


	while True:

		request = client_conn.recv(MAX_DATA_RECV)
		if request:
			print "Recieve request---------------------------\n"
			print request
			process_request(request,client_conn,server_port )


def process_request(request,client_conn,server_port):

	if request == 'KILL_SERVICE\n':

		print "Kill the service"
		
		chatroom.kill()
		sys.exit()


	elif request == "HELO BASE_TEST\n":
		print "Send back Hello"
		ip = get_ip_address()
		return_message = "HELO BASE_TEST\nIP:" + str(ip) + "\nPort:" + str(server_port) + "\nStudentID:" + "13329643" + "\n"
		print return_message
		client_conn.send(return_message)

	elif "JOIN_CHATROOM" in request:
		print "It is a JOIN CHATROOM REQUEST\n"
		chatroom.request_join_chatroom(request, client_conn, server_port)
		pass

	elif "LEAVE_CHATROOM" in request:
		print "It is a LEAVE CHATROOM REQUEST\n"
		chatroom.request_leaving_chatroom(request, client_conn, server_port)
		pass

	elif "CHAT" in request:
		print "It is a SEND MESSAGE REQUEST\n"
		chatroom.request_send_message(request, client_conn, server_port)
		pass
	elif "DISCONNECT" in request:
		print "It is a DISCONNECT REQUEST\n"
		chatroom.request_disconnect(request, client_conn, server_port)

	else:
		print "Nothing interesting"
		client_conn.send("Nothing interesting")

	print "Task Complete"

def get_ip_address():
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("8.8.8.8", 80))
		return s.getsockname()[0]

if __name__ == '__main__':
	main()








