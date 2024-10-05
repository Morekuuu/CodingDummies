import pandas as pd
import tkinter as tk
from tkinter import filedialog, ttk, simpledialog
import math

# Zmienne globalne
current_page = 0
rows_per_page = 25
df = pd.DataFrame()

# Funkcja do wczytywania pliku CSV
def load_csv():
    global df, current_page
    filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if filepath:
        try:
            df = pd.read_csv(filepath)  # Wczytanie pliku CSV do DataFrame Pandas
            current_page = 0
            display_data()            # Wyświetlenie danych
        except Exception as e:
            print(f"Error: {e}")

# Funkcja do wyświetlania danych w tabeli
def display_data():
    global current_page, rows_per_page, df
    # Czyszczenie poprzednich danych z tabeli
    for row in table.get_children():
        table.delete(row)

    # Ustawienie nagłówków kolumn na podstawie CSV
    table["columns"] = list(df.columns)
    table["show"] = "headings"

    # Dodanie nagłówków kolumn do tabeli
    for col in df.columns:
        table.heading(col, text=col)

    # Obliczenie zakresu wierszy do wyświetlenia
    start_row = current_page * rows_per_page
    end_row = start_row + rows_per_page
    page_data = df.iloc[start_row:end_row]

    # Dodanie danych z CSV do tabeli
    for index, row in page_data.iterrows():
        table.insert("", "end", values=list(row))

    # Aktualizacja informacji o stronie
    total_pages = (len(df) + rows_per_page - 1) // rows_per_page
    page_info_label.config(text=f"Page {current_page + 1} of {total_pages}")

# Funkcja do filtrowania danych według kolumny "sy_snum" i "discoverymethod"
def filter_sy_snum():
    global df, current_page
    filtered_df = df[(df['discoverymethod'] != 'Microlensing') & (df["pl_bmasse"] < 10) & (df["pl_rade"] < 2.5)]

    # Dodanie nowej kolumny z wynikiem mnożenia "pl_rade" i "pl_bmasse"
    filtered_df['SNR'] = (166.667 * filtered_df['pl_rade'] * filtered_df['st_rad'] * 6) / (filtered_df['pl_orbsmax'] * filtered_df['sy_dist'])

    # Filtrowanie wartości SNR większych od 5
    filtered_df = filtered_df[filtered_df['SNR'] > 5]
    filtered_df = filtered_df[filtered_df['pl_rade'] > (0.364*filtered_df['pl_bmasse']+0.45)]
    filtered_df = filtered_df[filtered_df['pl_rade'] < (0.364*filtered_df['pl_bmasse']+1.05)]
    filtered_df = filtered_df[filtered_df['sy_dist'] < (15/filtered_df['pl_orbsmax'])]
    filtered_df = filtered_df[filtered_df['pl_orbsmax'] < (-3.7736 * filtered_df['st_met']+ 2.0642)]
    filtered_df = filtered_df[filtered_df['pl_orbsmax'] > (-9.434 * filtered_df['st_met'] + 1.3604)]
    df = filtered_df
    current_page = 0
    display_data()


# Funkcje do nawigacji między stronami
def next_page():
    global current_page
    if (current_page + 1) * rows_per_page < len(df):
        current_page += 1
        display_data()

def previous_page():
    global current_page
    if current_page > 0:
        current_page -= 1
        display_data()

# Utworzenie okna aplikacji
root = tk.Tk()
root.title("CSV Viewer")
root.geometry("600x400")

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

# Ramka na przyciski nawigacyjne
nav_frame = tk.Frame(root)
nav_frame.pack(pady=10)

# Etykieta z informacją o stronie
page_info_label = tk.Label(nav_frame, text="Page 1 of 1")
page_info_label.pack(side="left", padx=5)

# Przycisk "Previous"
prev_button = tk.Button(nav_frame, text="Previous", command=previous_page)
prev_button.pack(side="left", padx=5)

# Przycisk "Next"
next_button = tk.Button(nav_frame, text="Next", command=next_page)
next_button.pack(side="left", padx=5)

# Ramka na przyciski
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# Przycisk do wczytywania pliku CSV
load_button = tk.Button(button_frame, text="Load CSV", command=load_csv)
load_button.pack(side="left", padx=5)

# Przycisk "Filter sy_snum"
filter_button = tk.Button(button_frame, text="Filter Habitat", command=filter_sy_snum)
filter_button.pack(side="left", padx=5)

# Start aplikacji
root.mainloop()
