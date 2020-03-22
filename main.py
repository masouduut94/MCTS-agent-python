from tkinter import Tk

from gui import Gui


def main():
    root = Tk()
    interface = Gui(root)
    root.mainloop()


if __name__ == "__main__":
    main()
