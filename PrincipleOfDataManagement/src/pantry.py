"""
File: pantry.py
Description: Implements functions relating managing a pantry
"""
import datetime, time
import connect


def pantryManagement(server, uname):
    """
    Handles the submenu of possible actions relating to the pantry
    :param uname: the username of the current user
    """
    user_input = ""
    while user_input != "back":
        user_input = input("Please select an option: new ingredient, edit ingredient, back\n")
        user_input = user_input.lower()

        if user_input == 'new' or user_input == 'new ingredient':
            addIngredient(server, uname)
        elif user_input == 'edit' or user_input == 'edit ingredient':
            editIngredient(server, uname)
        elif user_input == 'back':
            break
        else:
            print("Invalid command")


def handleDate(dateString):
    """
    Converts a string in mm/dd/yyyy format to a date object
    :param dateString: the string to convert
    :return: the date object, None if the conversion fails
    """
    try:
        date_time = time.strptime(dateString, "%m/%d/%Y")
        date = datetime.date(date_time.tm_year, date_time.tm_mon, date_time.tm_mday)
        return date
    except ValueError:
        return None


def addIngredient(server, uname):
    """
    Manages adding a new ingredient to a users pantry
    :param uname: the name of the user adding the ingredient
    """

    ingredient_name = input("Please enter the name of the new ingredient to add: ")
    ingredient_name = ingredient_name.lower()

    # Get the ingredient's id from its name
    q = "SELECT id FROM ingredient WHERE name = '" + ingredient_name + "';"

    connection = connect.getConnection(server)
    try:
        c = connection.cursor()
        c.execute(q)
        result = c.fetchall()
        connection.close()
        if len(result) == 1:
            ingredient_id = str(result[0][0])
        else:
            print("Invalid ingredient")
            return
    except:
        connection.close()
        print("Error reading from ingredient table\n")
        return

    # Determine if the user already has the ingredient in their pantry
    q = "SELECT current_quantity FROM pantry WHERE username = '" + uname \
        + "' AND ingredient_id = " + ingredient_id + ";"
    connection = connect.getConnection(server)
    try:
        c = connection.cursor()
        c.execute(q)
        result = c.fetchall()
        connection.close()
        if len(result) != 0:
            current_quantity = result[0][0]
            if current_quantity == 0:
                q = "DELETE FROM pantry WHERE username = '" + uname + \
                    "' AND ingredient_id = " + ingredient_id + ";"
                connection = connect.getConnection(server)
                c = connection.cursor()
                c.execute(q)
                connection.commit()
                connection.close()
            else:
                print("This ingredient is already in pantry. Consider editing the ingredient instead")
                return
    except:
        connection.close()
        print("Error reading from pantry\n")
        return

    # Get user input for additional fields in pantry
    quantity_int = -1
    quantity = ""
    while quantity_int == -1:
        quantity = input("Quantity purchased: ")
        if not quantity.isnumeric():
            print("Quantity must be a number")
        else:
            quantity_int = int(quantity)
            if quantity_int <= 0:
                print("Quantity must be positive")
                quantity_int = -1

    purchase_date = expiration_date = None
    while purchase_date is None:
        purchase_date = handleDate(input("Purchase date (mm/dd/yyyy): "))
        if purchase_date is None:
            print("Invalid date. Try again")

    add_expiration = None
    while add_expiration is None:
        expiration_input = input("Would you like to add an expiration date? (Y/N) ")
        expiration_input = expiration_input.capitalize()
        if expiration_input == 'Y':
            add_expiration = True
        elif expiration_input == 'N':
            add_expiration = False
        else:
            print("Invalid response")

    if add_expiration is True:
        expiration_date = None
        while expiration_date is None:
            expiration_date = handleDate(input("Expiration date (mm/dd/yyyy): "))
            if expiration_date is None:
                print("Invalid date. Try again")

    # Check if the user would like to add an aisle
    add_aisle = None
    while add_aisle is None:
        aisle_input = input("Would you like to add an aisle? (Y/N) ")
        aisle_input = aisle_input.capitalize()
        if aisle_input == 'Y':
            add_aisle = True
        elif aisle_input == 'N':
            add_aisle = False
        else:
            print("Invalid response")

    aisle_str = ""
    if add_aisle:
        aisle_name = input("Aisle name: ")
        aisle_name.lower()
        q = "SELECT id FROM aisle WHERE name = '"+aisle_name+"';"
        connection = connect.getConnection(server)
        try:
            c = connection.cursor()
            c.execute(q)
            result = c.fetchall()
            connection.close()
            if len(result) != 1:
                print("Aisle invalid. No aisle will be added")
                add_aisle = False
            else:
                aisle_id = str(result[0][0])
                aisle_str = ", " + aisle_id
        except:
            connection.close()
            print("Error reading from aisle\n")
            return

    # Add new ingredient
    q_columns = "INSERT INTO pantry (username, ingredient_id, " \
                "quantity_purchased, current_quantity, purchase_date"

    q_values = "VALUES ('" + uname + "', " + ingredient_id + ", " \
               + quantity + ", " + quantity + ", '" + str(purchase_date) + "'"

    if add_expiration:
        q_columns = q_columns + ", expiration_date"
        q_values = q_values + ", '"+str(expiration_date)+"'"

    if add_aisle:
        q_columns = q_columns + ", aisle"
        q_values = q_values + ", " + aisle_str

    q = q_columns + ") " + q_values + ");"
    connection = connect.getConnection(server)
    try:
        c = connection.cursor()
        c.execute(q)
        connection.commit()
        connection.close()
        print("Ingredient successfully added")
    except:
        connection.close()
        print("Error adding ingredient to pantry")
        return


