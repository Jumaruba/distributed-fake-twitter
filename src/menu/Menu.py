from ..consts import MENU_SIZE

class Menu:
    def __new__(cls):
        # Singleton class
        if not hasattr(cls, 'instance'):
            cls.instance = super(Menu, cls).__new__(cls)
        return cls.instance

    @staticmethod
    def normalize(string, size=None):
        string = str(string)
        if size is None:
            size = MENU_SIZE
        remaining = size - len(string)
        padding_right = (size - len(string)) // 2
        padding_left = padding_right + remaining % 2
        return padding_left * " " + string + padding_right * " "

    @staticmethod
    def replicate(char, size=None):
        if size is None:
            size = MENU_SIZE
        return size * char

    @staticmethod
    def print_table(rows):
        for row in rows:
            print("||" + row + "||")

    @staticmethod
    def show_initial_menu():
        Menu.print_table([
            Menu.replicate("="),
            Menu.normalize("WELCOME TO FAKE_TWITTER"),
            Menu.replicate("="),
            Menu.normalize("[1] Login"),
            Menu.normalize("[2] Exit"),
            Menu.replicate("="),
        ])

    @staticmethod 
    def get_option(min_value, max_value):
        Menu.show_initial_menu()
        while True: 
            try: 
                option = int(input("Choose an option: "))
                if option < min_value or option > max_value:
                    print(f"Your input should be in the range [{min_value}, {max_value}]")
                else:
                    # If option = 1 ask for username
                    return option 
            except ValueError: 
                print(f"Your input should be an integer.")

