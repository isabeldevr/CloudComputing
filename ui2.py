import streamlit as st
import json
from azure.iot.device import IoTHubDeviceClient, Message, exceptions as iot_exceptions
from azure.iot.hub import IoTHubRegistryManager
from datetime import datetime
import time

# Define Azure IoT Hub connection string
CONNECTION_STRING = "HostName=WaterValves.azure-devices.net;SharedAccessKeyName=service;SharedAccessKey=your_shared_access_key"

# Define password for admin access
ADMIN_PASSWORD = "cloud"

# Define all connections for valves
device_connection_devices = [
    "Valve 1",
    "Valve 2",
    "Valve 3",
    "Valve 4"
]

# Initialize status dictionary
valve_status = {}

# Function to connect to Azure IoT Hub
def connect_to_hub(device_id):
    return IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)


# Function to send a message to Azure IoT Hub
def send_message_and_disconnect(device_id, json_payload):
    try:
        client = connect_to_hub(device_id)
        client.connect()

        # Include the device ID in the message payload
        json_payload["DeviceId"] = device_id
        message = Message(json.dumps(json_payload))
        
        # Send the message
        client.send_message(message)
        client.disconnect()

    except iot_exceptions.ConnectionFailedError as e:
        print(f"Error connecting to IoT Hub: {e}")
    except Exception as e:
        print(f" ")

# Function to open a valve
def open_valve(device_id):
    try:
        json_payload = {"ValveStatus": 1}
        send_message_and_disconnect(device_id, json_payload)
        valve_status[device_id] = "Open"
    except iot_exceptions.ConnectionFailedError as e:
        print(f"Error connecting to IoT Hub: {e}")
    except Exception as e:
        print(f" ")


# Function to close a valve
def close_valve(device_id):
    try:
        json_payload = {"ValveStatus": 0}
        send_message_and_disconnect(device_id, json_payload)
        valve_status[device_id] = "Closed"
    except iot_exceptions.ConnectionFailedError as e:
        print(f"Error connecting to IoT Hub: {e}")
    except Exception as e:
        print(f" ")

# Function to read valve status from file (for user view)
def read_valve_status_for_ui():
    try:
        with open("valve_status.json", "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {device_id: {"ValveStatus": 0} for device_id in device_connection_devices}
    return data

# Function to write valve status to file (for user view)
def write_valve_status_for_ui(data):
    with open("valve_status.json", "w") as file:
        json.dump(data, file)

# Function to print valve status in terminal
def print_valve_status_in_terminal():
    print("Valve Status:")
    for device_id, status in valve_status.items():
        print(f"Valve {device_id}: {status}")

# Function for admin login
def admin_login():
    password = st.text_input("Enter admin password:", type="password")
    return password

# Function for admin actions
def admin_actions():
    st.subheader("Admin Actions")
    for device_id in device_connection_devices:
        if st.button(f"Open {device_id}"):
            open_valve(device_id)
        if st.button(f"Close {device_id}"):
            close_valve(device_id)
    sleep_duration = st.number_input("Enter sleep duration (in seconds):", min_value=0, step=1, value=5)
    st.button("Sleep", on_click=sleep_function, args=(sleep_duration,))
    print_valve_status_in_terminal()  # Print valve status in the terminal

# Function for user actions
def user_actions():
    st.subheader("User Actions")
    data = read_valve_status_for_ui()
    for device_id in device_connection_devices:
        st.write(f"{device_id} status: {data[device_id]['ValveStatus']}")
    print_valve_status_in_terminal()  # Print valve status in the terminal

# Function for sleep action
def sleep_function(sleep_duration):
    st.write(f"Sleeping for {sleep_duration} seconds...")
    time.sleep(sleep_duration)
    st.write("Wake up!")
    print_valve_status_in_terminal()  # Print valve status in the terminal

# Streamlit app
st.title("Water Treatment Plant Simulation")

# Check if the script is executed
if __name__ == "__main__":
    role = st.radio("Choose your role:", ("User", "Admin"))
    
    if role == "Admin":
        password = admin_login()
        if password == ADMIN_PASSWORD:
            admin_actions()
        elif password:
            st.warning("Incorrect password. Please try again.")

    elif role == "User":
        user_actions()
