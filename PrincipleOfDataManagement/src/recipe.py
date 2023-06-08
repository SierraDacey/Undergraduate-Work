"""
File: recipe.py
Description: Implements recipe related functionality
"""
import connect
import datetime

def recipeManagement(server, uname):
    """
    Handles the submenu of possible actions relating to recipes
    :param server: SSH tunnel to a server
    :param uname: the username of the current user
    """
    user_input = ""
    while user_input != "back":
        user_input = input("Please select an option: search, recommendations, new recipe, my recipes, sort, get recipe, make recipe, back\n")
        user_input = user_input.lower()  # make search all lower case
        if user_input == 'search':
            searchRecipe(server)
        elif user_input == 'recommendations':
            recommendedRecipes(server, uname)
        elif user_input == 'sort':
            sortRecipe(server)
        elif user_input == 'new' or user_input == 'new recipe':
            addRecipe(server, uname)
        elif user_input == 'my' or user_input == "my recipes":
            myRecipes(server, uname)
        elif user_input == 'back' or user_input == 'quit':
            break
        elif user_input == 'get recipe' or user_input == 'get':
            getRecipe(server)
        elif user_input == 'make' or user_input == 'make recipe':
            makeRecipe(server, uname)
        else:
            print("Invalid command")

def newIngredient(server, ingredient_name):
    """
    Adds a user-defined ingredient to the ingredient table
    :param server: SSH tunnel to a server
    :param recipe_id: id of the recipe in the recipe table
    """
    user_input = input("This is a new ingredient.  Please enter the unit in which it's measured.\n")
    user_input.replace("'", "''")
    user_input = user_input.lower()
    q = ("SELECT id FROM unit WHERE name = '" + user_input + "';")
    connection = connect.getConnection(server)
    try:
        c = connection.cursor()
        c.execute(q)
        result = c.fetchall()
        connection.close()
    except:
        connection.close()
        print("Error reading from unit table\n")
        return
    if len(result) > 0:
        unit_id = str(result[0][0])
    else:
        q = ("INSERT INTO unit (name) VALUES ('" + user_input + "') RETURNING id;")
        connection = connect.getConnection(server)
        try:
            c = connection.cursor()
            c.execute(q)
            result = c.fetchall()[0][0]
            connection.commit()
            connection.close()
        except:
            connection.close()
            print("Error updating unit table\n")
            return
        unit_id = str(result)
    q = ("INSERT INTO ingredient (name, unit_id) VALUES ('" + ingredient_name + "', " + 
         unit_id + ") RETURNING id;")
    connection = connect.getConnection(server)
    try:
        c = connection.cursor()
        c.execute(q)
        ingredient_id = c.fetchall()[0][0]
        connection.commit()
        connection.close()
        return ingredient_id
    except:
        connection.close()
        print("Error updating ingredient table\n")
        return
        


def addCategories(server, recipe_id):
    """
    Adds a recipe to existing or new categories
    :param server: SSH tunnel to a server
    :param recipe_id: id of the recipe in the recipe table
    """
    user_input = input("Enter a category name or 'done.'\n")
    while user_input != "done":
        user_input.replace("'", "''")
        # check if category already exists
        q = ("SELECT id FROM category WHERE name ='" + user_input + "';")
        connection = connect.getConnection(server)
        try:
            c = connection.cursor()
            c.execute(q)
            result = c.fetchall()
            connection.close()
        except:
            connection.close()
            print("Error adding categorization to database\n")
            return
        if len(result) >= 1:
            category_id = result[0][0]
            q = ("INSERT INTO recipe_categorization (recipe_id, category_id) values ("
                 + str(recipe_id) + ", " + str(category_id) + ");")
            connection = connect.getConnection(server)
            try:
                connection.cursor().execute(q)
                connection.commit()
                connection.close()
            except:
                connection.close()
                print("Error adding categorization to database\n")
                return
        else:
            # brand new category 
            q = "INSERT INTO category (name) VALUES ('" + user_input + "') RETURNING id;"
            connection = connect.getConnection(server)
            try:
                c = connection.cursor()
                c.execute(q)
                result = c.fetchall()
                connection.commit()
                connection.close()
            except:
                connection.close()
                print("Error adding new category to database\n")
                return
            q = ("INSERT INTO recipe_categorization (recipe_id, category_id) VALUES ("
                 + str(recipe_id) + ", " + str(result[0][0]) + ");")
            connection = connect.getConnection(server)
            try:
                connection.cursor().execute(q)
                connection.commit()
                connection.close()
            except:
                connection.close()
                print("Error adding categorization to database\n")
                return
        user_input = input("Enter a category name or 'done.'\n").replace("'", "''")


