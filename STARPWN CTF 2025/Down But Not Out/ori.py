import socket
import struct
import os

def display_banner():
    os.system('clear')
    banner = """
             ________________________________________________
            /                                                \\
           |    _________________________________________     |
           |   |                                         |    |
           |   |  #:~ satellite_conn                     |    |
           |   |      [*]Status: Connect                 |    |
           |   |      [-] Enter Command:                 |    |
           |   |                                         |    |
           |   |                                         |    |
           |   |                                         |    |
           |   |                                         |    |
           |   |                                         |    |
           |   |                                         |    |
           |   |                                         |    |
           |   |                                         |    |
           |   |                                         |    |
           |   |_________________________________________|    |
           |                                                  |
            \\________________________________________________/
                   \\___________________________________/
                ___________________________________________
             _-'    .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.  --- `-_
          _-'.-.-. .---.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.--.  .-.-.`-_
       _-'.-.-.-. .---.-.-.-. .---.-.-.-.-.-.-.-.-.-.-`__`. .-.-.-.`-_
    _-'.-.-.-.-. .---.-.-.-. .---.-.-.-.-.-.-.-.-.-.-.-.-.---.  .-.-.-.`-_
 _-'.-.-.-.-.-. .---.-.-.-. .---.-.-.-.-.-.-.-.-.-.-.-.-.-.-.`---'.-.-.-.-.`-_
:-----------------------------------------------------------------------------:
`---._.-----------------------------------------------------------------._.---'
    """
    print(banner)

# Example usage:
display_banner()


def create_ccsds_packet(auth_key, apid, command):
    version = 0b000  # Version number (3 bits)
    packet_type = 1  # Command packet (1 bit)
    sec_header_flag = 1  # Secondary header present (1 bit)
    id = apid # Example APID (11 bits)

    data = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' # Secondary Header Padding for Timing Data
    data += bytes(auth_key,'utf-8')
    data_length = len(data)  # Data length; ensure this is correctly used

    # Create packet ID with correct bit shifts
    packet_id = (version << 13) | (packet_type << 12) | (sec_header_flag << 11) | id

    sequence_flags = 0b00  # Example sequence flags (2 bits)
    sequence_count = 1  # Example sequence count (14 bits)

    primary_header = struct.pack('>HHH', packet_id, (sequence_flags << 14) | sequence_count, data_length - 1)

    return primary_header + data + command.encode()


def process_packet(data):
    if len(data) < 7:
        return False, "Packet too short to be valid"
    tlm_data = data[6:]
    print("[<] Response Data:", tlm_data.decode())


def execute_command(command, *args):
    """
    Execute the given command with optional arguments.

    :param command: str, the command to execute.
    :param args: list, additional arguments for the command.
    """
    commands = {
        'help': print_help,
        'set_authentication_key': set_authentication_key,
        'get_status': get_status,
        'ping': ping,
        'adcs_get_orient': adcs_get_orient,
        'adcs_set_orient': adcs_set_orient,
        'imu_get_mag': imu_get_mag,
        'imu_get_gyro': imu_get_gyro,
        'imu_get_accl': imu_get_accl,
        'imu_calibrate': imu_calibrate,
        'eps_get_voltages': eps_get_voltages,
        'eps_get_panel_voltage': eps_get_panel_voltage,
        'eps_get_panel_current': eps_get_panel_current,
        'eps_get_battery_state': eps_get_battery_state,
        'eps_list_channels': eps_list_channels,
        'eps_enable_channel': eps_enable_channel,
        'eps_disable_channel': eps_disable_channel,
        'exit': exit_client
    }
    
    if command in commands:
        commands[command](*args)
    else:
        print("Invalid command. Type 'help' to see the list of valid commands.")

def print_help():
    list_commands()

def set_authentication_key(*args):
    global auth_key
    apid = 100
    if not args:
        print("[*] Error: No authentication key provided. Please provide an authentication key.\n[#] Example: set_authentication_key <value>")
        return  
    auth_key = args[0]  
    print(f"[*] Authentication Key Set: {auth_key}")
    cmd = ""  
    send_packet(auth_key, apid, cmd)

def get_status():
    apid = 100
    cmd = str("get_status")
    send_packet(auth_key, apid, cmd)
    #pass 

def ping():
    apid = 100
    cmd = str("ping")
    send_packet(auth_key, apid, cmd)

