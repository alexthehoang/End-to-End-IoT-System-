import socket
import pymongo
from datetime import datetime, timedelta
import pytz
from config import MONGO_URI


def main():
    running = True
    while running:
        try:
            serverIp = input("Enter server IP address to bind (e.g., 0.0.0.0): ")
            serverPort = int(input("Enter server port number: "))
            serverIp = "0.0.0.0"
            serverPort = 14432
            running = False  # Exit loop if inputs are valid
        except ValueError:
            print("Invalid port number. Please enter a numeric value for the port.")
        except Exception as e:
            print(f"An error occurred: {e}")

    # Connect to MongoDB
    try:
        mongo_client = pymongo.MongoClient(MONGO_URI)
        db = mongo_client['test']  # Replace with your database name
        metadata_collection = db['thetable123_metadata']  # Metadata collection
        data_collection = db['thetable123_virtual']  # Replace with your data collection name
        print("Connected to MongoDB.")
    except Exception as e:
        print(f"Could not connect to MongoDB: {e}")
        return

    # Retrieve and cache metadata
    try:
        metadata = fetch_metadata(metadata_collection)
        print("Metadata fetched successfully.")
    except Exception as e:
        print(f"Error fetching metadata: {e}")
        return

    # Create a TCP socket
    myTCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Bind the socket to the given IP and port
        myTCPSocket.bind((serverIp, serverPort))
    except Exception as e:
        print(f"An error occurred while binding the socket: {e}")
        myTCPSocket.close()
        return

    # Listen for connections
    myTCPSocket.listen(5)
    print(f"Server is now listening on {serverIp} on port {serverPort}")

    while True:
        incomingSocket, incomingAddress = myTCPSocket.accept()
        print(f"Connected with {incomingAddress}")
        while True:
            try:
                # Receive data from the client
                receivedData = incomingSocket.recv(4096)
                if not receivedData:
                    print("The client has disconnected")
                    break
                # Decode the received data
                query = receivedData.decode('utf-8')
                print(f"Received query: {query}")

                # Process the query
                if query == "What is the average moisture inside my kitchen fridge in the past three hours?":
                    result = process_moisture_query(data_collection, metadata)
                elif query == "What is the average water consumption per cycle in my smart dishwasher?":
                    result = process_water_consumption_query(data_collection, metadata)
                elif query == "Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?":
                    result = process_electricity_consumption_query(data_collection, metadata)
                else:
                    result = "Invalid query received."

                # Send the result back to the client
                incomingSocket.sendall(result.encode('utf-8'))

            except Exception as e:
                print(f"An error occurred while processing the query: {e}")
                incomingSocket.sendall(f"An error occurred: {e}".encode('utf-8'))
                break

        incomingSocket.close()

    myTCPSocket.close()

def fetch_metadata(metadata_collection):
    """
    Fetches metadata from the metadata collection and structures it into a usable format.
    Returns a dictionary with device, board, and sensor information.
    """
    metadata = {}
    cursor = metadata_collection.find({"customAttributes.type": "DEVICE"})
    for device in cursor:
        device_id = device['assetUid']
        device_name = device['customAttributes']['name']
        device_info = {
            'device_id': device_id,
            'device_name': device_name,
            'boards': {}
        }

        # Iterate through boards
        for board in device['customAttributes'].get('children', []):
            board_id = board['assetUid']
            board_name = board['customAttributes']['name']
            board_info = {
                'board_id': board_id,
                'board_name': board_name,
                'sensors': {}
            }

            #Iterat through sensors
            for sensor in board['customAttributes'].get('children', []):
                sensor_id = sensor['assetUid']
                sensor_name = sensor['customAttributes']['name']
                sensor_info = {
                    'sensor_id': sensor_id,
                    'sensor_name': sensor_name,
                    'unit': sensor['customAttributes'].get('unit'),
                    'min_value': sensor['customAttributes'].get('minValue'),
                    'max_value': sensor['customAttributes'].get('maxValue'),
                    'desired_min': sensor['customAttributes'].get('desiredMinValue'),
                    'desired_max': sensor['customAttributes'].get('desiredMaxValue')
                }
                board_info['sensors'][sensor_name] = sensor_info

            device_info['boards'][board_name] = board_info

        metadata[device_name] = device_info
        
    for key, value in metadata.items():
        print(f"Device Name: {key}")
        print(f"Metadata: {value}")
        print("\n\n")

    return metadata

def process_moisture_query(data_collection, metadata):
    try:
        # Identify the relevant sensor using metadata
        device_name = "Refrigerator1" 
        device = metadata.get(device_name)
        if not device:
            return f"Metadata for {device_name} not found."

        # Identify the board and sensor
        board = None
        sensor = None
        for b_name, b_info in device['boards'].items():
            for s_name, s_info in b_info['sensors'].items():
                if "Moisture Meter" in s_name:
                    board = b_info
                    sensor = s_info
                    break
            if sensor:
                break

        if not sensor:
            return f"Moisture sensor not found for {device_name}."

        # Get current time in PST
        pst = pytz.timezone('US/Pacific')
        current_time = datetime.now(pst)
        three_hours_ago = current_time - timedelta(hours=3)

        # Convert times to UTC for MongoDB query
        utc = pytz.utc
        current_time_utc = current_time.astimezone(utc)
        three_hours_ago_utc = three_hours_ago.astimezone(utc)

        # Query MongoDB for moisture data from the kitchen fridge in the past three hours
        cursor = data_collection.find({
            "payload.asset_uid": board['board_id'],
            "time": {"$gte": three_hours_ago_utc, "$lte": current_time_utc},
            f"payload.{sensor['sensor_name']}": {"$exists": True}
        })

        moisture_values = []
        for document in cursor:
            moisture_str = document['payload'].get(sensor['sensor_name'])
            if moisture_str:
                moisture_value = float(moisture_str)
                # Convert to Relative Humidity Percentage (RH%)
                rh_percentage = convert_to_rh_percentage(moisture_value)
                moisture_values.append(rh_percentage)

        if moisture_values:
            average_moisture = sum(moisture_values) / len(moisture_values)
            result = f"The average moisture inside your kitchen fridge in the past three hours is {average_moisture:.2f}% RH."
        else:
            result = "No moisture data available for your kitchen fridge in the past three hours."

        return result

    except Exception as e:
        return f"Error processing moisture query: {e}"

def process_water_consumption_query(data_collection, metadata):
    pass

def process_electricity_consumption_query(data_collection, metadata):
    pass


def convert_to_rh_percentage(sensor_value):
    max_sensor_value = 1000  
    rh_percentage = (sensor_value / max_sensor_value) * 100
    return rh_percentage

if __name__ == "__main__":
    main()