def addRecipe(server, uname):
    """
    Allows a user to add a new recipe to the database
    :param server: SSH tunnel to a server
    :param uname: the username of the current user
    """
    title = input("Enter the recipe title\n").replace("'", "''")
    servings = input("Enter the number of servings\n").replace("'", "")
    description = input("Enter the recipe description\n").replace("'", "''")
    cook_time = input("Enter the cook time in minutes.\n").replace("'", "")
    difficulty = input("Enter the recipe's difficulty 1-5:  Easy = 1, easy-medium = 2, " +
                       "medium = 3, medium-hard = 4, or hard = 5.\n")
    ingredients = []
    print("Enter ingredient names one at a time.  When complete, enter 'done'")
    user_input = input("Enter ingredient name or 'done.'\n")
    while user_input != "done":
        user_input.replace("'", "''")
        user_input = user_input.lower()
        q = ("SELECT i.id, u.name FROM ingredient AS i INNER JOIN unit AS u ON i.unit_id = "
             + "u.id WHERE i.name ='" + user_input + "';")
        connection = connect.getConnection(server)
        try:
            c = connection.cursor()
            c.execute(q)
            result = c.fetchall()
            connection.close()
        except:
            connection.close()
            print("Error reading from ingredient table\n")
            return
        if len(result) > 0:
            ingredient_id = str(result[0][0])
            user_input = input(user_input + " is measured by " + result[0][1] +
                               ".  Please enter a quantity.\n")
        else:
            ingredient_id = newIngredient(server, user_input)
            user_input = input("Please enter a quantity.\n")
        ingredients.append([ingredient_id, float(user_input)])
        user_input = input("Enter ingredient name or 'done.'\n")

    steps = input("Enter the cooking instructions.\n").replace("'", "''")
    q = ("INSERT INTO recipe (creation_date, username, name, cook_time, difficulty_id, "
         + "servings, description, steps) VALUES (current_timestamp, '""" + uname + "', '"
         + title + "', " + cook_time + ", " + difficulty + ", " + servings + ", '"
         + description + "', '" + steps + "') RETURNING id;")

    connection = connect.getConnection(server)
    try:
        c = connection.cursor()
        c.execute(q)
        recipe_id = c.fetchall()[0][0]
        connection.commit()
        for ingredient in ingredients:
            q = ("INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity) VALUES ("
                 + str(recipe_id) + ", " + ingredient[0] + ", " + str(ingredient[1]) + ")")
            connection.cursor().execute(q)
            connection.commit()
        connection.close()
    except:
        connection.close()
        print("Error adding recipe to database\n")
        return
    user_input = input("Would you like to categorize your recipe?\n")
    user_input = user_input.lower()
    if user_input == 'y' or user_input == 'yes':
        addCategories(server, recipe_id)
    else:
        return


