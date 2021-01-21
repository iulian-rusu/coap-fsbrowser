from src.app_root import AppRoot
from src.test_server import TestServer

if __name__ == '__main__':
    my_server = TestServer('127.0.0.1', 5683)
    my_server.start()

    app = AppRoot()
    app.mainloop()

    my_server.stop()
