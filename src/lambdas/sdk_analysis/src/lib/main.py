from sshtunnel import SSHTunnelForwarder
import pymysql
from ssm import get_secrets

secrets = get_secrets()
ssh_pkey = secrets['ssh_pkey']
db_username = secrets['username']
db_password = secrets['password']
db_host = "iac-253-mantarray-rds-1.cya18gqzi4zd.us-east-1.rds.amazonaws.com"
ssh_host = "ec2-54-226-191-183.compute-1.amazonaws.com"
ssh_user = "ec2-user"

def open_ssh_tunnel():
    """Open an SSH tunnel and connect using a username and password.
    
    :param verbose: Set to True to show logging
    :return tunnel: Global SSH tunnel connection
    """
    
    global tunnel
    with SSHTunnelForwarder(
        (ssh_host, 22),
        ssh_username=ssh_user,
        ssh_pkey=ssh_pkey,
        remote_bind_address=(db_host, 3306),
        local_bind_address=("127.0.0.1", 3306)
    ) as tunnel:
        db = pymysql.connect(host='127.0.0.1', 
            user=db_username,
            password=db_password, 
            port=tunnel.local_bind_port)
    try:
        # Print all the databases
        with db.cursor() as cur:
            cur.execute('SHOW DATABASES')
            for r in cur:
                print(r)
    finally:
        db.close()

open_ssh_tunnel()