def deleteRecipe(server, uname, recipe_id):
    """
    Deletes a recipe from the database.
    :param server: SSH tunnel to a server
    :param uname: the username of the current user
    :param recipe_id: id of the recipe to be deleted
    """
    # Confirm creator
    q = "SELECT username FROM recipe WHERE id = " + str(recipe_id) + ";"
    connection = connect.getConnection(server)
    try:
        c = connection.cursor()
        c.execute(q)
        result = c.fetchall()
        connection.close()
    except:
        connection.close()
        print("Error retrieving recipe ownership information\n")
        return
    if len(result) == 1:
        if result[0][0] != uname:
            print("You can only delete recipes you have added.\n")
            return
    else:
        print("Error retrieving recipe ownership information\n")
        return
    # Check if a recipe has been made
    q = "SELECT COUNT(*) FROM recipe_made WHERE recipe_id = " + str(recipe_id) + ";"
    connection = connect.getConnection(server)
    try:
        c = connection.cursor()
        c.execute(q)
        result = c.fetchall()
        connection.close()
        if result[0][0] != 0:
            print("You can only delete recipes that haven't been made.\n")
            return
    except:
        connection.close()
        print("Error retrieving recipe information\n")
        return
    connection = connect.getConnection(server)
    # For atomicity, this section should be one transaction.
    try:
        # Delete referencing tables first: recipe_categorization, recipe_ingredients
        q = "DELETE FROM recipe_categorization WHERE recipe_id = " + str(recipe_id) + ";"
        connection.cursor().execute(q)
        q = "DELETE FROM recipe_ingredients WHERE recipe_id = " + str(recipe_id) + ";"
        connection.cursor().execute(q)
        # Delete recipe
        q = "DELETE FROM recipe WHERE id = " + str(recipe_id) + ";"
        connection.cursor().execute(q)
        connection.commit()
        connection.close()
    except:
        connection.rollback()
        connection.close()
        print("Error deleting recipe.\n")
        return


