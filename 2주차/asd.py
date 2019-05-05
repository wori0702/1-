from tkinter import *
from tkinter import messagebox

def func_open():
    messagebox.showinfo("메뉴 선택","열기 메뉴를 선택함")

def func_exit():
    window.quit()
    window.destroy()

window = Tk()

mainMenu = Menu(window)
window.configure(menu = mainMenu)

window.mainloop()