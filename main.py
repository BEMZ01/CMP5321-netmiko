import os
import netmiko
import logging
from dotenv import load_dotenv

# cisco cisco123!

class NetworkDevice:
    def __init__(self, host, username, password, device_type, port=22, secret=None):
        self.net_connect = None
        self.host = host
        self.username = username
        self.password = password
        self.device_type = device_type
        self.port = port
        self.secret = secret
        try:
            self.connect()
        except netmiko.NetMikoAuthenticationException:
            print("Authentication failed")
        except netmiko.NetMikoTimeoutException:
            print("Timeout error")
        except Exception as e:
            print(f"An unexpected error occurred. {e}")

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

    def disconnect(self):
        if self.net_connect is not None:
            self.net_connect.disconnect()
            self.net_connect = None

    def modify_hostname(self, new_hostname):
        if self.net_connect is None:
            self.connect()
        return self.net_connect.send_config_set([f"hostname {new_hostname}"])

    def send_command(self, command):
        if self.net_connect is None:
            self.connect()
        return self.net_connect.send_command(command)

def main():
    # Create a device object
    device = NetworkDevice(
        host=int(os.getenv("HOST").split(":")[0]),
        username=os.getenv("USERNAME"),
        password=os.getenv("PASSWORD"),
        port=int(os.getenv("HOST").split(":")[1]),
        device_type="cisco_ios"
    )



if __name__ == "__main__":
    # Set up netmiko's built-in logging
    netmiko_logger = logging.getLogger('netmiko')
    netmiko_logger.setLevel(logging.DEBUG)  # or INFO
    netmiko_logger.propagate = False

    # Set up the main logger
    logger = logging.getLogger('main')
    logger.setLevel(logging.DEBUG)  # Set logger level
    logger.propagate = False

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

    # Load environment variables from .env file
    load_dotenv()

    main()
