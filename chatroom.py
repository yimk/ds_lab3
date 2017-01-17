import sqlite3 as lite
import os,sys,socket,thread,threading
import fcntl
import struct


class Chatroom:

	JOIN_CHATROOM_RESPONSE_PROTOCOL = ["JOINED_CHATROOM","SERVER_IP","PORT","ROOM_REF","JOIN_ID"]
	SEND_MESSAGE_PROTOCOL = ["CHAT","JOIN_ID","CLIENT_NAME","MESSAGE","",""]
	SEND_MESSAGE_REPSONSE_PROTOCOL = ["CHAT","CLIENT_NAME","MESSAGE"]
	LEAVE_CHATROOM_RESPONSE_PROTOCOL = ["LEFT_CHATROOM","JOIN_ID"]

	# list of all chatrooms , each chatroom's index in the list is it's reference
	chatrooms = []
	# list of all users names, it's index is this user's join id
	users_name = []
	# list of all users' corresponding group,
	users_corresponding_group = []
	# list of users' connection e.g users_conns[0].send(message)
	users_conns = []

	ip = ''

	def __init__(self):
		self.ip = self.get_ip_address()
		print self.ip
		pass


	def request_join_chatroom(self,request,client_conn,port):
		
		# Parse request for essential information
		request_lines = request.split("\n")
		room_name = request_lines[0].split(":")[1]
		client_name =  request_lines[3].split(":")[1]

		#Join the chatroom
		if not self.is_chatroom_exist( room_name ): 
			self.create_chatroom( room_name )
		
		(room_ref, join_id) = self.join_chatroom( room_name ,client_name ,client_conn)

		
		# responds to the client that the joiniing is sucecesful
		return_message = self.JOIN_CHATROOM_RESPONSE_PROTOCOL[0] + ':' + room_name +'\n'
		return_message = return_message + self.JOIN_CHATROOM_RESPONSE_PROTOCOL[1] + ':' + str(self.ip) +'\n'
		return_message = return_message + self.JOIN_CHATROOM_RESPONSE_PROTOCOL[2] + ':' + str(port) +'\n'
		return_message = return_message + self.JOIN_CHATROOM_RESPONSE_PROTOCOL[3] + ':' + str(room_ref) +'\n'
		return_message = return_message + self.JOIN_CHATROOM_RESPONSE_PROTOCOL[4] + ':' + str(join_id) +'\n'
		client_conn.send(return_message)

		# broadcast the joining of new members in the chat room
		message = "CHAT:%s\nCLIENT_NAME:%s\nMESSAGE:%s has joined this chatroom.\n\n" %(str(room_ref),str(client_name),str(client_name))
		self.broadcast_within_room(message,room_ref)

		
		print "JOIN SUCCESFULLY\n"
		return True

	def request_leaving_chatroom(self,request,client_conn,server_port):

		# Parse request for essential information
		request_lines = request.split("\n")
		room_ref = request_lines[0].split(":")[1]
		join_id =  request_lines[1].split(":")[1]
		client_name =  request_lines[2].split(":")[1]
		

		# responds to the client
		return_message = self.LEAVE_CHATROOM_RESPONSE_PROTOCOL[0] + ':' + room_ref +'\n'
		return_message = return_message + self.LEAVE_CHATROOM_RESPONSE_PROTOCOL[1] + ':' + join_id +"\n"

		print ("Sent Response:\n%s") %(return_message)

		client_conn.send(return_message)

		message = "CHAT:%s\nCLIENT_NAME:%s\nMESSAGE:%s has left chatroom.\n\n" %(str(room_ref),str(client_name),str(client_name))
		self.broadcast_within_room(message,room_ref)
		self.leave_chatroom(join_id, room_ref)
		return True

	def request_disconnect(self,request,client_conn,server_port):

		# Parse request for essential information
		request_lines = request.split("\n")
		client_name =  request_lines[2].split(":")[1]
		join_id = self.users_name.index(client_name)
		
		print "Disconnection:"
		print "Client: ", client_name
		print "ID: ", join_id
		print "Room: ",  self.users_corresponding_group[join_id], " \n"

		room_list = list( self.users_corresponding_group[join_id] )

		for room_ref in room_list:

			message = "CHAT:%s\nCLIENT_NAME:%s\nMESSAGE:%s has left chatroom.\n\n" %(str(room_ref),str(client_name),str(client_name))
			self.broadcast_within_room(message,room_ref)
			self.leave_chatroom(join_id, room_ref)

		return True


	def request_send_message(self,request,client_conn,server_port):

		# Parse request for essential information
		request_lines = request.split("\n")
		room_ref = request_lines[0].split(":")[1]
		join_id =  request_lines[1].split(":")[1]
		clinet_name =  request_lines[2].split(":")[1]
		message =  request_lines[3].split(":")[1]

		message = "CHAT: %s\nCLIENT_NAME: %s\nMESSAGE: %s\n\n" % (room_ref, clinet_name, message)

		self.broadcast_within_room(message,room_ref)
		return True

	def create_chatroom(self,room):

		# add new chatromm
		print "Create CHATRoom", room
		self.chatrooms.append(room)

	def join_chatroom(self,room,user,client_conn):

		# get the ref of the chat room
		ref = self.chatrooms.index(room)

		# add new user
		print "User Conn %s\n\n" %(client_conn)
		if client_conn in self.users_conns:
			print "Client Conn Exists"
			join_id = self.users_conns.index(client_conn)
			self.users_corresponding_group[join_id].append(ref)
		elif user in self.users_name:
			print "Client Name exists"
			join_id = self.users_name.index(user)
			self.users_corresponding_group[join_id].append(ref)
			self.users_conns[join_id] = client_conn

		else:
			join_id = len(self.users_conns)
			self.users_name.append(user)
			self.users_corresponding_group.append([])
			self.users_corresponding_group[join_id].append(ref)
			self.users_conns.append(client_conn)
			print "Add new user %s with join id %d" % (user,join_id)

		return (ref,join_id)

	def broadcast_within_room(self,message,room):

		room = int(room)
		print "Room: ", room, "\n"

		for i, c in enumerate(self.users_conns):

			print "JOIN ID: ", i 
			print "Client:", self.users_name[i]
			print self.users_corresponding_group[i],"\n"

			for r in self.users_corresponding_group[i]:
				if r == room:
					print "Sending:\n%s" %(message)
					c.send(message)
					break

	def is_chatroom_exist(self,room_name):

		if room_name in self.chatrooms:
			return True
		else:
			return False

	def leave_chatroom(self,client_id, room):
		
		client_id = int(client_id)
		self.users_corresponding_group[client_id].remove(int(room))

	def get_ip_address(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("8.8.8.8", 80))
		return s.getsockname()[0]

	def kill(self):
		for c in self.users_conns:
			c.send("Killing the service!")
			c.close()
	

	












