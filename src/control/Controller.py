from .Menu import Menu
import asyncio


class Controller:
    def __init__(self, peer) -> None:
        self.peer = peer

    def handle(self, title, options):
        option = Menu.get_option(title, list(options.keys()))
        return options[option]()

    def run(self):
        options = {
            "Show timeLine": Controller.example,
            "Show followers": Controller.example,
            "Follow a user": Controller.example,
            "Exit": exit
        }
        self.handle("Main Menu", options)

    def run_in_loop(self, function):
        return asyncio.run_coroutine_threadsafe(function, self.peer.loop)

    @staticmethod
    def example():
        print("Ignoring...")

    # -------------------------------------------------------------------------
    # START MENU
    # -------------------------------------------------------------------------

    def start(self):
        # NOTE, to get the results from operations task it's necessary to use function_name.result()
        options = {
            "Register": self.register,
            "Login": self.login,
            "Exit": exit
        }
        future = self.handle("Welcome", options)

        # Check result
        status = future.result()
        if not status[0]:
            print("[ ERROR ]", status[1])
        else:
            print("[ SUCCESS ]", status[1])

    def register(self):
        username = input("Type your username: ")
        return self.run_in_loop(self.peer.register(username))

    def login(self):
        username = input("Type your username: ")
        return self.run_in_loop(self.peer.login(username))
