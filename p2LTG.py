#%%
# PRESENT TO SIR JEFF
# IT READS THE UPDATED CSV GOING TO DATAFRAME PROPERLY
# IF THE PROGRAM RESTARTED THE LAST OOT COUNTING MEMORY WILL BE SAVED
# IT DOES NOT READ THE OLD ENTRY, IT DOES READ ONLY A NEW ROW ENTRY BASE ON THE NEW DATE AND TIME
# COUNTS OOT AND IT
# IF THE TKINTER GUI ACCIDENTALLY EXITED IT WILL READ THE PREVIOUS COUNT BEFORE IT WAS TURNED OFF


# ERROR:
# NEED TO CLICK THE STOP BUTTON TWICE (RUN p2LTG_PBI.py INSTEAD)


import json
import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import messagebox
import os
import time
import threading

# File Paths
# DATA_FILE = r"\\192.168.2.19\ai_team\AI Program\Outputs\CompiledPiMachine\CompiledPIMachine.csv"    #Carls PIMACHINE DATABASE
# DATA_FILE = r"\\192.168.2.19\ai_team\INDIVIDUAL FOLDER\June-San\p2LTG\p2LTG_TransferData\CompiledPIMachine.csv"
DATA_FILE = r"\\192.168.2.19\ai_team\INDIVIDUAL FOLDER\June-San\p2LTG\p2LTG_TransferData\CompiledPIMachine.csv"       #FALSE EXAMPLE     
# DATA_FILE = r"\\192.168.2.19\ai_team\INDIVIDUAL FOLDER\June-San\p2LTG\p2LTG_TransferData\CompiledPIMachine.csv"
UCL_LCL_FILE = r"\\192.168.2.19\ai_team\INDIVIDUAL FOLDER\June-San\p2LTG\p2LTG_TransferData\UCL_LCL.xlsx"
COUNT_FILE = "previous_counts.json"

# pd.set_option('display.max_columns', None)      #ACTIVATE THIS WHEN YOU WANT TO VIEW THE WHOLE COLUMNS
# pd.set_option('display.max_rows', None)         #ACTIVATE THIS WHEN YOU WANT TO VIEW THE WHOLE ROWS

remarks_columns = []
labels = {}
count_list = {}
compiledFrame = None
last_row = None  # Track the previous last row entry
last_timestamp = None  # Ensure proper tracking of file updates

# Function to check file modification time
def get_file_timestamp(file_path):
    return os.path.getmtime(file_path) if os.path.exists(file_path) else None

# Load data and detect only new row entries
def load_data():
    global compiledFrame, remarks_columns, last_row

    if not os.path.exists(DATA_FILE):
        print(f"Error: Cannot access file {DATA_FILE}")
        return False

    try:
        df = pd.read_csv(DATA_FILE, encoding="latin1", low_memory=False)

        if df.empty:
            print("Warning: CSV file is empty. Skipping update.")
            return False

        uclLclFile = pd.read_excel(UCL_LCL_FILE, sheet_name="Sheet1")

        # Filter unwanted model codes
        df = df[~df["MODEL CODE"].isin(["60CAT0203M"])]

        # Create UCL & LCL mapping
        ucl_VOLTAGEMAX = uclLclFile.set_index("MODEL CODE")["VOLTAGE MAX (V) UCL"].to_dict()
        lcl_VOLTAGEMAX = uclLclFile.set_index("MODEL CODE")["VOLTAGE MAX (V) LCL"].to_dict()

        ucl_WATTAGEMAX = uclLclFile.set_index("MODEL CODE")["WATTAGE MAX (W) UCL"].to_dict()
        lcl_WATTAGEMAX = uclLclFile.set_index("MODEL CODE")["WATTAGE MAX (W) LCL"].to_dict()

        ucl_CLOSEDPRESSURE_MAX = uclLclFile.set_index("MODEL CODE")["CLOSED PRESSURE_MAX (kPa) UCL"].to_dict()
        lcl_CLOSEDPRESSURE_MAX = uclLclFile.set_index("MODEL CODE")["CLOSED PRESSURE_MAX (kPa) LCL"].to_dict()

        ucl_VOLTAGEMiddle = uclLclFile.set_index("MODEL CODE")["VOLTAGE Middle (V) UCL"].to_dict()
        lcl_VOLTAGEMiddle = uclLclFile.set_index("MODEL CODE")["VOLTAGE Middle (V) LCL"].to_dict()

        ucl_WATTAGEMiddle = uclLclFile.set_index("MODEL CODE")["WATTAGE Middle (W) UCL"].to_dict()
        lcl_WATTAGEMiddle = uclLclFile.set_index("MODEL CODE")["WATTAGE Middle (W) LCL"].to_dict()

        ucl_AMPERAGEMiddle = uclLclFile.set_index("MODEL CODE")["AMPERAGE Middle (A) UCL"].to_dict()
        lcl_AMPERAGEMiddle = uclLclFile.set_index("MODEL CODE")["AMPERAGE Middle (A) LCL"].to_dict()

        ucl_CLOSEDPRESSUREMiddle = uclLclFile.set_index("MODEL CODE")["CLOSED PRESSURE Middle (kPa) UCL"].to_dict()
        lcl_CLOSEDPRESSUREMiddle = uclLclFile.set_index("MODEL CODE")["CLOSED PRESSURE Middle (kPa) LCL"].to_dict()

        ucl_VOLTAGEMIN = uclLclFile.set_index("MODEL CODE")["VOLTAGE MIN (V) UCL"].to_dict()
        lcl_VOLTAGEMIN = uclLclFile.set_index("MODEL CODE")["VOLTAGE MIN (V) LCL"].to_dict()

        ucl_WATTAGEMIN = uclLclFile.set_index("MODEL CODE")["WATTAGE MIN (W) UCL"].to_dict()
        lcl_WATTAGEMIN = uclLclFile.set_index("MODEL CODE")["WATTAGE MIN (W) LCL"].to_dict()

        ucl_CLOSEDPRESSUREMIN = uclLclFile.set_index("MODEL CODE")["CLOSED PRESSURE MIN (kPa) UCL"].to_dict()
        lcl_CLOSEDPRESSUREMIN = uclLclFile.set_index("MODEL CODE")["CLOSED PRESSURE MIN (kPa) LCL"].to_dict()


        # ---------------------------------------------------------------------------------------------------
