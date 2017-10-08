from sys import path as syspath
from os import path


def main():
    syspath.append(path.join(path.dirname(__file__), ".."))

    from appapi.app import App
    app = App()
    app.run()

if __name__ == '__main__':
    main()
