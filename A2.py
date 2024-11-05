import pexpect
import difflib

class CSR1KV:
    def __init__(self, host, user, password, port=22, disable_paging=True):
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        print(f"Attemping to connect to {self.host}...")
        self.session = pexpect.spawn(f"ssh {self.user}@{self.host} -p {self.port}")
        try:
            self.session.expect("Password:", timeout=5)
        except pexpect.exceptions.EOF:
            print(str(self.session.before, "utf-8"))
            raise Exception("Connection failed")
        except pexpect.exceptions.TIMEOUT:
            print(str(self.session.before, "utf-8"))
            raise Exception("Connection timeout")
        self.session.sendline(self.password)
        self.session.expect("#")
        print(f"Connected to {self.host}! Now pulling information...")
        self.hostname = self.send_cmd("show run | i hostname", "#", ignore_hostname=True).split()[1]
        print(f"Found hostname: {self.hostname}")
        if disable_paging:
            self.send_cmd("terminal length 0", "#")
            print("Disabled pagination")
        print("Ready!")

    def is_connected(self):
        return not self.session.closed

    def is_logged_in(self):
        return self.is_connected() and (self.session.after == b"#" or self.session.after == b">")

    def is_in_privileged_mode(self):
        return self.is_logged_in() and self.session.after == b"#"

    def toggle_privileged_mode(self):
        if self.is_in_privileged_mode():
            self.session.sendline("exit")
            self.session.expect(">")
        else:
            self.session.sendline("enable")
            self.session.expect("#")

    def get_config(self, type: str):
        if not self.is_logged_in():
            raise Exception("Not logged in")
        if type == "running":
            return self.send_cmd("show run", "#")
        elif type == "startup":
            return self.send_cmd("show start", "#")
        else:
            raise Exception("Invalid config type")

    def compare_config(self, type: str, other_config: str):
        if not self.is_logged_in():
            raise Exception("Not logged in")
        local_config = self.get_config(type)
        diff = difflib.unified_diff(local_config.splitlines(), other_config.splitlines(), lineterm="")
        return "\n".join(diff)

    def send_cmd(self, cmd, expect, ignore_hostname=False):
        if not self.is_logged_in():
            raise Exception("Not logged in")
        self.session.sendline(cmd)
        self.session.expect(expect)
        if ignore_hostname:
            return str(self.session.before, "utf-8").replace(cmd, "").strip()
        else:
            return str(self.session.before, "utf-8").replace(cmd, "").replace(self.hostname, "").strip()

if __name__ == "__main__":
    csr = CSR1KV("10.10.1.115", "cisco", "cisco123!")
    if csr.is_logged_in():
        print("Comparing running config with startup config...")
        startup_config = csr.get_config("startup")
        print(csr.compare_config("running", startup_config))
        print("Comparing running config with a local config...")
        with open("config_ssh.txt", "r") as f:
            print(csr.compare_config("running", f.read()))