def editIngredient(server, uname):
    """
    Manages manually editing the quantity of an ingredient in the pantry
    :param uname: The name of the user editing the ingredient
    """
    ingredient_name = input("Please enter the name of the ingredient to edit: ")
    ingredient_name = ingredient_name.lower()

    # Get the ingredient's id from its name
    q = "SELECT id FROM ingredient WHERE name = '" + ingredient_name + "';"
    connection = connect.getConnection(server)
    try:
        c = connection.cursor()
        c.execute(q)
        result = c.fetchall()
        connection.close()
        if len(result) == 1:
            ingredient_id = str(result[0][0])
        else:
            print("Invalid ingredient")
            return
    except:
        connection.close()
        print("Error reading from ingredient table\n")
        return

    # Determine if the user already has the ingredient in their pantry
    q = "SELECT current_quantity FROM pantry WHERE username = '" + uname + "' AND ingredient_id = " + ingredient_id
    connection = connect.getConnection(server)
    try:
        c = connection.cursor()
        c.execute(q)
        result = c.fetchall()
        connection.close()
        if len(result) == 0:
            print("Ingredient not in pantry, add ingredient instead")
            return
    except:
        connection.close()
        print("Error reading from pantry\n")
        return

    quantity = result[0][0]
    print("Current quantity of '"+ingredient_name+"' is: "+ str(quantity))
    new_quantity_int = -1
    new_quantity = ""
    while new_quantity_int == -1:
        new_quantity = input("Please enter a new quantity: ")
        if not new_quantity.isnumeric():
            print("New quantity must be a number")
        else:
            new_quantity_int = int(new_quantity)
            if new_quantity_int < 0:
                print("New quantity must not be negative")
                new_quantity_int = -1

    q = "UPDATE pantry SET current_quantity = " + new_quantity + \
        "WHERE username = '" + uname + "' AND ingredient_id = " + ingredient_id
    connection = connect.getConnection(server)
    try:
        c = connection.cursor()
        c.execute(q)
        connection.commit()
        connection.close()
        print("Quantity successfully updated")
    except:
        connection.close()
        print("Error updating pantry\n")
        return
