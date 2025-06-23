import paramiko

import os
import time
import subprocess
import tarfile
from shutil import make_archive
from dotenv import load_dotenv

load_dotenv()

# for ssh access
remote_host = os.getenv("REMOTE_HOST")
remote_port = os.getenv("REMOTE_PORT")
docker_db_port = os.getenv("DB_DOCKER_PORT")
remote_username = os.getenv("REMOTE_USERNAME")
private_key_path = os.getenv("PRIVATE_KEY_PATH")
private_key_passphrase = os.getenv("PRIVATE_KEY_PASSPHRASE")
# for remote DB
remote_db = os.getenv("REMOTE_DB")
# for local DB
local_username = os.getenv("DB_USER")
local_password = os.getenv("DB_PASSWORD")
local_database = os.getenv("DB_NAME")
local_host = os.getenv("DB_HOST")


class Sync_helper:

    def dump(self, local_tables, local_dumpfile):

        print(f"Dumping to {local_dumpfile}")

        os.makedirs(os.path.dirname(local_dumpfile), exist_ok=True)

        # Use subprocess instead of os.system for better error handling

        dumpcmd = [
            "mysqldump",
            "-h",
            local_host,
            "-u",
            local_username,
            f"-p{local_password}",
            "--protocol=TCP",
            f"-P {docker_db_port}",
            local_database,
        ]
        # Add tables if specified
        if local_tables:
            dumpcmd.extend(local_tables.split())

        # Run command and redirect output to file
        with open(local_dumpfile, "w") as outfile:
            result = subprocess.run(dumpcmd, stdout=outfile, stderr=subprocess.PIPE)

        # Check if command was successful
        if result.returncode != 0:
            print(f"Error dumping database: {result.stderr.decode()}")
            return False

        print(f"Dump completed successfully to {local_dumpfile}")
        return True

    def compress(self, path, file, compressed_file):
        print("compressing file")
        compressed_file_base_name = compressed_file.split(".")[0]
        make_archive(
            f"{path}/{compressed_file_base_name}", "gztar", root_dir=path, base_dir=file
        )

    def compress_folders(self, save_folder_base, folders_to_compress, compressed_file):
        print("compressing folder")
        with tarfile.open(f"{save_folder_base}/{compressed_file}", "w:gz") as tar:
            for source_dir in folders_to_compress:
                tar.add(
                    f"{save_folder_base}/{source_dir}",
                    arcname=os.path.basename(source_dir),
                )

    def connect(self):
        private_key = paramiko.RSAKey.from_private_key_file(
            private_key_path, password=private_key_passphrase
        )
        # connect to remote server
        print("connect")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.load_system_host_keys()
        client.connect(
            hostname=remote_host,
            username=remote_username,
            port=remote_port,
            pkey=private_key,
            passphrase=private_key_passphrase,
        )
        return client

    def transfer(self, ssh, local_path, file, remote_path=None):
        # send file to server root
        print("transfering", f"{local_path}/{file}")
        ftp_client = ssh.open_sftp()
        remote_file_path = f"{remote_path}/{file}" if remote_path else file
        ftp_client.put(f"{local_path}/{file}", remote_file_path)
        ftp_client.close()
        print("transfer complete")

    def remote_extract(self, ssh, file, location=None):
        print(f"extract {file} on server")
        extract_cmd = f"tar -xzvf {file}"

        if location:
            extract_cmd += f" -C {location}"
        print(extract_cmd)
        stdin, stdout, stderr = ssh.exec_command(extract_cmd)
        outlines = stdout.readlines()
        resp = "".join(outlines)
        print(resp)

    def remote_import_table(self, ssh, file):
        # import sql to remote
        print("importing table on remote db")
        # import_cmd = f'mysql -u {remote_db_username} -p{remote_db_password} -D {remote_db} -e "\. {file}÷"'
        # login path needs to be set up on the remote server using mysql_config_editor set --login-path=compodio --host=localhost --user=xxxxx --password
        import_cmd = f'mysql --login-path=compodio -D {remote_db} -e "\. {file}"'

        stdin, stdout, stderr = ssh.exec_command(import_cmd)

        outlines = stdout.readlines()
        resp = "".join(outlines)
        print(resp)
        print(stderr.readlines())

        print("import complete")

    def synch_tables(self, local_path, dumpfile, compressed_dumpfile, local_table=""):
        """Handles dumping, compressing, and transferring, extrating and importing a table(s) to the remote server.

        if local_table is not specified, all tables are dumped and synched.

        Args:
            local_path (str): path to location where the dumpfile is stored.
            dumpfile (str): name of the dumpfile to be created.
            compressed_dumpfile (str): name of the compressed dumpfile to be created.
            local_table (str, optional): table to dump and synch. Defaults to ''.
        """

        print("synching: ", local_table)
        self.dump(local_table, f"{local_path}/{dumpfile}")

        self.compress(local_path, dumpfile, compressed_dumpfile)

        ssh = self.connect()

        self.transfer(ssh, local_path, compressed_dumpfile)

        self.remote_extract(ssh, compressed_dumpfile)

        self.remote_import_table(ssh, dumpfile)
