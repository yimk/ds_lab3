import os,sys,socket,thread,threading


# i am sending my message to my localhost php server
# i set:
	# my server host port to be 8000
#Constant variable

BACKLOG = 50
MAX_DATA_RECV = 999999 # max number of bytes we receive at once
server_port = 8010

MESSAGE = "JOIN_CHATROOM: test\nCLIENT_IP: [IP Address of client if UDP | 0 if TCP]\nPORT: [port number of client if UDP | 0 if TCP]\nCLIENT_NAME: ben"

LEAVING_MESSAGE = "LEAVE_CHATROOM: 0\nJOIN_ID: 1\nCLIENT_NAME: ben"
MESSAGE1 = "CHAT: 0\nJOIN_ID: 1\nCLIENT_NAME: ben \nMESSAGE: Hello\n\n"

def main():
	try:

		# get the local machine name
		host = ''
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

		
		# client_socket.send(LEAVING_MESSAGE)
		# recieve returning message from the server
		while True:
	 		data = client_socket.recv(999999)
			if data:
				print data
				
				if data.split(":")[0] == "JOINED_CHATROOM":
					client_socket.send(MESSAGE1)

				if data.split(":")[0] == "CHAT":
					print "leave"
					client_socket.send(LEAVING_MESSAGE)

				if data.split(":")[0] == "LEFT":
					print "leFT"
					break

	
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
		










