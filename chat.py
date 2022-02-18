# Christian Battista Giannarelli, cibigi.github.io
# Released under GNU GPL v3
# Hybrid Chat

import socket
from threading import Thread
import errno

# Opening log file
file = open("connections.txt", "a")

# Connections list
connections = []


# AS SERVER - New connection operations thread (creating log, listening, forwarding to every client)
def new_connection(connection, address):
	with connection:
		print("New connection: ", address)
		file.write(str(address))
		file.flush()

		while True:
			data = connection.recv(1024)

			# Data is corrupted, kills thread
			if not data:
				break

			print(address, data.decode())
			send_to_clients(data)


# AS SERVER - Connection class, starts new_connection thread
class Connection:
	def __init__(self, connection, address):
		self.connection = connection
		self.address = address
		self.thread = Thread(target = new_connection, args = (self.connection, self.address,))
		self.thread.start()


# AS CLIENT - Receiving data, thread
def receive_as_client():
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as my_socket:
		my_socket.connect((server_address, int(port)))
		
		while True:
			data= my_socket.recv(1024)
			print(data.decode())


# Sending data, thread
def send_as_client():
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as my_socket:
		my_socket.connect((server_address, int(port)))

		while True:
			text = input()
			my_socket.sendall(bytes(username + " : " + text, encoding = "utf8"))


# AS SERVER - Forwarding received data to every client (called in new_connection threads)
def send_to_clients(data):
	for connected in connections:
		connected.connection.sendall(data)


# Welcome guide
print("Welcome!\na) Type \"localhost\" and your chosen port to operate as server-client hybrid.\nb) Type the server IP address and the port it uses to operate as client-only.")

# Server IP address selection
server_address = input("Server IP address: ")

# Port selection
port = input("Port: ")

# Username selection
username = input("Username: ")

# Sending operations (server-client hybrid and client-only)
send_as_client_thread = Thread(target = send_as_client)
send_as_client_thread.start()


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as my_socket:
	# OPERATING AS SERVER-CLIENT HYBRID (unused port)
	try:
		my_socket.bind((server_address, int(port)))
		my_socket.listen()

		# New username
		username = username + " SERVER"

		print("Server started!\nYour new username is: " + username + "!\nType some text and press enter to send as " + username + ".")

		# Accepting new connections, creating new Connection objects
		while True:
			connection, address = my_socket.accept()
			connected = Connection(connection, address)
			connections.append(connected)

	# OPERATING AS CLIENT-ONLY (port already in use)
	except socket.error as e:
		if e.errno == errno.EADDRINUSE:
			print("Port is already in use. Client-only mode starting...\nType some text and press enter to send ('q' to quit).")
			
			receive_as_client_thread = Thread(target = receive_as_client)
			receive_as_client_thread.start()

			while True:
				pass
		else:
			print(e)