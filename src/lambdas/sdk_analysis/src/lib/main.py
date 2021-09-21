from sshtunnel import SSHTunnelForwarder
import pymysql
import paramiko
from io import StringIO 
from ssm import get_secrets
from ssm import get_endpoints

secrets = get_secrets()
ssh_pkey = secrets['ssh_pkey']
db_username = secrets['username']
db_password = secrets['password']

endpoints = get_endpoints()
db_host = endpoints["rds_endpoint"]
ssh_host = endpoints["ec2_endpoint"]
ssh_user = "ec2-user"
db_name = "mantarray_recordings"

def open_ssh_tunnel():
    """Open an SSH tunnel and connect using a username and password.
    
    :param verbose: Set to True to show logging
    :return tunnel: Global SSH tunnel connection
    """
    pkey = StringIO(ssh_pkey)
    k = paramiko.RSAKey.from_private_key(pkey)

    with SSHTunnelForwarder(
        (ssh_host, 22),
        ssh_username=ssh_user,
        ssh_pkey=k,
        remote_bind_address=(db_host, 3306)
    ) as tunnel:
        #should this be a different host once deployed?
        conn = pymysql.connect(host='127.0.0.1', user=db_username,
            passwd=db_password, db=db_name,
            port=tunnel.local_bind_port)

        cur = conn.cursor()

        cur.execute("describe s3_objects;")
        data = cur.fetchall()
        for x in data:
            print(x)

        tunnel.close()

open_ssh_tunnel()
