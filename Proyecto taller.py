import tkinter as tk
from tkinter import messagebox
import datetime
import os

def main():
    root = tk.Tk()
    root.title("Virus Spread Game")

    frame = tk.Frame(root)
    frame.pack(expand=True)

    btn1 = tk.Button(frame, text="New Game")
    btn1.pack(pady=10)

    btn2 = tk.Button(frame, text="Options", command=options)
    btn2.pack(pady=10)

    btn3 = tk.Button(frame, text="Resume Game")
    btn3.pack(pady=10)

    root.geometry("250x250")
    root.mainloop()

def options():
    root = tk.Tk()
    root.title("Options")

    frame = tk.Frame(root)
    frame.pack(expand=True)

    lbl = tk.Label(frame, text="Choose difficulty")
    lbl.pack(pady=20)

    root.geometry("250x250")
    root.mainloop()

if __name__ == "__main__":
    main()