def editRecipe(server, uname, recipe_id):
    """
    Modifies an existing recipe in the database.
    :param server: SSH tunnel to a server
    :param uname: the username of the current user
    :param recipe_id: id of the recipe to be edited
    """
    # Confirm creator
    q = ("SELECT r.username, r.name, r.cook_time, d.name, r.servings, r.description, r.steps, "
         + "d.id FROM recipe AS r JOIN difficulty AS d ON r.difficulty_id = d.id WHERE r.id = "
         + str(recipe_id) + ";")
    connection = connect.getConnection(server)
    try:
        c = connection.cursor()
        c.execute(q)
        result = c.fetchall()
        connection.close()
    except:
        connection.close()
        print("Error retrieving recipe ownership information\n")
        return
    if len(result) == 1:
        if result[0][0] != uname:
            print("You can only modify recipes you created.\n")
            return
    else:
        print("Error retrieving recipe ownership information\n")
        return
    user_input = input("Recipe name: '" + result[0][1] + "' Enter 'edit' to change or any other "
                       + "key to continue.\n")
    user_input = user_input.lower()
    if user_input == 'edit':
        new_title = input("Enter the new title\n").replace("'", "''")
    else:
        new_title = result[0][1].replace("'", "''")
    user_input = input("Cook time: " + str(result[0][2]) + ". Enter 'edit' to change or or any "
                       " other key to continue.\n")
    user_input = user_input.lower()
    if user_input == 'edit':
        new_time = input("Enter the new cook time\n")
    else:
        new_time = str(result[0][2])
    user_input = input("Difficulty: " + result[0][3] + ".  Enter 'edit' to change or any other key"
                       + " to continue.\n")
    user_input = user_input.lower()
    if user_input == 'edit':
        new_difficulty = input("Enter the new difficulty 1-5:  Easy = 1, easy-medium = 2, medium "
                               + "= 3, medium-hard = 4, or hard = 5.\n")
    else:
        new_difficulty = str(result[0][7])
    user_input = input("Servings: " + str(result[0][4]) + ".  Enter 'edit' to change or any other "
                       + "key to continue.\n")
    user_input = user_input.lower()
    if user_input == 'edit':
        new_servings = input("Enter the number of servings\n")
    else:
        new_servings = str(result[0][4])
    user_input = input("Current description: " + result[0][5] + ".  Enter 'edit' to change or any "
                       + "other key to continue.\n")
    user_input = user_input.lower()
    if user_input == 'edit':
        new_description = input("Enter the updated description\n").replace("'", "''")
    else:
        new_description = result[0][5].replace("'", "''")
    user_input = input("Current instructions: " + result[0][6] + ".  Enter 'edit' to change or any"
                       + " other key to continue.\n")
    user_input = user_input.lower()
    if user_input == 'edit':
        new_steps = input("Enter the updated instruction\n").replace("'", "''")
    else:
        new_steps = result[0][6].replace("'", "''")
    q = ("UPDATE recipe SET name = '" + new_title + "', cook_time = " + new_time +
         ", difficulty_id = " + new_difficulty + ", servings = " + new_servings + 
         ", description = '" + new_description + "', steps = '" + new_steps + "' WHERE id = " + 
         str(recipe_id) + ";")
    connection = connect.getConnection(server)
    try:
        connection.cursor().execute(q)
        connection.commit()
        connection.close()
    except:
        connection.close()
        print("Error editing your recipe\n")
        return
    user_input = input("Enter 'edit' to modify recipe ingredients or press any key to skip\n")
    user_input = user_input.lower()
    if user_input == 'edit':
        while user_input != "done":
            q = ("SELECT ri.ingredient_id, u.name, ri.quantity, i.name FROM recipe_ingredients "
                "ri INNER JOIN ingredient i ON ri.ingredient_id = i.id INNER JOIN unit u ON " + 
                 "i.unit_id = u.id WHERE ri.recipe_id = " + str(recipe_id) + ";")
            connection = connect.getConnection(server)
            try:
                c = connection.cursor()
                c.execute(q)
                result = c.fetchall()
                connection.close()
            except:
                connection.close()
                print("Error retrieving recipe ingredient information\n")
                return
            print("Here are the ingredients in your recipe:")
            ind = 0
            while ind < len(result):
                print(str(ind) + ": " + str(result[ind][2]) + " " + result[ind][1] + " " + 
                      result[ind][3])
                ind += 1
            user_input = input("Select add, edit, delete, or done\n")
            user_input = user_input.lower()
            if user_input == 'edit':
                user_input = input("Enter the id of the ingredient to edit\n")
                display_id = int(user_input)
                if display_id < len(result):
                    user_input = input("Enter the updated quantity of " + result[display_id][3] 
                                       + "\n")
                    q = ("UPDATE recipe_ingredients SET quantity = " + user_input +
                         " WHERE recipe_id = " + str(recipe_id) + " AND ingredient_id = " +
                         str(result[display_id][0]) + ";")
                    connection = connect.getConnection(server)
                    try:
                        connection.cursor().execute(q)
                        connection.commit()
                        connection.close()
                    except:
                        connection.close()
                        print("Error editing your recipe\n")
                        return
                    print("Updating ingredients.")
                else:
                    print("Invalid selection")
            elif user_input == 'delete':
                user_input = input("Enter the id of the ingredient to remove\n")
                display_id = int(user_input)
                if display_id < len(result):
                    q = ("DELETE FROM recipe_ingredients WHERE recipe_id = " + str(recipe_id) +
                         " AND ingredient_id = " + str(result[display_id][0]) + ";")
                    connection = connect.getConnection(server)
                    try:
                        connection.cursor().execute(q)
                        connection.commit()
                        connection.close()
                    except:
                        connection.close()
                        print("Error editing your recipe\n")
                        return
                    print("Updating ingredients.")
                else:
                    print("Invalid selection")
            elif user_input == 'add':
                user_input = input("Enter the ingredient to add\n")
                user_input.replace("'", "''")
                
                q = ("SELECT i.id, u.name FROM ingredient AS i INNER JOIN unit AS u ON i.unit_id ="
                     + " u.id WHERE i.name ='" + user_input + "';")
                connection = connect.getConnection(server)
                try:
                    c = connection.cursor()
                    c.execute(q)
                    result = c.fetchall()
                    connection.close()
                except:
                    connection.close()
                    print("Error reading from ingredient table\n")
                    return
                if len(result) == 1:
                        ingredient_id = str(result[0][0])
                        user_input = input(user_input + " is measured by " + result[0][1] +
                                           ".  Please enter a quantity.\n")
                        connection = connect.getConnection(server)
                        try:
                            c = connection.cursor()
                            q = ("INSERT INTO recipe_ingredients (recipe_id, ingredient_id, " + 
                                 "quantity) VALUES (" + str(recipe_id) + ", " + ingredient_id + 
                                 ", " + user_input + ")")
                            connection.cursor().execute(q)
                            connection.commit()
                            connection.close()
                            print("Recipe ingredients updated.")
                        except:
                            connection.close()
                            print("Error adding ingredient to recipe\n")
                            return
                else:
                        print("Invalid ingredient")
            elif user_input == 'done':
                break
            else:
                print("Invalid selection")