def adcs_get_orient():
    apid = 103
    cmd = str("adcs_get_orient")
    send_packet(auth_key, apid, cmd)

def adcs_set_orient(*args):
    apid = 103
    if not len(args) == 4:
        print("[*] Error: Not Enough Arguments Provided.\n[#] Example: adcs_set_orient <mode> <x> <y> <z>")
        return
    cmd = str("adcs_set_orient " + args[0] + " " + args[1] + " " + args[2] + " " + args[3])
    send_packet(auth_key, apid, cmd)

def imu_get_mag():
    apid = 101
    cmd = str("imu_get_mag")
    send_packet(auth_key, apid, cmd)

def imu_get_gyro():
    apid = 101
    cmd = str("imu_get_gyro")
    send_packet(auth_key, apid, cmd)

def imu_get_accl():
    apid = 101
    cmd = str("imu_get_accl")
    send_packet(auth_key, apid, cmd)

def imu_calibrate():
    apid = 101
    cmd = str("imu_calibrate")
    send_packet(auth_key, apid, cmd)

def eps_get_voltages():
    apid = 102
    cmd = str("eps_get_voltages")
    send_packet(auth_key, apid, cmd)

def eps_get_panel_voltage():
    apid = 102
    cmd = str("eps_get_panel_voltage")
    send_packet(auth_key, apid, cmd)

def eps_get_panel_current():
    apid = 102
    cmd = str("eps_get_panel_current")
    send_packet(auth_key, apid, cmd)

def eps_get_battery_state():
    apid = 102
    cmd = str("eps_get_battery_state")
    send_packet(auth_key, apid, cmd)

def eps_list_channels():
    apid = 102
    cmd = str("eps_list_channels")
    send_packet(auth_key, apid, cmd)

def eps_enable_channel(*args):
    apid = 102
    cmd = str("eps_enable_channel " + args[0])
    send_packet(auth_key, apid, cmd)

def eps_disable_channel(*args):
    apid =102
    cmd = str("eps_disable_channel " + args[0])
    send_packet(auth_key, apid, cmd)

def exit_client():
    exit()    

def list_commands():
    print("""
Available Commands:
- help: Print help menu
- set_authentication_key: Set the authentication key to be used in the CCSDS packets
- get_status: Get all status of all subsystems
- ping: Test connection to satellite
- adcs_get_orient: Get current orientation in degrees (Euler angles)
- adcs_set_orient: Set new orientation using ADCS modes (command mode int(x) int(y) int(z))
  Modes: 
    - rcw: Reaction Control Wheels
    - mag: Magnetorquers       
- imu_get_mag: Read magnetometer
- imu_get_gyro: Read gyroscope
- imu_get_accl: Read accelerometer
- imu_calibrate: Calibrate IMU
- eps_get_voltages: Get voltages of all EPS channels
- eps_get_panel_voltage: Get voltages of panels
- eps_get_panel_current: Get current of panels
- eps_get_battery_state: See if battery is charging and percentage of battery remaining
- eps_list_channels: List EPS channels
- eps_enable_channel: Enable EPS power channel (command int(Channel Number))
- eps_disable_channel: Disable EPS power channel (command int(Channel Number))
    """)

auth_key = ''

def send_packet(auth_key, apid, cmd):
    host = '34.205.255.133'  # Target host
    port = 41057        # Target port
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        try:
            # Set a timeout for blocking socket operations
            sock.settimeout(1.0)

            # Create a packet based on the command and authorization key
            packet = create_ccsds_packet(auth_key, apid, cmd)

            # Send the packet to the specified host and port
            sock.sendto(packet, (host, port))

            # Prepare to receive multiple responses until the timeout is reached
            while True:
                try:
                    # Attempt to receive a response within the timeout period
                    response = sock.recv(1024)
                    process_packet(response)
                except socket.timeout:
                    break
                except Exception as e:
                    # Handle any other exceptions
                    print(f"An error occurred: {e}")
                    break
        except Exception as e:
            print(f"An error occurred while sending the packet: {e}")


if __name__ == '__main__':
    while True:
        cmd = input("Command to Issue: ")
        cmd_parts = cmd.split()  # Split the input by spaces

        if cmd_parts:  # Check if there is at least one element from the split
            cmd = cmd_parts[0]  # The command is the first element
            args = cmd_parts[1:]  # All other elements are considered arguments
            execute_command(cmd, *args)
    