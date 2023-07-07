import paramiko
from dotenv import load_dotenv

import os
import sys

load_dotenv()

# for ssh access
remote_host = os.getenv("remote_host")
remote_port = os.getenv("remote_port")
remote_username = os.getenv("remote_username")
private_key_path = os.getenv("private_key_path")
private_key_passphrase = os.getenv("private_key_passphrase")
# for remote DB
remote_db = os.getenv("remote_db")
# for local DB
local_username = os.getenv("local_username")
local_password = os.getenv("local_password")
local_database = os.getenv("local_database")
local_host = os.getenv("local_host")

class Sync_helper():

    def dump(self, local_tables, local_dumpfile):
       
        print('dump')
        
        dumpcmd = f"/usr/local/mysql/bin/mysqldump -h {local_host} -u {local_username} -p{local_password} {local_database} {local_tables} > {local_dumpfile}"

        os.system(dumpcmd)

    def compress(self, path, file, compressed_file):
        print('compressing file')
        compresscmd = f"tar -czvf {path}{compressed_file} -C {path} {file}"
        # compress the files without including the folder


        os.system(compresscmd)

    def compress_folders(self, save_folder_base,folders_to_compress, compressed_file):
        print('compressing folder')
        compresscmd = f"tar -C {save_folder_base} -czvf {compressed_file} {folders_to_compress}"
        os.system(compresscmd)

    def connect(self):
        private_key = paramiko.RSAKey.from_private_key_file(private_key_path, password=private_key_passphrase)
        #connect to remote server
        print('connect')
        client=paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.load_system_host_keys()
        client.connect(hostname=remote_host,username=remote_username,port=remote_port,pkey=private_key, passphrase=private_key_passphrase)
        return client

    def transfer(self, ssh, local_path, file):
        #send file to server root
        print('transfering', f'{local_path}{file}')
        ftp_client=ssh.open_sftp()
        ftp_client.put(f'{local_path}{file}', file)
        ftp_client.close()  
        print('transfer complete') 

    def remote_extract(self, ssh, file, location = None):
        print(f'extract {file} on server')
        extract_cmd = f'tar -xzvf {file}'

        if location:
            extract_cmd += f" -C {location}"
        print(extract_cmd)
        stdin,stdout,stderr=ssh.exec_command(extract_cmd)
        outlines=stdout.readlines()
        resp=''.join(outlines)
        print(resp)

    def remote_import_table(self,ssh, file):
        #import sql to remote
        print('importing table on remote db')
        # import_cmd = f'mysql -u {remote_db_username} -p{remote_db_password} -D {remote_db} -e "\. {file}÷"'
        # login path needs to be set up on the remote server using mysql_config_editor set --login-path=compodio --host=localhost --user=xxxxx --password
        import_cmd = f'mysql --login-path=compodio -D {remote_db} -e "\. {file}"'
        
        stdin,stdout,stderr=ssh.exec_command(import_cmd)

        outlines=stdout.readlines()
        resp=''.join(outlines)
        print(resp)
        print(stderr.readlines())

        print('import complete')

    def synch_tables(self, local_path, dumpfile, compressed_dumpfile, local_table=''):
        """Handles dumping, compressing, and transferring, extrating and importing a table(s) to the remote server.
        
        if local_table is not specified, all tables are dumped and synched.

        Args:
            local_dumpfile (str): path to dumpfile that will be created
            compressed_dumpfile (str): path to compressed dumpfile that will be created
            local_table (str, optional): table to dump and synch. Defaults to ''.
        """
        
        print('synching: ', local_table)
        self.dump(local_table, f'{local_path}{dumpfile}')

        self.compress(local_path, dumpfile, compressed_dumpfile)

        ssh = self.connect()

        self.transfer(ssh, local_path, compressed_dumpfile)

        self.remote_extract(ssh, compressed_dumpfile)

        self.remote_import_table(ssh, dumpfile)
