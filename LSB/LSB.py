from tkinter.constants import END, NW, WORD
from PIL import Image as Img
from PIL import ImageTk, Image
import numpy as np
import tkinter.ttk as ttk
from tkinter import Button, Canvas, Entry, Frame, Label, Menu, StringVar, Text, Tk, Toplevel, filedialog as fd
from tkinter import messagebox as mb
from tkinter import messagebox
import datetime

def encript_image(imagename, text):
    im = Img.open(imagename)
    im = im.convert('RGBA')
    m, n = im.size
    txt = text
    ln = len(txt)
    image = im.copy()
    nw = image.load()
    for i in range(8):
        r, g, b, a = im.getpixel((i, n - 1))
        r = ((r & 254) | (1 if (ln & (1 << i)) > 0 else 0))
        nw[i, n - 1] = (r, g, b, a)
    x = 8
    y = n - 1
    for i in range(ln):
        c = ord(txt[i])
        if c > 900:
            c = c - 848
        for j in range(8):
            if x >= m:
                y -= 1
                x = 0
            r, g, b, a = im.getpixel((x, y))
            r = ((r & 254) | (1 if (c & (1 << j)) > 0 else 0))
            nw[x, y] = (r, g, b, a)
            x += 1
    return image

def decript_image(imagename):
    im = Img.open(imagename)
    im = im.convert('RGBA')

    m, n = im.size

    len = 0
    txt = ''
    for i in range(8):
        r, g, b, a = im.getpixel((i, n - 1))
        len = len | ((r & 1) << i)

    x = 8
    y = n - 1
    for i in range(len):
        c = 0
        for j in range(8):
            if x >= m:
                y -= 1
                x = 0
            if y < 0: break
            r, g, b, a = im.getpixel((x, y))
            c = c | ((r & 1) << j)
            x += 1
        if c > 128:
            c = c + 848
            txt += chr(c)
    return txt

class WorkWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Стеганографія методом LSB")

        nb = ttk.Notebook(master)
        nb.pack(fill='both', expand='yes')

        encrypt_frame = self.encrypt_frame()
        decrypt_frame = self.decrypt_frame()

        nb.add(encrypt_frame, text='Вбудувати повідомлення')
        nb.add(decrypt_frame, text='Добути повідомлення')

    def input_entry_double_click(self, event):
        file_name = fd.askopenfilename(filetypes=[("bmp files", "*.bmp")], initialdir="/", title='Виберіть зображення для вбудовування')
        self.enc_input_file.set(file_name)

    def input_entry_double_click2(self, event):
        file_name = fd.askopenfilename(filetypes=[("bmp files", "*.bmp")], initialdir="/", title=('Виберіть зображення для видовування'))
        self.dec_input_file.set(file_name)

    def output_entry_double_click(self, event):
        file_name = fd.asksaveasfilename(filetypes=[("bmp files", "*.bmp")], initialdir="/", title='Виберіть зображення для збереження', defaultextension="*.*")
        self.enc_output_file.set(file_name)

    def process_file(self):
        input_file = self.enc_input_file.get().strip()
        output_file = self.enc_output_file.get().strip()
        text = self.enc_text.get("1.0", END).strip()
        if len(input_file) == 0 or len(output_file) == 0 or len(text) == 0:
            mb.showerror("Помилка", "Необхідно задати вихідний файл, кінцевий файл і текст")
            return
        if len(text) > 255:
            answer = mb.askyesno(title="Текст", message="Текст занадто довгий, скоротити автоматично?")
            if answer == True:
                text = text[:255]
            else:
                return
        image = encript_image(input_file, text)
        image.save(output_file)
        mb.showinfo("Файл збережено", "Файл збережено")

    def process_file2(self):
        self.dec_text.delete('1.0', END)
        input_file = self.dec_input_file.get().strip()
        text = ""
        if len(input_file) == 0:
            mb.showerror("Помилка", "Потрібно задати вихідний файл")
        # отримуємо текст з файла і виводимо його в текстове поле
        self.dec_text.insert(END, decript_image(input_file))
        mb.showinfo("Текст отримано","Текст отримано")

    def encrypt_frame(self):
        enc_frame = Frame(self.master)
        Label(enc_frame, text="Зображення для вбудовування", anchor='w').pack(fill='both', side='top')
        self.enc_input_file = StringVar()
        input_entry = Entry(enc_frame, textvariable=self.enc_input_file)
        input_entry.pack(fill='both', padx = 5)
        input_entry.bind('<Double-1>', self.input_entry_double_click)
        Label(enc_frame, text="Зашифроване зображення", anchor='w').pack(fill='both', side='top')
        self.enc_output_file = StringVar()
        output_entry = Entry(enc_frame, textvariable=self.enc_output_file)
        output_entry.pack(fill='both', padx = 5)
        output_entry.bind('<Double-1>', self.output_entry_double_click)
        text_frame = Frame(enc_frame)
        Label(text_frame, text="Введіть текст, не більше 255 символів з пропусками", anchor='w').pack(fill='both')
        self.enc_text = Text(text_frame, width=25, height=7, wrap=WORD)
        self.enc_text.pack(fill='x', side='top', expand='yes', padx=5)
        text_frame.pack(fill='both', side='top', pady=10)
        Button(enc_frame, text="Вбудувати", command=self.process_file).pack(fill='both', side='bottom', padx=5, pady=5)
        return enc_frame

    def decrypt_frame(self):
        enc_frame = Frame(self.master)
        Label(enc_frame, text="Зображення для видобування", anchor='w').pack(fill='both', side='top')
        self.dec_input_file = StringVar()
        input_entry = Entry(enc_frame, textvariable=self.dec_input_file)
        input_entry.pack(fill='both', padx = 5)
        input_entry.bind('<Double-1>', self.input_entry_double_click2)
        text_frame = Frame(enc_frame)
        Label(text_frame, text="Добутий текст", anchor='w').pack(fill='both')
        self.dec_text = Text(text_frame, width=25, height=9, wrap=WORD)
        self.dec_text.pack(fill='x', side='top', expand='yes', padx=5)
        text_frame.pack(fill='both', side='top', pady=10)
        Button(enc_frame, text="Добути", command=self.process_file2).pack(fill='both', side='bottom', padx=5, pady=5)
        return enc_frame