# Apply mappings with explicit numeric conversion
        df["VOLTAGE MAX (V) UCL"] = pd.to_numeric(df["MODEL CODE"].map(ucl_VOLTAGEMAX), errors='coerce')
        df["VOLTAGE MAX (V) LCL"] = pd.to_numeric(df["MODEL CODE"].map(lcl_VOLTAGEMAX), errors='coerce')
        df["VOLTAGE MAX (V)"] = pd.to_numeric(df["VOLTAGE MAX (V)"], errors='coerce')

        df["WATTAGE MAX (W) UCL"] = pd.to_numeric(df["MODEL CODE"].map(ucl_WATTAGEMAX), errors='coerce')
        df["WATTAGE MAX (W) LCL"] = pd.to_numeric(df["MODEL CODE"].map(lcl_WATTAGEMAX), errors='coerce')
        df["WATTAGE MAX (W)"] = pd.to_numeric(df["WATTAGE MAX (W)"], errors='coerce')

        df["CLOSED PRESSURE_MAX (kPa) UCL"] = pd.to_numeric(df["MODEL CODE"].map(ucl_CLOSEDPRESSURE_MAX), errors='coerce')
        df["CLOSED PRESSURE_MAX (kPa) LCL"] = pd.to_numeric(df["MODEL CODE"].map(lcl_CLOSEDPRESSURE_MAX), errors='coerce')
        df["CLOSED PRESSURE_MAX (kPa)"] = pd.to_numeric(df["CLOSED PRESSURE_MAX (kPa)"], errors='coerce')

        df["VOLTAGE Middle (V) UCL"] = pd.to_numeric(df["MODEL CODE"].map(ucl_VOLTAGEMiddle), errors='coerce')
        df["VOLTAGE Middle (V) LCL"] = pd.to_numeric(df["MODEL CODE"].map(lcl_VOLTAGEMiddle), errors='coerce')
        df["VOLTAGE Middle (V)"] = pd.to_numeric(df["VOLTAGE Middle (V)"], errors='coerce')

        df["WATTAGE Middle (W) UCL"] = pd.to_numeric(df["MODEL CODE"].map(ucl_WATTAGEMiddle), errors='coerce')
        df["WATTAGE Middle (W) LCL"] = pd.to_numeric(df["MODEL CODE"].map(lcl_WATTAGEMiddle), errors='coerce')
        df["WATTAGE Middle (W)"] = pd.to_numeric(df["WATTAGE Middle (W)"], errors='coerce')

        df["AMPERAGE Middle (A) UCL"] = pd.to_numeric(df["MODEL CODE"].map(ucl_AMPERAGEMiddle), errors='coerce')
        df["AMPERAGE Middle (A) LCL"] = pd.to_numeric(df["MODEL CODE"].map(lcl_AMPERAGEMiddle), errors='coerce')
        df["AMPERAGE Middle (A)"] = pd.to_numeric(df["AMPERAGE Middle (A)"], errors='coerce')

        df["CLOSED PRESSURE Middle (kPa) UCL"] = pd.to_numeric(df["MODEL CODE"].map(ucl_CLOSEDPRESSUREMiddle), errors='coerce')
        df["CLOSED PRESSURE Middle (kPa) LCL"] = pd.to_numeric(df["MODEL CODE"].map(lcl_CLOSEDPRESSUREMiddle), errors='coerce')
        df["CLOSED PRESSURE Middle (kPa)"] = pd.to_numeric(df["CLOSED PRESSURE Middle (kPa)"], errors='coerce')

        df["VOLTAGE MIN (V) UCL"] = pd.to_numeric(df["MODEL CODE"].map(ucl_VOLTAGEMIN), errors='coerce')
        df["VOLTAGE MIN (V) LCL"] = pd.to_numeric(df["MODEL CODE"].map(lcl_VOLTAGEMIN), errors='coerce')
        df["VOLTAGE MIN (V)"] = pd.to_numeric(df["VOLTAGE MIN (V)"], errors='coerce')

        df["WATTAGE MIN (W) UCL"] = pd.to_numeric(df["MODEL CODE"].map(ucl_WATTAGEMIN), errors='coerce')
        df["WATTAGE MIN (W) LCL"] = pd.to_numeric(df["MODEL CODE"].map(lcl_WATTAGEMIN), errors='coerce')
        df["WATTAGE MIN (W)"] = pd.to_numeric(df["WATTAGE MIN (W)"], errors='coerce')

        df["CLOSED PRESSURE MIN (kPa) UCL"] = pd.to_numeric(df["MODEL CODE"].map(ucl_CLOSEDPRESSUREMIN), errors='coerce')
        df["CLOSED PRESSURE MIN (kPa) LCL"] = pd.to_numeric(df["MODEL CODE"].map(lcl_CLOSEDPRESSUREMIN), errors='coerce')
        df["CLOSED PRESSURE MIN (kPa)"] = pd.to_numeric(df["CLOSED PRESSURE MIN (kPa)"], errors='coerce')

        # ---------------------------------------------------------------------------------------------------------------- #


