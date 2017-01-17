import os,sys,socket,thread,threading


# i am sending my message to my localhost php server
# i set:
	# my server host port to be 8000
#Constant variable

BACKLOG = 50
MAX_DATA_RECV = 999999 # max number of bytes we receive at once
server_port = 4093

MESSAGE = "JOIN_CHATROOM: test\nCLIENT_IP: [IP Address of client if UDP | 0 if TCP]\nPORT: [port number of client if UDP | 0 if TCP]\nCLIENT_NAME: steve"


def main():
	try:

		# get the local machine name
		host = '134.226.32.10'
		server_port = int(sys.argv[1])
		print host

		# create the client socket
		client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		# connect to the server
		client_socket.connect((host, server_port))

		print "Part 1 -------------------------------------"


		# send message to the server
		header = "GET /echo.php?message=" + MESSAGE + " HTTP/1.0\r\n\r\n"
		print "Message: " + MESSAGE
		client_socket.send(MESSAGE)

		# recieve returning message from the server
		while 1:
	 		data = client_socket.recv(999999)
			if data:
				print data


	
		# Terminate	
		client_socket.close()
		sys.exit(1)

	except socket.error, (value, message):
	  if client_socket:
	      client_socket.close()
	  print "Could not open socket:", message
	  sys.exit(1)

if __name__ == '__main__':
	main()
		










