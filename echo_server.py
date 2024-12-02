import socket

def main():
    running = True
    while running:
        try:
            serverIp = input("Enter server IP address: ")
            serverPort = int(input("Enter server port number: "))
            running = False  # Exit loop if inputs are valid
        except Exception as e:
            print(f"An error occurred: {e}")
            
    # creates a TCP socket
    myTCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # binds the socket to the given IP and port
        myTCPSocket.bind((serverIp,serverPort))
    except Exception as e:
        print(f"An error occurred: {e}")
        myTCPSocket.close()
        return
    
    # listen for connections
    myTCPSocket.listen(5)
    print(f"Server is now listening on {serverIp} on port {serverPort}")
    
    incomingSocket, incomingAddress = myTCPSocket.accept()
    print(f"Connected with {incomingAddress}")
    while True:
        # this is the data received from the client
        receivedData = incomingSocket.recv(1024)
        # if there is not data then the client closed the connection
        if not receivedData:
            print("The client has disconnected")
            break
        #decodes the received data
        decodedData = receivedData.decode('utf-8')
        print(f"Data received: {decodedData}" )
        # converts to uppercase 
        upperResponse = decodedData.upper()
        # echoes the uppercase message back to the client
        incomingSocket.send(bytearray(str(upperResponse), encoding='utf-8'))
    incomingSocket.close()
        
if __name__ == "__main__":
    main()   
        