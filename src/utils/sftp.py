import os
import pysftp
import configparser

def read_sftp_config(config_file='sftp.config'):
    """Read SFTP configuration from a config file."""
    config = configparser.ConfigParser()
    config.read(config_file)

    sftp_host = config['SFTP']['host']
    sftp_username = config['SFTP']['username']
    sftp_password = config['SFTP']['password']
    remote_path = config['SFTP']['remote_path']
    local_path = config['SFTP']['local_path']

    return sftp_host, sftp_username, sftp_password, remote_path, local_path

def download_logs_from_sftp(sftp_host, sftp_username, sftp_password, remote_path, local_path):
    """Download log files from an SFTP server."""
    with pysftp.Connection(host=sftp_host, username=sftp_username, password=sftp_password) as sftp:
        print("Connected to SFTP server.")
        if not os.path.exists(local_path):
            os.makedirs(local_path)
        sftp.cwd(remote_path)
        for file in sftp.listdir():
            if file.startswith("Inbound_") and file.endswith(".log"):
                print(f"Downloading {file}...")
                sftp.get(file, os.path.join(local_path, file))
        print("All log files downloaded.")