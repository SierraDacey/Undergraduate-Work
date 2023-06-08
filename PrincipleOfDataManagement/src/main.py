import pantry, account, recipe, connect


def main():
    server = connect.startServer()

    user_input = ""
    logged_in = False
    user_name = None
    while user_input != 'quit':
        if logged_in:
            user_input = input("Please select an option: recipes, pantry, logout, quit\n")
        else:
            user_input = input("Please select an option: signup, login, quit\n")

        user_input = user_input.lower()

        if user_input == 'signup' and not logged_in:
            logged_in, user_name = account.signup(server)
        elif user_input == 'login'and not logged_in:
            logged_in, user_name = account.login(server)
        elif user_input == 'logout' and logged_in:
            logged_in = False
            user_name = None
        elif user_input == 'pantry' and logged_in:
            pantry.pantryManagement(server, user_name)
        elif (user_input == 'recipes' or user_input == 'recipe') and logged_in:
            recipe.recipeManagement(server, user_name)
        elif user_input == 'quit':
            print("You exited the program.")
            server.close()
        else:
            print("Invalid command")


main()
