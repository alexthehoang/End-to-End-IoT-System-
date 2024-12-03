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
            running = False  
        except ValueError:
            print("Invalid port number. Please enter a numeric value for the port.")
        except Exception as e:
            myTCPSocket.close()
            print(f"An error occurred. Please input a valid server IP and port number. {e}")
    print("Connected to server.")

    valid_queries = [
        "What is the average moisture inside my kitchen fridge in the past three hours?",
        "What is the average water consumption per cycle in my smart dishwasher?",
        "Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?"
    ]

    connection = True
    while connection:
        print("\nSelect a query to send to the server:")
        for i, query in enumerate(valid_queries, start=1):
            print(f"{i}. {query}")
        print("Type 'quit' to exit.")

        user_input = input("Enter your choice: ")
        if user_input.lower() == 'quit':
            print("Closing connection.")
            break 

        try:
            choice = int(user_input)
            if 1 <= choice <= len(valid_queries):
                message = valid_queries[choice - 1]
                myTCPSocket.send(bytearray(message, encoding='utf-8'))
                # Receives response from the server
                receivedData = myTCPSocket.recv(1024)
                if not receivedData:
                    print("Server closed the connection.")
                    break
                print(f"Data received from the server: {receivedData.decode('utf-8')}")
            else:
                print("Invalid choice. Please select a valid number from the list.")
        except ValueError:
            print("Invalid input. Please enter a number corresponding to your choice.")
        except Exception as e:
            print(f"An error occurred while communicating with the server: {e}")
            break

    myTCPSocket.close()
    
if __name__ == "__main__":
    main()