def makeRecipe(server, uname):
    """
    Allows a user to mark a recipe as made and adjusts their pantry.
    :param server: SSH tunnel to a server
    :param uname: the username of the current user
    """

    name = input("Please input the name of the recipe\n").replace("'", "''")

    query = "SELECT id FROM recipe WHERE name = '" + name + "';"

    connection = connect.getConnection(server)
    try:
        c = connection.cursor()
        c.execute(query)
        result = c.fetchall()
        connection.close()
        if len(result) == 0:
            print("No recipe matching that name")
            return
    except:
        connection.close()
        print("Error reading from recipe table\n")
        return

    recipe_id = result[0][0]
    makeRecipeById(server, uname, recipe_id)

def makeRecipeById(server, uname, recipe_id):
    """
    Allows a user to mark a recipe as made and adjusts their pantry.
    :param server: SSH tunnel to a server
    :param uname: the username of the current user
    :param recipe_id: id (key) in the recipe table
    """

    scale = input("Enter a scale for the recipe (1 for default, 2 to double, etc)\n")
    # Confirm that the user has all ingredients
    q = ("SELECT ingredient_id, quantity*" + scale + ", i.name FROM recipe_ingredients ri  " 
        + "INNER JOIN ingredient i ON ri.ingredient_id = i.id WHERE "
         "recipe_id = " + str(recipe_id) + " ORDER BY ingredient_id;")
    connection = connect.getConnection(server)
    try:
        c = connection.cursor()
        c.execute(q)
        recipe_ingredients = c.fetchall()
        connection.close()
    except:
        connection.close()
        print("Error retrieving recipe information\n")
        return
    q = ("SELECT p.ingredient_id, (CASE WHEN current_quantity IS null THEN quantity_purchased "
        + "ELSE current_quantity END) - " + scale + " *(ri.quantity) AS new_quantity FROM "
        + "pantry p INNER JOIN recipe_ingredients ri ON p.ingredient_id = ri.ingredient_id WHERE "
        + "p.username = '" + uname + "' AND ri.recipe_id = " + str(recipe_id) + ";")
    connection = connect.getConnection(server)
    try:
        c = connection.cursor()
        c.execute(q)
        pantry_ingredients = c.fetchall()
        connection.close()
    except:
        connection.close()
        print("Error retrieving pantry information\n")
        return
    if len(recipe_ingredients) == len(pantry_ingredients):
        print("All ingredients are in your pantry")
        quantity_check = 1
        for i in pantry_ingredients:
            if i[1] < 0:
                quantity_check = 0
        if quantity_check == 1:
            user_input = input("Would you like to rate the recipe?  Enter Y to rate.\n")
            user_input = user_input.lower()
            rating = "NULL"
            if user_input == "y" or user_input == "yes":
                rating = input("Enter a rating 0-5\n")
                try:
                    int_rating = int(rating)
                    if int_rating < 0 or int_rating > 5:
                        rating = "NULL"
                        raise ValueError()
                except:
                    print("Invalid value - no rating will be added.")
            q = ("UPDATE pantry SET current_quantity = (CASE WHEN current_quantity IS null THEN " +
                "quantity_purchased ELSE current_quantity END) - (recipe_ingredients.quantity)*" + 
                scale + " FROM recipe_ingredients WHERE pantry.ingredient_id = "
                "recipe_ingredients.ingredient_id AND pantry.username = '" + uname + 
                "' AND recipe_ingredients.recipe_id = " + str(recipe_id) + ";")
            q2 = ("INSERT INTO recipe_made (date_made, username, recipe_id, rating) VALUES " +
                "(current_timestamp, '" + uname + "', " + str(recipe_id) + ", " + rating + ");" )
            connection = connect.getConnection(server)
            try:
                #this should be one transaction for atomicity
                connection.cursor().execute(q)
                connection.cursor().execute(q2)
                connection.commit()
                connection.close()
            except:
                connection.close()
                print("Error retrieving pantry information")
                return  
            print("Recipe recorded.")
        else: 
            print("Unfortunately, you do not have sufficient quantities to make this recipe.")  
    else:
        missing_ingredients = []
        for i in recipe_ingredients:
          missing_ingredients.append(i[2])
        print("You do not have the necessary ingredients to make this recipe.  It requires:\n"
              + ", ".join(missing_ingredients))

