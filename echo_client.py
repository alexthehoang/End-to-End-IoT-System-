import socket

def main():
    running = True
    while running:
        try:
            serverIp = input("Enter server IP address: ")
            serverPort = int(input("Enter server port number: "))
            # Creates a TCP socket
            myTCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Connects to the server
            myTCPSocket.connect((serverIp, serverPort))
            running = False  # Exit loop if inputs are valid
        except ValueError:
            print("Invalid port number. Please enter a numeric value for the port.")
        except Exception as e:
            myTCPSocket.close()
            print(f"An error occurred. Please input a valid server IP and port number. {e}")
    #myTCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #myTCPSocket.connect((serverIp, serverPort))
    print("Connected to server.")

    valid_queries = [
        "What is the average moisture inside my kitchen fridge in the past three hours?",
        "What is the average water consumption per cycle in my smart dishwasher?",
        "Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?"
    ]
    connection = True
    while connection:
        message = input("Enter message to send to the server (type 'quit' to exit): ")
        if message.lower() == 'quit':
            print("Closing connection.")
            break  # Exit loop if user wants to quit

        if message in valid_queries:
            try:
                #Sends the message to the server
                myTCPSocket.send(bytearray(str(message), encoding='utf-8'))
                # response from server
                receivedData = myTCPSocket.recv(1024)
                if not receivedData:
                    print("Server closed the connection.")
                    break
                print(f"Data recieved from the server: {receivedData.decode('utf-8')}")
            except Exception as e:
                print(f"An error occurred while communicating with the server: {e}")
                break
        else:
            print("Sorry, this query cannot be processed. Please try one of the following:")
            for query in valid_queries:
                print(f"- {query}")

        

    myTCPSocket.close()
        
if __name__ == "__main__":
    main()