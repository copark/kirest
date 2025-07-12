import tkinter as tk
from tkinter import messagebox
from datetime import datetime

from config import *

class Util:
    def today_date():
        today = datetime.today()
        return today.strftime('%Y%m%d')

    def today():
        today = datetime.today()
        return today.strftime('%Y%m%d%H%M%S')
    
    
    def strip_leading_zeros(s):
        try:
            number = int(s)
            return f"{number:,}"
        except (ValueError, TypeError):
            return ""        

    def remove_commas(s):
        try:
            return str(s).replace(",", "")
        except Exception:
            return ""
        


class UxUtil:
    @staticmethod
    def init_label(parent, text):
        return tk.Label(parent, text=text, font=(DEFAULT_FONT, DEFAULT_FONT_SIZE), 
                        anchor=tk.W,justify=tk.LEFT).pack(padx=10, pady=10, anchor=tk.W)

    
    @staticmethod
    def init_label_entry(parent, text, row, textvariable, state=tk.NORMAL):
        label = tk.Label(parent, text=text, font=(DEFAULT_FONT, DEFAULT_FONT_SIZE))
        label.grid(row=row, column=0, padx=5)
        entry = tk.Entry(parent, state=state, textvariable=textvariable, font=(DEFAULT_FONT, DEFAULT_FONT_SIZE), width=40)
        entry.grid(row=row, column=1, padx=5)
        return label, entry


    @staticmethod
    def show_info(message):
        messagebox.showinfo('Info', message)


    def show_warning(message):
        messagebox.showwarning('Error', message)


    def show_confirm(title, message):
        return messagebox.askyesno(title, message)



        