def myRecipes(server, uname):
    """
    Lists a user's recipes and provides a menu for editing and deleting.
    :param server: SSH tunnel to a server
    :param uname: the username of the current user
    """
    q = ("SELECT id, name FROM recipe WHERE username = '" + uname + "';")
    connection = connect.getConnection(server)
    try:
        c = connection.cursor()
        c.execute(q)
        result = c.fetchall()
        connection.close()
    except:
        connection.close()
        print("Error retrieving your recipes\n")
        return

    if len(result) >= 1:
        print("Here are the recipes you have submitted:")
        ind = 0
        while ind < len(result):
            print(str(ind) + ": " + result[ind][1])
            ind += 1
        user_input = input("Select edit, delete, or back\n")
        user_input = user_input.lower()
        if user_input == 'delete':
            user_input = input("Enter the id of the recipe to delete\n")
            display_id = int(user_input)
            if display_id < len(result):
                user_input = input("Deleting recipe '" + result[display_id][1] + "' - enter 'y' to confirm.\n")
                user_input = user_input.lower()
                if user_input == 'y' or user_input == 'yes':
                    deleteRecipe(server, uname, result[display_id][0])
                else:
                    print("Deletion canceled.\n")
            else:
                print("Invalid selection.\n")
        elif user_input == 'edit':
            user_input = input("Enter the id of the recipe to edit\n")
            display_id = int(user_input)
            if display_id < len(result):
                editRecipe(server, uname, result[display_id][0])
            else:
                print("Invalid selection.\n")
        elif user_input == 'back' or user_input == 'quit':
            return
        else:
            print("Invalid command")
            return
    else:
        print("You don't have any recipes to manage.\n")
        return


def searchRecipe(server):
    """
    Handles searching for recipes in various ways
    :param server: SSH tunnel to a server
    """
    search_type = input("Please select how to search by: name, category, ingredient\n")
    search_value = input("Please enter search value:\n")
    search_type = search_type.lower()
    query = ""
    if search_type != "name" and search_type != "category" and search_type != "ingredient":
        print("Invalid command")
        searchRecipe(server)
        return
    elif search_type == "name":
        query = "SELECT " + search_type + " FROM recipe WHERE " + search_type + " LIKE '%" + search_value + "%' ORDER BY " + search_type + " ASC;"
    elif search_type == "category":
        query = "SELECT name FROM recipe WHERE id IN (SELECT recipe_categorization.recipe_id FROM recipe_categorization " \
                "WHERE recipe_categorization.category_id = ( SELECT id FROM category WHERE name = '" + search_value + "')) " \
                "ORDER BY name ASC;"
    elif search_type == "ingredient":
        query = "SELECT name FROM recipe WHERE id IN (SELECT recipe_ingredients.recipe_id FROM recipe_ingredients " \
                "INNER JOIN ingredient ON recipe_ingredients.ingredient_id = ingredient.id WHERE ingredient.name like '%"\
                + search_value + "%' ) ORDER BY name ASC;"
    try:
        connection = connect.getConnection(server)
        c = connection.cursor()
        c.execute(query)
        result = c.fetchall()
        connection.close()
        if len(result) == 0:
            print("No matching " + search_type + "\'s")
            searchAgain = input("Want to search again? (Y/N)")
            searchAgain = searchAgain.lower()
            if searchAgain == "y" or "yes":
                searchRecipe(server)
                return
            else:
                return
        else:
            formatResults(result)
    except:
        connection.close()
        print("Error reading from recipe table\n")
        return


