import pandas as pd
import tkinter as tk
from tkinter import filedialog, ttk

# Funkcja do wczytywania pliku CSV
def load_csv():
    filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if filepath:
        try:
            df = pd.read_csv(filepath)  # Wczytanie pliku CSV do DataFrame Pandas
            display_data(df)            # Wyświetlenie danych
        except Exception as e:
            print(f"Error: {e}")

# Funkcja do wyświetlania danych w tabeli
def display_data(df):
    # Czyszczenie poprzednich danych z tabeli
    for row in table.get_children():
        table.delete(row)

    # Ustawienie nagłówków kolumn na podstawie CSV
    table["columns"] = list(df.columns)
    table["show"] = "headings"

    # Dodanie nagłówków kolumn do tabeli
    for col in df.columns:
        table.heading(col, text=col)
        table.column(col, width=100, anchor="center")  # Dopasowanie szerokości kolumn

    # Dodanie danych z CSV do tabeli
    for index, row in df.iterrows():
        table.insert("", "end", values=list(row))

# Utworzenie okna aplikacji
root = tk.Tk()
root.title("CSV Viewer")
root.geometry("800x600")

# Przycisk do wczytywania pliku CSV
load_button = tk.Button(root, text="Load CSV", command=load_csv)
load_button.pack(pady=10)

# Frame dla tabeli i pasków przewijania
frame = tk.Frame(root)
frame.pack(fill="both", expand=True)

# Tworzenie tabeli (Treeview)
table = ttk.Treeview(frame, show="headings")

# Pionowy pasek przewijania
vsb = ttk.Scrollbar(frame, orient="vertical", command=table.yview)
vsb.pack(side="right", fill="y")
table.configure(yscrollcommand=vsb.set)

# Poziomy pasek przewijania
hsb = ttk.Scrollbar(frame, orient="horizontal", command=table.xview)
hsb.pack(side="bottom", fill="x")
table.configure(xscrollcommand=hsb.set)

# Umieszczamy tabelę w ramce
table.pack(fill="both", expand=True)

# Start aplikacji
root.mainloop()
