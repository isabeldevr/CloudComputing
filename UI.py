import streamlit as st
import json
from azure.iot.hub import IoTHubRegistryManager
# import the IOT exceptions
from datetime import datetime
import time

# Define Azure IoT Hub connection string

CONNECTION_STRING = "HostName=WaterValves.azure-devices.net;SharedAccessKeyName=iothubowner;SharedAccessKey=6JNFXlM4CgUEDzNxiZMnC3b3oj/WYpya0AIoTPYVrDs="

# Define password for admin access
ADMIN_PASSWORD = "cloud"

# Define all connections for valves
device_connection_devices = [
    "Valve1",
    "Valve2",
    "Valve3",
    "Valve4"
]

# Initialize status dictionary
valve_status = {}


# Function to connect to Azure IoT Hub
def connect_to_hub():
    try:
        # Create an instance of the registry manager
        registry_manager = IoTHubRegistryManager(CONNECTION_STRING)

        # Return the registry manager
        return registry_manager

    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# Function to send a message to Azure IoT Hub
def send_message_and_disconnect(device_id, json_payload):
    client = connect_to_hub()
    print("Sending message to:", device_id)
    # Send the JSON payload to Azure IoT Hub
    client.send_c2d_message(device_id, json.dumps(json_payload))
    print("Message sent:", json_payload)



# Function to open a valve
def open_valve(device_id):
    try:
        json_payload = {"ValveStatus": 1}
        send_message_and_disconnect(device_id, json_payload)
        valve_status[device_id] = "Open"


    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# Function to close a valve
def close_valve(device_id):
    try:
        json_payload = {"ValveStatus": 0}
        send_message_and_disconnect(device_id, json_payload)
        valve_status[device_id] = "Closed"
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


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


# Function for admin login
def admin_login():
    password = st.text_input("Enter admin password:", type="password")
    return password


# Function for admin actions
def admin_actions():
    st.subheader("Admin Actions")
    for device_id in device_connection_devices:
        if st.button(f"Open Valve {device_id}"):
            open_valve(device_id)
        if st.button(f"Close Valve {device_id}"):
            close_valve(device_id)
    sleep_duration = st.number_input("Enter sleep duration (in seconds):", min_value=0, step=1, value=5)
    st.button("Sleep", on_click=sleep_function, args=(sleep_duration,))


# Function for user actions
def user_actions():
    st.subheader("User Actions")
    data = read_valve_status_for_ui()

    # Print keys for debugging
    print("Keys in device_connection_devices:", device_connection_devices)
    print("Keys in data:", list(data.keys()))

    for device_id in device_connection_devices:
        st.write(f"Valve {device_id} status: {data.get(device_id, {}).get('ValveStatus', 'Unknown')}")


# Function for sleep action
def sleep_function(sleep_duration):
    st.write(f"Sleeping for {sleep_duration} seconds...")
    time.sleep(sleep_duration)
    st.write("Wake up!")


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