def sortRecipe(server):
    """
    Handles sorting recipes in various orders
    :param server: SSH tunnel to a server
    """
    sort_type = input("Please select how to sort by: name, rating, most recent\n")
    query = ""
    if sort_type == "name":
        query = "SELECT name FROM recipe ORDER BY name ASC"
    elif sort_type == "rating":
        sortRecipeRating(server)
        return
    elif sort_type == "most recent" or "recent":
        query = "SELECT name FROM recipe ORDER BY creation_date DESC"
    else:
        print("Invalid command")
        sortRecipe(server)
        return
    try:
        connection = connect.getConnection(server)
        c = connection.cursor()
        c.execute(query)
        result = c.fetchall()
        if len(result) == 0:
            print("No recipes in table")
        else:
            formatResults(result)
        connection.close()
    except:
        connection.close()
        print("Error reading from recipe table\n")
        return


def sortRecipeRating(server):
    """
    Sorts the recipes in the server by rating
    :param server: SSH tunnel to a server
    """
    query = "SELECT name, weighted_rating FROM recipe INNER JOIN (SELECT recipe_id AS recipe_id, SUM(rating)/ COUNT(*) " \
            "AS weighted_rating FROM recipe_made GROUP BY recipe_id) AS rating_info ON recipe.id = rating_info.recipe_id " \
            "ORDER BY weighted_rating DESC"
    try:
        connection = connect.getConnection(server)
        c = connection.cursor()
        c.execute(query)
        result = c.fetchall()
        if len(result) == 0:
            print("No recipes rating stored")
            return
        else:
            for item in result:
                try:
                    print("%s : %d" %(item[0], item[1]))
                except:
                    print("%s : No rating" %(item[0]))
        connection.close()
    except:
        connection.close()
        print("Error reading from recipe table\n")
        return


def formatResults(results):
    """
    Prints the given results
    :param results: a list of items to print
    """
    for result in results:
        print(result[0])


def getRecipe(server):
    """
    Asks a user for the recipe they want to get and prints it for them
    :param server: SSH tunnel to a server
    """
    name = input("Please input recipe name you would like\n").replace("'", "''")

    query = "SELECT id, name, description, servings, difficulty_id, cook_time, steps "\
            "FROM recipe WHERE name = '" + name + "';"
    try:
        connection = connect.getConnection(server)
        c = connection.cursor()
        c.execute(query)
        result = c.fetchall()
        connection.close()
        if len(result) == 0:
            print("No recipe matching that name")
        else:
            print("Name: %s" %result[0][1])
            print("Description: %s" %result[0][2])
            print("Servings: %d" %result[0][3])
            print("Difficulty: %d" %result[0][4])
            print("Cook time: %d" %result[0][5])
            print("Instructions: %s" %result[0][6])
    except:
        connection.close()
        print("Error reading from recipe table\n")
        return


def getRecipeById(server, recipe_id, uname):
    """
    Displays a recipe
    :param server: SSH tunnel to a server
    """
    q = "SELECT r.id, r.name, r.description, r.servings, d.name, r.cook_time, r.steps FROM " \
        "recipe r INNER JOIN difficulty d  ON r.difficulty_id = d.id WHERE r.id = " \
        + str(recipe_id) + ";"
    q2 = "SELECT i.name, ri.quantity, u.name FROM recipe_ingredients ri INNER JOIN ingredient i "\
         "ON ri.ingredient_id = i.id INNER JOIN unit u ON i.unit_id = u.id WHERE ri.recipe_id = " \
         + str(recipe_id) + ";"
    try:
        connection = connect.getConnection(server)
        c = connection.cursor()
        c.execute(q)
        result = c.fetchall()
        connection.close()
        connection = connect.getConnection(server)
        c = connection.cursor()
        c.execute(q2)
        ingreds = c.fetchall()
        connection.close()        
    except:
        connection.close()
        print("Error reading from recipe table\n")
        return
    if len(result) == 0:
        print("Recipe not found")
    else:
        print("Name: %s" %result[0][1])
        print("Description: %s" %result[0][2])
        print("Servings: %d" %result[0][3])
        print("Difficulty: %s" %result[0][4])
        print("Ingredients: ")
        for i in ingreds:
            print(str(i[1]) + " " + i[2] + " " + i[0])
        print("Cook time: %d" %result[0][5])
        print("Instructions: %s" %result[0][6])
    user_input = input("Did you make this recipe?  Enter 'make' to mark it as made or 'back' "\
                 "to return.\n")
    if user_input.lower() == 'make':
        makeRecipeById(server, uname, recipe_id)


