import psycopg2
from sshtunnel import SSHTunnelForwarder

# CS DEPT PW
user = ""
pw = ""


def startServer():
    """
    Starts and returns an SSH tunnel to the CS department starbug server
    :return: the SSH tunnel
    """

    server = SSHTunnelForwarder(
        ('starbug.cs.rit.edu', 22),
        ssh_username=user,
        ssh_password=pw,
        remote_bind_address=('localhost', 5432))

    server.start()
    print("SSH tunnel established")
    return server


def getConnection(server):
    """
    Starts a connection to the provided server
    :param server: The server to connect to
    :return: the connection
    """

    params = {
        'database': 'p320_12',
        'user': user,
        'password': pw,
        'host': 'localhost',
        'port': server.local_bind_port
    }
    conn = psycopg2.connect(**params)
    return conn