# Apply tolerance check
        df["VOLTAGE MAX (V) REMARKS"] = df.apply(
            lambda x: "IN TOLERANCE" if pd.notna(x["VOLTAGE MAX (V) UCL"]) and pd.notna(x["VOLTAGE MAX (V) LCL"]) and
            x["VOLTAGE MAX (V) LCL"] <= x["VOLTAGE MAX (V)"] <= x["VOLTAGE MAX (V) UCL"]
            else "OUT OF TOLERANCE",
            axis=1
        )
        df["WATTAGE MAX (W) REMARKS"] = df.apply(
            lambda x: "IN TOLERANCE" if pd.notna(x["WATTAGE MAX (W) UCL"]) and pd.notna(x["WATTAGE MAX (W) LCL"]) and
            x["WATTAGE MAX (W) LCL"] <= x["WATTAGE MAX (W)"] <= x["WATTAGE MAX (W) UCL"]
            else "OUT OF TOLERANCE",
            axis=1
        )

        df["CLOSED PRESSURE_MAX (kPa) REMARKS"] = df.apply(
            lambda x: "IN TOLERANCE" if pd.notna(x["CLOSED PRESSURE_MAX (kPa) UCL"]) and pd.notna(x["CLOSED PRESSURE_MAX (kPa) LCL"]) and
            x["CLOSED PRESSURE_MAX (kPa) LCL"] <= x["CLOSED PRESSURE_MAX (kPa)"] <= x["CLOSED PRESSURE_MAX (kPa) UCL"]
            else "OUT OF TOLERANCE",
            axis=1
        )

        df["VOLTAGE Middle (V) REMARKS"] = df.apply(
            lambda x: "IN TOLERANCE" if pd.notna(x["VOLTAGE Middle (V) UCL"]) and pd.notna(x["VOLTAGE Middle (V) LCL"]) and
            x["VOLTAGE Middle (V) LCL"] <= x["VOLTAGE Middle (V)"] <= x["VOLTAGE Middle (V) UCL"]
            else "OUT OF TOLERANCE",
            axis=1
        )

        df["WATTAGE Middle (W) REMARKS"] = df.apply(
            lambda x: "IN TOLERANCE" if pd.notna(x["WATTAGE Middle (W) UCL"]) and pd.notna(x["WATTAGE Middle (W) LCL"]) and
            x["WATTAGE Middle (W) LCL"] <= x["WATTAGE Middle (W)"] <= x["WATTAGE Middle (W) UCL"]
            else "OUT OF TOLERANCE",
            axis=1
        )

        df["AMPERAGE Middle (A) REMARKS"] = df.apply(
            lambda x: "IN TOLERANCE" if pd.notna(x["AMPERAGE Middle (A) UCL"]) and pd.notna(x["AMPERAGE Middle (A) LCL"]) and
            x["AMPERAGE Middle (A) LCL"] <= x["AMPERAGE Middle (A)"] <= x["AMPERAGE Middle (A) UCL"]
            else "OUT OF TOLERANCE",
            axis=1
        )

        df["CLOSED PRESSURE Middle (kPa) REMARKS"] = df.apply(
            lambda x: "IN TOLERANCE" if pd.notna(x["CLOSED PRESSURE Middle (kPa) UCL"]) and pd.notna(x["CLOSED PRESSURE Middle (kPa) LCL"]) and
            x["CLOSED PRESSURE Middle (kPa) LCL"] <= x["CLOSED PRESSURE Middle (kPa)"] <= x["CLOSED PRESSURE Middle (kPa) UCL"]
            else "OUT OF TOLERANCE",
            axis=1
        )

        df["VOLTAGE MIN (V) REMARKS"] = df.apply(
            lambda x: "IN TOLERANCE" if pd.notna(x["VOLTAGE MIN (V) UCL"]) and pd.notna(x["VOLTAGE MIN (V) LCL"]) and
            x["VOLTAGE MIN (V) LCL"] <= x["VOLTAGE MIN (V)"] <= x["VOLTAGE MIN (V) UCL"]
            else "OUT OF TOLERANCE",
            axis=1
        )

        df["WATTAGE MIN (W) REMARKS"] = df.apply(
            lambda x: "IN TOLERANCE" if pd.notna(x["WATTAGE MIN (W) UCL"]) and pd.notna(x["WATTAGE MIN (W) LCL"]) and
            x["WATTAGE MIN (W) LCL"] <= x["WATTAGE MIN (W)"] <= x["WATTAGE MIN (W) UCL"]
            else "OUT OF TOLERANCE",
            axis=1
        )

        df["CLOSED PRESSURE MIN (kPa) REMARKS"] = df.apply(
            lambda x: "IN TOLERANCE" if pd.notna(x["CLOSED PRESSURE MIN (kPa) UCL"]) and pd.notna(x["CLOSED PRESSURE MIN (kPa) LCL"]) and
            x["CLOSED PRESSURE MIN (kPa) LCL"] <= x["CLOSED PRESSURE MIN (kPa)"] <= x["CLOSED PRESSURE MIN (kPa) UCL"]
            else "OUT OF TOLERANCE",
            axis=1
        )

