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

    # Dodanie danych z CSV do tabeli
    for index, row in df.iterrows():
        table.insert("", "end", values=list(row))

# Pusta funkcja dla przycisku "Filter Habitat"
def filter_habitat():
    pass

# Utworzenie okna aplikacji
root = tk.Tk()
root.title("CSV Viewer")
root.geometry("600x400")

# Ramka na przyciski
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# Przycisk do wczytywania pliku CSV
load_button = tk.Button(button_frame, text="Load CSV", command=load_csv)
load_button.pack(side="left", padx=5)

# Przycisk "Filter Habitat"
filter_button = tk.Button(button_frame, text="Filter Habitat", command=filter_habitat)
filter_button.pack(side="left", padx=5)

# Ramka na tabelę i scrollbary
frame = tk.Frame(root)
frame.pack(expand=True, fill="both")

# Tabela do wyświetlania danych
table = ttk.Treeview(frame)

# Pionowy scrollbar
vsb = ttk.Scrollbar(frame, orient="vertical", command=table.yview)
vsb.pack(side="right", fill="y")

# Poziomy scrollbar
hsb = ttk.Scrollbar(frame, orient="horizontal", command=table.xview)
hsb.pack(side="bottom", fill="x")

# Powiązanie scrollbara z tabelą
table.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
table.pack(expand=True, fill="both")

# Start aplikacji
root.mainloop()
