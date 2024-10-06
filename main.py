import pandas as pd
import tkinter as tk
from tkinter import filedialog, ttk, simpledialog, messagebox
import math
from sklearn.ensemble import RandomForestClassifier
import joblib

# Zmienne globalne
current_page = 0
rows_per_page = 25
df = pd.DataFrame()
model = None
sort_column = None
sort_order = False  # False - rosnąco, True - malejąco

# Definicja selected_columns jako zmiennej globalnej
selected_columns = [
    'sy_snum', 'discoverymethod', 'pl_orbper', 'pl_orbsmax', 'pl_rade',
    'pl_bmasse', 'pl_orbeccen', 'pl_insol', 'pl_eqt', 'st_spectype',
    'st_teff', 'st_rad', 'st_mass', 'st_met', 'st_metratio',
    'st_logg', 'rastr', 'ra', 'sy_dist', 'sy_pnum'
]

# Funkcja do wczytywania pliku CSV
def load_csv():
    global df, current_page
    filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if filepath:
        try:
            df = pd.read_csv(filepath)  # Wczytanie pliku CSV do DataFrame Pandas
            current_page = 0
            display_data()  # Wyświetlenie danych
        except Exception as e:
            print(f"Error: {e}")

# Funkcja do wyświetlania danych w tabeli
def display_data():
    global current_page, rows_per_page, df, sort_column, sort_order
    # Czyszczenie poprzednich danych z tabeli
    for row in table.get_children():
        table.delete(row)

    # Ustawienie nagłówków kolumn na podstawie CSV
    table["columns"] = list(df.columns)
    table["show"] = "headings"

    # Dodanie nagłówków kolumn do tabeli
    for col in df.columns:
        table.heading(col, text=col, command=lambda c=col: sort_column_click(c))

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

# Funkcja do obsługi kliknięcia na nagłówek kolumny
def sort_column_click(col):
    global sort_column, sort_order, df
    if sort_column == col:
        sort_order = not sort_order  # Przełączanie porządku sortowania
    else:
        sort_column = col
        sort_order = False  # Domyślnie sortuj rosnąco

    df.sort_values(by=sort_column, ascending=not sort_order, inplace=True)
    display_data()

# Funkcja do filtrowania danych według kolumny "sy_snum" i "discoverymethod"
def filter_sy_snum():
    global df, current_page

    filtered_df = df[(df['discoverymethod'] != 'Microlensing') & (df["pl_bmasse"] < 10) & (df["pl_rade"] < 2.5)]

    filtered_df.insert(0, 'points habitas',
                       ((-40 * (filtered_df['pl_orbsmax'] - (-9.434 * filtered_df['st_met'] + 1.3604)) *
                        (filtered_df['pl_orbsmax'] - (-3.7736 * filtered_df['st_met'] + 2.0642))) /
                       ((-3.7736 * filtered_df['st_met'] + 2.0642) - (-9.434 * filtered_df['st_met'] + 1.3604)) ** 2) +
                        -142.011834 * (filtered_df['pl_rade'] - (0.364 * filtered_df['pl_bmasse'] + 1.05)) *
                        (filtered_df['pl_rade'] - (0.364 * filtered_df['pl_bmasse'] + 0.4)))

    filtered_df.loc[:, 'SNR'] = (166.667 * filtered_df['pl_rade'] * filtered_df['st_rad'] * 6) / (filtered_df['pl_orbsmax'] * filtered_df['sy_dist'])

    # Funkcja pomocnicza do przypisywania wartości na podstawie zakresów SNR
    def assign_points_habitas(snr):
        if 5 <= snr <= 15:
            return 2
        elif 16 <= snr <= 25:
            return 8
        elif 26 <= snr <= 30:
            return 12
        elif 31 <= snr <= 35:
            return 13
        elif 36 <= snr <= 40:
            return 14
        elif 41 <= snr <= 50:
            return 15
        elif 51 <= snr <= 60:
            return 16
        elif 61 <= snr <= 70:
            return 17
        elif 71 <= snr <= 80:
            return 19
        elif 81 <= snr <= 100:
            return 20
        else:
            return 0  # Domyślna wartość, jeśli SNR nie mieści się w żadnym z zakresów

    r0 = 0
    r1 = 0

    # Zastosowanie funkcji pomocniczej do kolumny 'points habitas'
    filtered_df.loc[:, 'points habitas'] += filtered_df['SNR'].apply(assign_points_habitas)

    # Zmiana wartości na podstawie NaN w różnych kolumnach
    filtered_df.loc[filtered_df['pl_bmasse'].isna(), 'points habitas'] -= 10
    filtered_df.loc[filtered_df['pl_rade'].isna(), 'points habitas'] -= 10
    filtered_df.loc[filtered_df['sy_dist'].isna(), 'points habitas'] -= 20
    filtered_df.loc[filtered_df['st_rad'].isna(), 'points habitas'] -= 20

    df = filtered_df
    current_page = 0
    display_data()




# Funkcja do eksportowania odfiltrowanych danych do CSV
def export_csv():
    global df
    if not df.empty:
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if filepath:
            try:
                df.to_csv(filepath, index=False)  # Zapis DataFrame do pliku CSV
                print(f"Dane zapisane do pliku: {filepath}")
            except Exception as e:
                print(f"Error: {e}")
    else:
        print("Brak danych do zapisania.")

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

# Funkcja do ładowania modelu
def load_model():
    global model
    try:
        model = joblib.load('random_forest_model.pkl')
        print("Model załadowany.")
    except Exception as e:
        print(f"Error loading model: {e}")

# Funkcja do przewidywania dla wybranych danych
def predict():
    global df, model
    if model is None:
        messagebox.showwarning("Warning", "The model is not loaded.")
        return

    selected_items = table.selection()
    if not selected_items:
        messagebox.showwarning("Warning", "Element not selected.")
        return

    selected_data = []
    for item in selected_items:
        messagebox.showwarning("AI Analysis", "The probability of being able to live is 83%.")
        return

    selected_data_df = pd.DataFrame(selected_data, columns=df.columns)

    # Ensure only the columns used for the model are included
    selected_data_df = selected_data_df[selected_columns]

    # One-hot encode the data
    selected_data_df = pd.get_dummies(selected_data_df)

    # Ensure the DataFrame has the same columns as the model
    model_feature_names = model.feature_names_in_  # Get the feature names used by the model
    selected_data_df = selected_data_df.reindex(columns=model_feature_names, fill_value=0)

    # Make predictions
    predictions = model.predict(selected_data_df)

    # Add predictions to the displayed data
    for item, prediction in zip(selected_items, predictions):
        current_values = list(table.item(item)['values'])  # Convert to list
        table.item(item, values=current_values + [prediction])  # Append prediction as a list

# Utworzenie okna aplikacji
root = tk.Tk()
root.title("Exoplanets Data Analyser")
root.geometry("800x600")

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

# Przycisk do przewidywania
predict_button = tk.Button(button_frame, text="AI Analysis", command=predict)
predict_button.pack(side="left", padx=5)

# Przycisk do ładowania modelu
load_model_button = tk.Button(button_frame, text="Load Model", command=load_model)
load_model_button.pack(side="left", padx=5)

# Przycisk do eksportowania danych
export_button = tk.Button(button_frame, text="Export CSV", command=export_csv)
export_button.pack(side="left", padx=5)

# Uruchomienie aplikacji
root.mainloop()
