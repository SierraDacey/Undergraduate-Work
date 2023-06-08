"""
File: account.py
Description: Implements functions relating to creating or logging in to an account
"""
import connect


def signup(server):
    """
    Processes the action of creating a new user account, ensuring that the username
    is not already associated with an account
    :returns True/False, username/None depending on if the action was successful
    """
    available = 0
    uname = input("Enter a username:")
    # check availability in database
    connection = connect.getConnection(server)
    try:
        c = connection.cursor()
        q = """select * from users where username = '""" + uname + """';"""
        c.execute(q)
        if len(c.fetchall()) == 0:
            available = 1
    except:
        print("Error reading from users table.\n")
    finally:
        connection.close()

    if available:
        pw = input(uname + " is available.  Please select a password:")
        query = """INSERT INTO users (username, password, last_login, creation_date) VALUES ('""" \
                + uname + """', '""" + pw + """', current_timestamp, current_timestamp);"""

        connection = connect.getConnection(server)
        try:
            c = connection.cursor()
            c.execute(query)
            connection.commit()
            connection.close()
            print("Signup succeeded")
            return True, uname
        except:
            connection.close()
            print("Error adding to users table.\n")
            return False, None
    else:
        selection = '0'
        while selection != '1' and selection != '2':
            print(uname + " is not available.")
            return False, None


def login(server):
    """
    Processes the action of logging in to an existing account
    :returns True/False, username/None depending on if the action was successful
    """
    valid_name = 0
    uname = input("Enter your username: ")
    password = input("Enter your password: ")

    connection = connect.getConnection(server)
    try:
        cursor = connection.cursor()
        q = """select username, password from users where username = '""" + uname + """';"""
        cursor.execute(q)
        result = cursor.fetchall()
        connection.close()
    except:
        connection.close()
        print("Error reading from users table.\n")
        return False, None

    if len(result) == 1:
        valid_name = 1

    if valid_name and password == result[0][1]:
        query = """UPDATE users SET last_login = current_timestamp WHERE username = '"""+ uname + """';"""

        connection = connect.getConnection(server)
        try:
            c = connection.cursor()
            c.execute(query)
            connection.commit()
            connection.close()
            print("Welcome " + uname)
            return True, uname
        except:
            connection.close()
            print("Error logging in.\n")
            return False, None
    else:
        selection = '0'
        while selection != '1' and selection != '2':
            print("Invalid username or password.")
            return False, None