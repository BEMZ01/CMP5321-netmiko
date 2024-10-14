import pexpect

cisco_ssh = {
    "host": "10.10.1.115",
    "username": "cisco",
    "password": "cisco123!",
    "port": 22
}

cisco_telnet = {
    "host": "10.10.1.115",
    "username": "cisco",
    "password": "cisco123!",
    "port": 23
}

def send_cmd(session, cmd, expect):
    session.sendline(cmd)
    session.expect(expect)
    return session.before

def main():
    # SSH
    print("SSH")
    ssh_session = pexpect.spawn(f"ssh {cisco_ssh['username']}@{cisco_ssh['host']} -p {cisco_ssh['port']}")
    ssh_session.expect("Password:")
    ssh_session.sendline(cisco_ssh["password"])
    ssh_session.expect("#")
    send_cmd(ssh_session, "terminal length 0", "#") # disable pagination
    send_cmd(ssh_session, "enable", "#")
    send_cmd(ssh_session, "conf t", "#")
    send_cmd(ssh_session, "hostname SSH-CISCO", "#")
    send_cmd(ssh_session, "end", "#")
    send_cmd(ssh_session, "wr", "#")
    # write the current config to a file
    with open("config_ssh.txt", "w") as f:
        f.write(str(send_cmd(ssh_session, "show run", "#"), "utf-8"))
    ssh_session.close()

    # Telnet
    print("Telnet")
    telnet_session = pexpect.spawn(f"telnet {cisco_telnet['host']} {cisco_telnet['port']}")
    telnet_session.expect("Username:")
    telnet_session.sendline(cisco_telnet["username"])
    telnet_session.expect("Password:")
    telnet_session.sendline(cisco_telnet["password"])
    telnet_session.expect("#")
    send_cmd(telnet_session, "terminal length 0", "#") # disable pagination
    send_cmd(telnet_session, "enable", "#")
    send_cmd(telnet_session, "conf t", "#")
    send_cmd(telnet_session, "hostname TELNET-CISCO", "#")
    send_cmd(telnet_session, "end", "#")
    send_cmd(telnet_session, "wr", "#")
    with open("config_telnet.txt", "w") as f:
        f.write(str(send_cmd(telnet_session, "show run", "#"), "utf-8"))
    telnet_session.close()
    print("Done")

if __name__ == "__main__":
    main()