root = Tk()
root.geometry('600x300')
root.resizable(False, False)
mainmenu = Menu(root) 
root.config(menu=mainmenu)
 
filemenu = Menu(mainmenu, tearoff=0)
filemenu.add_command(label="Вихід", command=root.destroy)
 
helpmenu = Menu(mainmenu, tearoff=0)
helpmenu.add_command(label="Допомога", command=lambda: mb.showinfo("Допомога",
"""
Програма призначена для приховування інформації
в зображенні методом LSB.
В головному вікні програми є дві вкладки,
перша з яких призначена для вбудовування тексту,
друга для його добування. Файли для обробки
вказуються в текстових полях. Для цього можна
вписати шлях до файла, або застосувати подвійне
клацання для появи діалогового вікна.
Для вбудовування тексту потрібно вказати вихідний
файл, файл для збереження результату і текст.
Для добування повідомлення вказується лише вихідний
файл.
"""))

def authorInf():
    author = Toplevel()
    author.geometry("800x600")
    author.title("Про автора")
    author.resizable(0,0)
    canvas = Canvas(author,width=800, height=600)
    image = ImageTk.PhotoImage(Image.open("D:\LSB\source\\bgwall.png"))
    canvas.create_image(0,0,anchor = NW,image = image)
    canvas.pack()
    author.mainloop()

def taskInfo():
    taskinf = Toplevel()
    taskinf.geometry("700x500")
    taskinf.title("Завдання")
    taskinf.resizable(0,0)
    canvas = Canvas(taskinf,width=800, height=600)
    image = ImageTk.PhotoImage(Image.open("D:\LSB\source\\task.png"))
    canvas.create_image(0,0,anchor = NW,image = image)
    canvas.pack()
    taskinf.mainloop()



mainmenu.add_cascade(label="Файл", menu=filemenu)
mainmenu.add_cascade(label="Довідка", menu=helpmenu)
mainmenu.add_cascade(label= "Про автора", command = authorInf)
mainmenu.add_cascade(label= "Завдання", command = taskInfo)
 

WorkWindow(root)
root.mainloop()
