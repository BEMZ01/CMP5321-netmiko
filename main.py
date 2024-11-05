import os
import netmiko
import logging
from dotenv import load_dotenv

# https://www.cisco.com/c/en/us/support/docs/ip/access-lists/13608-21.html

# cisco cisco123!

# Load environment variables from .env file
load_dotenv()

class DeviceManager:
    def __init__(self):
        self.__devices = []
        self.logger = logging.getLogger('DeviceManager')

    def __iter__(self):
        return iter(self.__devices)

    def add_device(self, host, username, password, device_type, hostname, port=22, secret=None):
        self.__devices.append(NetworkDevice(len(self.__devices), host, username, password, device_type, hostname, port, secret))
        # return the id of the device
        return len(self.__devices) - 1

    def remove_device(self, id):
        # disconnect from device, then replace with None (to preserve the id)
        self.__devices[id].disconnect()
        self.__devices[id] = None

    def get_device(self, id):
        return self.__devices[id]


class NetworkDevice:
    def __init__(self, ID, host, username, password, device_type, hostname, port=22, secret=None):
        self.net_connect = None
        self.expect_string = None
        self.host = host
        self.hostname = hostname
        self.username = username
        self.password = password
        self.device_type = device_type
        self.port = port
        self.secret = secret
        self.id = ID
        self.logger = logging.getLogger(f'NetworkDevice#{ID}')
        try:
            self.connect()
        except netmiko.NetMikoAuthenticationException as e:
            self.logger.error(f"Authentication failed\n{e}")
            raise Exception("AuthenticationException")
        except netmiko.NetMikoTimeoutException as e:
            self.logger.error(f"Timeout error\n{e}")
            raise Exception("TimeoutException")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred. {e}")

    def connect(self, force=False):
        if self.net_connect is not None and not force:
            return
        else:
            self.net_connect = netmiko.ConnectHandler(
                host=self.host,
                username=self.username,
                password=self.password,
                device_type=self.device_type,
                port=self.port,
                secret=self.secret
            )
            self.logger.info(f"Connected to {self.host}")

    def __send_command(self, command):
        self.logger.debug(f"sending command: {command}, expect_string: {self.net_connect.find_prompt()}")
        if self.net_connect is None:
            self.connect()
        if "hostname" in command:
            return self.net_connect.send_command(command, expect_string=self.hostname)
        return self.net_connect.send_command(command)

    def save_config(self):
        if self.net_connect is None:
            self.connect()
        return self.__send_command("copy run start")

    def fallback_config(self):
        if self.net_connect is None:
            self.connect()
        # revert to the saved config
        self.__send_command("copy start run")

    def disconnect(self):
        if self.net_connect is not None:
            self.net_connect.disconnect()
            self.net_connect = None

    def modify_hostname(self, new_hostname):
        if self.net_connect is None:
            self.connect()
        self.logger.info(f"Modifying hostname to {new_hostname}")
        # set expected string to the current hostname
        self.__send_command("en")
        self.__send_command("conf t")
        self.__send_command(f"hostname {new_hostname}")
        self.hostname = new_hostname

    def get_config(self):
        if self.net_connect is None:
            self.connect()
        return self.__send_command("show run")

    def send_command(self, command):
        if self.net_connect is None:
            self.connect()
        return self.__send_command(command)

def create_devices():
    """
    Create a list of devices from environment variables, pack into a device manager and return
    :return: DeviceManager
    """
    deviceManager = DeviceManager()
    USERNAMES = os.getenv('USERNAMES').split(',')
    PASSWORDS = os.getenv('PASSWORDS').split(',')
    HOSTS = os.getenv('HOSTS').split(',')
    HOSTNAME = os.getenv('HOSTNAME').split(',')
    DEVICE_TYPES = os.getenv('DEVICE_TYPES').split(',')
    if len(USERNAMES) != len(PASSWORDS) or len(USERNAMES) != len(HOSTS) or len(USERNAMES) != len(DEVICE_TYPES):
        raise Exception("Invalid environment variables")
    logger.info(f"Creating {len(USERNAMES)} devices")
    for i in range(len(USERNAMES)):
        if ":" in HOSTS[i]:
            host, port = HOSTS[i].split(":")
            deviceManager.add_device(host, USERNAMES[i], PASSWORDS[i], DEVICE_TYPES[i], HOSTNAME[i], int(port))
        else:
            deviceManager.add_device(HOSTS[i], USERNAMES[i], PASSWORDS[i], DEVICE_TYPES[i], HOSTNAME[i])
    return deviceManager


if __name__ == "__main__":
    # Set up netmiko's built-in logging
    netmiko_logger = logging.getLogger('netmiko')
    netmiko_logger.setLevel(logging.DEBUG)  # or INFO
    #netmiko_logger.propagate = False

    # Set up the main logger
    logger = logging.getLogger('main')
    logger.setLevel(logging.DEBUG)  # Set logger level
    #logger.propagate = False

    # Create a FileHandler for logging to a file
    file_handler = logging.FileHandler('debug.log')
    file_handler.setLevel(logging.DEBUG)  # Set handler level

    # Create a StreamHandler for logging to STDOUT
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)  # Set handler level

    # Create a Formatter for log messages
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Set the Formatter for the handlers
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    # Add the handlers to the discord logger
    netmiko_logger.addHandler(file_handler)
    netmiko_logger.addHandler(stream_handler)

    # Create a DeviceManager object
    deviceManager = create_devices()

    # device 0 is ssh
    # device 1 is telnet

    # device 0
    device = deviceManager.get_device(0)
    print("Device 0")
    # modify the hostname
    device.modify_hostname("SSH-CISCO")
    device.save_config()
    #write the current config to a file
    with open("config_0.txt", "w") as f:
        f.write(device.get_config())
    # disconnect
    deviceManager.remove_device(0)

    # device 1
    device = deviceManager.get_device(1)
    print("Device 1")
    # modify the hostname
    device.modify_hostname("TELNET-CISCO")
    device.save_config()
    #write the current config to a file
    with open("config_1.txt", "w") as f:
        f.write(device.get_config())