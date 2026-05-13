import tkinter as tk

def main():
    root = tk.Tk()
    root.title("Hello World")
    root.geometry("300x200")
    label = tk.Label(root, text="Hello World", font=("Arial", 24))
    label.pack(expand=True)
    root.mainloop()

if __name__ == "__main__":
    main()