def recommendedRecipes(server, uname):
    """
    Menu provides recommded recipes based on rating, popularity, and other criteria
    :param server: SSH tunnel to a server
    :param uname: the username of the current user
    """
    print("Please select a recommendation type:")
    print("1: Top Rated: See the 50 best-rated recipes")
    print("2: Newest: See the 50 most recently added recipes")
    print("3: Your Pantry: See recipes you can make with your current pantry ingredients")
    print("4: Recommended: See recipes made by other users who make the same recipes as you")
    user_input = input("Enter an option (1-4)\n")
    q = ''
    m = ''
    if user_input == '1':
        q = "SELECT r.id, r.name, r.creation_date, r.username, avg(rm.rating) FROM recipe r " \
            "INNER JOIN recipe_made rm ON r.id = rm.recipe_id WHERE rm.rating IS NOT null " \
            "GROUP BY r.id ORDER BY avg(rm.rating) DESC LIMIT 50;"
        m = "Here are the 50 best-rated recipes:"
    elif user_input == '2':
        q = "SELECT r.id, r.name, r.creation_date, r.username, avg(rm.rating) FROM recipe r "\
            "INNER JOIN recipe_made rm on r.id = rm.recipe_id GROUP BY r.id, r.creation_date, "\
            "r.name, r.id, r.username ORDER BY r.creation_date DESC LIMIT 50;"
        m = "Here are the 50 newest recipes:"
    elif user_input == '3':
        q = "SELECT r.id, r.name, r.creation_date, r.username, avg(rm.rating) FROM recipe r " \
            "inner JOIN recipe_ingredients ri ON r.id = ri.recipe_id inner JOIN pantry p ON " \
            "ri.ingredient_id = p.ingredient_id LEFT JOIN  recipe_made rm ON r.id = rm.recipe_id "\
            "WHERE p.username = '" + uname + "' AND ri.quantity < COALESCE(p.current_quantity, "\
            "p.quantity_purchased) AND r.id NOT IN (SELECT r2.recipe_id FROM recipe_ingredients "\
            "r2 WHERE r2.ingredient_id NOT IN (SELECT DISTINCT p2.ingredient_id FROM pantry p2 "\
            "WHERE p2.username = '" + uname + "')) GROUP BY r.id ORDER BY avg(rm.rating) DESC "\
            "NULLS LAST;"
        m = "Here are the recipes you can make with your current pantry ingredients:"
    elif user_input == '4':
        q = "SELECT  r.id, r.name, r.creation_date, r.username, avg(rm.rating) FROM recipe r "\
            "INNER JOIN recipe_made rm ON r.id = rm.recipe_id WHERE rm.username IN (SELECT "\
            "DISTINCT rm2.username FROM recipe_made rm1 INNER JOIN recipe_made rm2 ON "\
            "rm1.recipe_id = rm2.recipe_id WHERE rm1.username = '" + uname + "') AND r.id NOT IN "\
            "(SELECT recipe_id FROM recipe_made WHERE username = '" + uname + "') GROUP BY r.id "\
            "ORDER BY avg(rm.rating) DESC;"
        m = "Here are the other recipes made by users who made the same recipes you've made:"    
    else:
        return
    if len(q) > 0:
        connection = connect.getConnection(server)
        try:
            c = connection.cursor()
            c.execute(q)
            result = c.fetchall()
            connection.close()
        except:
            connection.close()
            print("Error retrieving your recipes\n")
            return
        if len(result) > 0:
            ind = 0
            print(m);
            rating = 'not yet rated'
            if result[ind][4] is not None:
                rating = "{:.2f}".format(result[ind][4])
            while ind < len(result):
                print(str(ind) + ": " + result[ind][1]  + " added on " + 
                result[ind][2].strftime('%b %d %Y') + " average rating: " + rating)
                ind += 1
            user_input = input("Enter the number to view a recipe or 'Back' to return\n")
            if user_input.isnumeric():
                if int(user_input) <= len(result):
                    getRecipeById(server, result[int(user_input)][0], uname)
        else:
            print("This search returns no recipes.")
    return