# ---------------------------------------------------------------------------------------------------------------- #
 
# Define required columns
        columns = [
            "DATE", "TIME", "MODEL CODE", "S/N", 
            "VOLTAGE MAX (V)", "VOLTAGE MAX (V) UCL", "VOLTAGE MAX (V) LCL", "VOLTAGE MAX (V) REMARKS",
            "WATTAGE MAX (W)", "WATTAGE MAX (W) UCL", "WATTAGE MAX (W) LCL", "WATTAGE MAX (W) REMARKS",
            "CLOSED PRESSURE_MAX (kPa)", "CLOSED PRESSURE_MAX (kPa) UCL", "CLOSED PRESSURE_MAX (kPa) LCL", "CLOSED PRESSURE_MAX (kPa) REMARKS",
            "VOLTAGE Middle (V)", "VOLTAGE Middle (V) UCL", "VOLTAGE Middle (V) LCL", "VOLTAGE Middle (V) REMARKS",
            "WATTAGE Middle (W)", "WATTAGE Middle (W) UCL", "WATTAGE Middle (W) LCL", "WATTAGE Middle (W) REMARKS",
            "AMPERAGE Middle (A)", "AMPERAGE Middle (A) UCL", "AMPERAGE Middle (A) LCL", "AMPERAGE Middle (A) REMARKS",
            "CLOSED PRESSURE Middle (kPa)", "CLOSED PRESSURE Middle (kPa) UCL", "CLOSED PRESSURE Middle (kPa) LCL", "CLOSED PRESSURE Middle (kPa) REMARKS",
            "VOLTAGE MIN (V)", "VOLTAGE MIN (V) UCL", "VOLTAGE MIN (V) LCL", "VOLTAGE MIN (V) REMARKS",
            "WATTAGE MIN (W)", "WATTAGE MIN (W) UCL", "WATTAGE MIN (W) LCL", "WATTAGE MIN (W) REMARKS",
            "CLOSED PRESSURE MIN (kPa)", "CLOSED PRESSURE MIN (kPa) UCL", "CLOSED PRESSURE MIN (kPa) LCL", "CLOSED PRESSURE MIN (kPa) REMARKS"
        ]

        compiledFrame = df[columns]
        remarks_columns = [col for col in compiledFrame.columns if col.endswith("REMARKS")][:10]

        

        return True
    except Exception as e:
        print(f"Error loading data: {e}")
        return False

