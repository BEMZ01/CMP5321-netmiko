import netmiko

class NetworkDevice:
    def __init__(self, host, username, password, device_type, port=22, secret=None):
        self.host = host
        self.username = username
        self.password = password
        self.device_type = device_type
        self.port = port
        self.secret = secret

    def connect(self):
        self.net_connect = netmiko.ConnectHandler(
            host=self.host,
            username=self.username,
            password=self.password,
            device_type=self.device_type,
            port=self.port,
            secret=self.secret
        )

    def disconnect(self):
        self.net_connect.disconnect()

    def modify_hostname(self, new_hostname):
        self.net_connect.send_command(f"hostname {new_hostname}")

    def save_running_config(self, filename):
        output = self.net_connect.send_command("show run")
        with open(filename, "w") as f:
            f.write(output)

def main():
    # Create a device object
    device = NetworkDevice(
        host="192.168.1.1",
        username="username",
        password="password",
        device_type="cisco_ios"
    )

    # Connect to the device
    device.connect()

    # Modify the hostname
    device.modify_hostname("new_hostname")

    # Save the running configuration
    device.save_running_config("running_config.txt")

    # Disconnect from the device
    device.disconnect()

if __name__ == "__main__":
    main()