# Get only the newest row based on DATE & TIME
def get_latest_entries():
    global last_row

    latest_entries = compiledFrame.sort_values(["DATE", "TIME"], ascending=[False, False]).head(1)

    new_last_row = latest_entries.iloc[0]

    if last_row is not None and new_last_row.equals(last_row):
        return pd.DataFrame()  # No new data detected, return empty

    last_row = new_last_row
    return latest_entries

# Reset a specific counter
def reset_counter(column):
    count_list[column] = []
    labels[column].config(text=f"{column}: 0 OUT OF TOLERANCE")
    save_counts()

# Save counts safely by converting int64 to standard int
def save_counts():
    try:
        cleaned_counts = {
            key: [int(value) if isinstance(value, (np.int64, int, float)) else value for value in values]
            for key, values in count_list.items()
        }
        
        with open(COUNT_FILE, "w") as f:
            json.dump(cleaned_counts, f, indent=4)
    except Exception as e:
        print(f"Error saving counts: {e}")

print("No new entries detected. Waiting for updates...CompiledPIMachine.csv")

# Update counts dynamically without exiting Tkinter
def update_counts():
    global compiledFrame

    latest_entries = get_latest_entries()
    if latest_entries.empty:
        # print("No new entries detected. Waiting for updates...")
        root.after(5000, update_counts)
        return

    for column in remarks_columns:
        if column not in count_list:
            count_list[column] = []

        out_of_tolerance_count = latest_entries[column].eq("OUT OF TOLERANCE").sum() if column in latest_entries.columns else 0
        count_list[column].append(out_of_tolerance_count)

        if "IN TOLERANCE" in latest_entries[column].values:
            count_list[column].clear()

        recent_count = sum(count_list[column][-5:])

        labels[column].config(text=f"{column}: {recent_count} OUT OF TOLERANCE")

        if recent_count >= 5:
            messagebox.showwarning("Warning", f"{column} has reached 5 consecutive OUT OF TOLERANCE!")

        save_counts()

    root.after(5000, update_counts)

    # print("Waiting for updates...CompiledPIMachine.csv")

# Monitor file changes and reload data safely
def monitor_file_changes():
    global last_timestamp

    while True:
        try:
            time.sleep(5)  # Check every 5 seconds
            current_timestamp = get_file_timestamp(DATA_FILE)

            if current_timestamp and current_timestamp != last_timestamp:
                print("File CompiledPIMachine.csv updated! Checking for new rows...")
                last_timestamp = current_timestamp
                print("Waiting for updates...CompiledPIMachine.csv")

                if load_data():
                    update_counts()
        except Exception as e:
            print(f"Error in file monitoring: {e}")
        
        

# Start the file monitor in a separate thread
monitor_thread = threading.Thread(target=monitor_file_changes, daemon=True)
monitor_thread.start()

# Tkinter GUI Setup
if load_data():
    root = tk.Tk()
    root.title("Live Out of Tolerance Monitor")

    for column in remarks_columns:
        frame = tk.Frame(root)
        frame.pack(pady=5)

        label_value = tk.Label(frame, text=f"{column}: 0 OUT OF TOLERANCE", font=("Arial", 12))
        label_value.pack()
        labels[column] = label_value

        stop_button = tk.Button(frame, text="STOP", command=lambda col=column: reset_counter(col))
        stop_button.pack()

    root.after(5000, update_counts)
    root.mainloop()
else:
    print("Error: DataFrame not ready, GUI launch aborted.")

# %%
