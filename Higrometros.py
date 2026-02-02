"""


Instrucciones:

1. Descargar a Icloud los ficheros de los sensores comedor exterior y bomba de achique.
2. Mover a la carpeta de mis ficheros personales en DESKTOP.
3. Ejecutar este script.

Probado con Python 3.3.3

Genera cuatro graficas y las guarda en disco con una marca de tiempo. Guarda también  una copia de los ficheros de entrada.

La gráfica más interesante es la última, donde indica el margen de la temperatura interior de la bomba de achique respecto a la tempertura del punto de rocío.

"""


from pathlib import Path
import sys
import pandas as pd
import matplotlib.pyplot as plt
import shutil
from datetime import date


# Marca de tiempo:

today_str = date.today().strftime("%Y%m%d")

#Ficheros de entrada.

raw_path  = r"C:\Users\REEMMMO\OneDrive - Ericsson\Desktop\MARIANO_PERSONAL\SensoresTemperatura/S4_BombaAchique_Int_data.csv"
raw_path2 = r"C:\Users\REEMMMO\OneDrive - Ericsson\Desktop\MARIANO_PERSONAL\SensoresTemperatura/S2_Comedor_Ext_data.csv"

# Backup ficheros de entrada con marca de tiempo.

dst = r"C:\Users\REEMMMO\OneDrive - Ericsson\Desktop\MARIANO_PERSONAL\SensoresTemperatura/" + today_str   + "_S4_BombaAchique_Int_data.csv"
dst2 = r"C:\Users\REEMMMO\OneDrive - Ericsson\Desktop\MARIANO_PERSONAL\SensoresTemperatura/" + today_str  + "_S2_Comedor_Ext_data.csv"

try:
    shutil.copy(raw_path, dst)  # copy contents and permission bits
    print(f"Copied {raw_path} -> {dst}")
except Exception as e:
    print("Error copying file:", e)

try:
    shutil.copy(raw_path2, dst2)  # copy contents and permission bits
    print(f"Copied {raw_path2} -> {dst2}")
except Exception as e:
    print("Error copying file:", e)


#Lectura de los ficheros de entrada. 

file_path  = Path(raw_path).expanduser()
file_path2 = Path(raw_path2).expanduser()

# Read CSV. Let pandas infer datetime; if the timestamp column name contains weird chars, adjust accordingly.
df  = pd.read_csv(file_path)
df2 = pd.read_csv(file_path2)

ts_col = "Timestamp"

df[ts_col] = pd.to_datetime(df[ts_col], errors="coerce")
if df[ts_col].isna().all():
    print("All timestamps could not be parsed. Check format.", file=sys.stderr)
    sys.exit(1)

df2[ts_col] = pd.to_datetime(df2[ts_col], errors="coerce")
if df2[ts_col].isna().all():
    print("All timestamps could not be parsed. Check format.", file=sys.stderr)
    sys.exit(1)

# Drop rows with NaT in timestamp
df  = df .dropna(subset=[ts_col])
df2 = df2.dropna(subset=[ts_col])

# Set timestamp as index for easier plotting
df = df.set_index(ts_col)

# renombrar la columna de temperatura de df2 (opcional, para claridad)
temp_col = 'Temperature_Celsius(°C)'
hume_col = 'Relative_Humidity(%)'
hume_abs_col = 'Absolute_Humidity(g/m³)'
df2_temp = df2[['Timestamp', temp_col,hume_col,hume_abs_col]].rename(columns={temp_col: f'{temp_col}_Exterior',hume_col: f'{hume_col}_Exterior',hume_abs_col:f'{hume_abs_col}_Exterior'})

df2_temp = df2_temp.set_index(ts_col)


#Poner a cero los segundos para que coincidan las muestras de los dos ficheros. 
df.index       = df      .index.round('min')
df2_temp.index = df2_temp.index.round('min')

# left merge para añadir la columna de df2 a df1 en función de Timestamp
df = df.merge(df2_temp, on='Timestamp', how='left')


df.rename(columns={"Temperature_Celsius(°C)": "Temp Int (ºC)","DPT_Celsius(°C)":"Punto Rocío(ºC)","Temperature_Celsius(°C)_Exterior":"Temp Ext (ºC)"}, inplace=True)

df["Margen (ºC)"] = df["Temp Int (ºC)"] - df["Punto Rocío(ºC)"]


df.dropna(subset=["Temp Ext (ºC)"], how='any', inplace=True)


###############################################################################################################################

# Expected column names (exactly as provided). If your CSV uses slightly different names, adjust here.

cols_to_plot = [
    "Temp Int (ºC)",
    "Punto Rocío(ºC)",
    "Margen (ºC)",
]


# Ensure plotting columns exist; filter to those present
present_cols = [c for c in cols_to_plot if c in df.columns]
if not present_cols:
    print("None of the requested columns were found in the file. Available columns:", df.columns.tolist(), file=sys.stderr)
    sys.exit(1)




# Create plot
plt.style.use("dark_background")
fig, ax1 = plt.subplots(figsize=(12, 6))

colors = ["tab:blue", "tab:orange", "tab:red"]
# We'll plot the first two series on ax1 and the remaining on a twin y-axis if scales differ.
# This approach keeps the plot readable when ranges differ.
if len(present_cols) <= 2:
    for c, color in zip(present_cols, colors):
        ax1.plot(df.index, df[c], label=c, color=color)
    ax1.set_ylabel(", ".join(present_cols))
else:
    # Plot first two on ax1
    for c, color in zip(present_cols[:2], colors):
        ax1.plot(df.index, df[c], label=c, color=color)
    ax1.set_ylabel(" / ".join(present_cols[:2]))

    # Create a secondary axis for the remaining columns
    ax2 = ax1.twinx()
    for c, color in zip(present_cols[2:], colors[2:]):
        ax2.plot(df.index, df[c], label=c, color=color, linestyle="--")
    ax2.set_ylabel(" / ".join(present_cols[2:]))

# Formatting
ax1.set_xlabel("Timestamp")
ax1.set_title("Temperatura interior (ºC) vs Punto de rocío. ")
fig.autofmt_xdate(rotation=35)
# Build a combined legend
lines, labels = ax1.get_legend_handles_labels()
if 'ax2' in locals():
    l2, lab2 = ax2.get_legend_handles_labels()
    lines += l2
    labels += lab2
ax1.legend(lines, labels, loc="upper left", fontsize="small")

plt.tight_layout()
# Save and show
out_file = file_path.with_suffix(".png")
print(out_file)
plt.savefig(today_str + "_" + "Temp_vs_PtoRocio.png", dpi=150)
print(f"Saved plot to {out_file}")




###############################################################################################################################



# Expected column names (exactly as provided). If your CSV uses slightly different names, adjust here.

cols_to_plot = [
    "Temp Int (ºC)",
    "Temp Ext (ºC)",

]


# Ensure plotting columns exist; filter to those present
present_cols = [c for c in cols_to_plot if c in df.columns]
if not present_cols:
    print("None of the requested columns were found in the file. Available columns:", df.columns.tolist(), file=sys.stderr)
    sys.exit(1)


# Create plot
plt.style.use("dark_background")
fig, ax1 = plt.subplots(figsize=(12, 6))

colors = ["tab:blue", "tab:orange", "tab:red"]
# We'll plot the first two series on ax1 and the remaining on a twin y-axis if scales differ.
# This approach keeps the plot readable when ranges differ.
if len(present_cols) <= 2:
    for c, color in zip(present_cols, colors):
        ax1.plot(df.index, df[c], label=c, color=color)
    ax1.set_ylabel(", ".join(present_cols))
else:
    # Plot first two on ax1
    for c, color in zip(present_cols[:2], colors):
        ax1.plot(df.index, df[c], label=c, color=color)
    ax1.set_ylabel(" / ".join(present_cols[:2]))

    # Create a secondary axis for the remaining columns
    ax2 = ax1.twinx()
    for c, color in zip(present_cols[2:], colors[2:]):
        ax2.plot(df.index, df[c], label=c, color=color, linestyle="--")
    ax2.set_ylabel(" / ".join(present_cols[2:]))

# Formatting
ax1.set_xlabel("Timestamp")
ax1.set_title("Temperatura Exterior vs Interior")
fig.autofmt_xdate(rotation=35)
# Build a combined legend
lines, labels = ax1.get_legend_handles_labels()
if 'ax2' in locals():
    l2, lab2 = ax2.get_legend_handles_labels()
    lines += l2
    labels += lab2
ax1.legend(lines, labels, loc="upper left", fontsize="small")

plt.tight_layout()
# Save and show
out_file = file_path.with_suffix(".png")
plt.savefig(today_str + "_" + "Ext_Int.png", dpi=150)
print(f"Saved plot to {out_file}")









###############################################################################################################################





# Calcular estadísticos diarios: min y max (y opcionalmente mean)
daily  = df['Temp Ext (ºC)'].resample('D').agg(['min', 'max', 'mean']).rename(columns={'min':'A_min','max':'A_max','mean':'A_mean'})
daily2 = df['Temp Int (ºC)'].resample('D').agg(['min', 'max', 'mean']).rename(columns={'min':'B_min','max':'B_max','mean':'B_mean'})


# Graficar serie original (opcional: suavizada o por puntos) y las líneas diarias
fig, ax = plt.subplots(figsize=(12,6))

# Si quieres graficar la serie original (cada punto u línea)
#ax.plot(df.index, df['Temp Ext (ºC)'], color='yellow', alpha=0.6, label='Ext')

#ax.plot(df.index, df['Temp Int (ºC)'], color='blue', alpha=0.6, label='Int')


# Líneas de máximo y mínimo diarios (usando los índices de daily)

ax.plot(daily.index, daily['A_mean'], color='red', linestyle='--', linewidth=1.5, label='Temp Ext (ºC) Promedio diario')
ax.plot(daily2.index, daily2['B_mean'], color='blue', linestyle='--', linewidth=1.5, label='Temp Int (ºC) Promedio diario')

# Banda rellena entre min y max diarios
#ax.fill_between(daily.index, daily['A_min'], daily['A_max'], color='gray', alpha=0.2, label='Rango diario (min-max)')

# (Opcional) línea de media diaria
#ax.plot(daily.index, daily['A_mean'], color='red', linestyle='-', linewidth=1.5, label='Media diaria A')

ax.set_xlabel('Timestamp (día)')
ax.set_ylabel('Temp Ext (ºC)')
ax.set_title('Temp Ext (ºC): máximos y mínimos diarios')
ax.legend()
plt.tight_layout()

plt.savefig(today_str + "_" + "TempMean.png", dpi=150)






###############################################################################################################################




# Expected column names (exactly as provided). If your CSV uses slightly different names, adjust here.

cols_to_plot = [
    "Margen (ºC)",

]


# Ensure plotting columns exist; filter to those present
present_cols = [c for c in cols_to_plot if c in df.columns]
if not present_cols:
    print("None of the requested columns were found in the file. Available columns:", df.columns.tolist(), file=sys.stderr)
    sys.exit(1)


# Create plot
plt.style.use("dark_background")
fig, ax1 = plt.subplots(figsize=(12, 6))

colors = ["tab:blue", "tab:orange", "tab:red"]
# We'll plot the first two series on ax1 and the remaining on a twin y-axis if scales differ.
# This approach keeps the plot readable when ranges differ.
if len(present_cols) <= 2:
    for c, color in zip(present_cols, colors):
        ax1.plot(df.index, df[c], label=c, color=color)
    ax1.set_ylabel(", ".join(present_cols))
else:
    # Plot first two on ax1
    for c, color in zip(present_cols[:2], colors):
        ax1.plot(df.index, df[c], label=c, color=color)
    ax1.set_ylabel(" / ".join(present_cols[:2]))

    # Create a secondary axis for the remaining columns
    ax2 = ax1.twinx()
    for c, color in zip(present_cols[2:], colors[2:]):
        ax2.plot(df.index, df[c], label=c, color=color, linestyle="--")
    ax2.set_ylabel(" / ".join(present_cols[2:]))

# Formatting
ax1.set_xlabel("Timestamp")
ax1.set_title("Margen")
fig.autofmt_xdate(rotation=35)
# Build a combined legend
lines, labels = ax1.get_legend_handles_labels()
if 'ax2' in locals():
    l2, lab2 = ax2.get_legend_handles_labels()
    lines += l2
    labels += lab2
ax1.legend(lines, labels, loc="upper left", fontsize="small")

plt.tight_layout()
# Save and show
out_file = file_path.with_suffix(".png")
plt.savefig(today_str + "_" + "Margen.png", dpi=150)
print(f"Saved plot to {out_file}")


###############################################################################################################################




# Expected column names (exactly as provided). If your CSV uses slightly different names, adjust here.

cols_to_plot = [
    'Relative_Humidity(%)',
    'Relative_Humidity(%)_Exterior',

]



# Ensure plotting columns exist; filter to those present
present_cols = [c for c in cols_to_plot if c in df.columns]
if not present_cols:
    print("None of the requested columns were found in the file. Available columns:", df.columns.tolist(), file=sys.stderr)
    sys.exit(1)


# Create plot
plt.style.use("dark_background")
fig, ax1 = plt.subplots(figsize=(12, 6))

colors = ["tab:blue", "tab:orange", "tab:red"]
# We'll plot the first two series on ax1 and the remaining on a twin y-axis if scales differ.
# This approach keeps the plot readable when ranges differ.
if len(present_cols) <= 2:
    for c, color in zip(present_cols, colors):
        ax1.plot(df.index, df[c], label=c, color=color)
    ax1.set_ylabel(", ".join(present_cols))
else:
    # Plot first two on ax1
    for c, color in zip(present_cols[:2], colors):
        ax1.plot(df.index, df[c], label=c, color=color)
    ax1.set_ylabel(" / ".join(present_cols[:2]))

    # Create a secondary axis for the remaining columns
    ax2 = ax1.twinx()
    for c, color in zip(present_cols[2:], colors[2:]):
        ax2.plot(df.index, df[c], label=c, color=color, linestyle="--")
    ax2.set_ylabel(" / ".join(present_cols[2:]))

# Formatting
ax1.set_xlabel("Timestamp")
ax1.set_title("Humedad Exterior vs Interior")
fig.autofmt_xdate(rotation=35)
# Build a combined legend
lines, labels = ax1.get_legend_handles_labels()
if 'ax2' in locals():
    l2, lab2 = ax2.get_legend_handles_labels()
    lines += l2
    labels += lab2
ax1.legend(lines, labels, loc="upper left", fontsize="small")

plt.tight_layout()
# Save and show
out_file = file_path.with_suffix(".png")
plt.savefig(today_str + "_" + "Humedad Ext_Int.png", dpi=150)
print(f"Saved plot to {out_file}")







# Expected column names (exactly as provided). If your CSV uses slightly different names, adjust here.

cols_to_plot = [
    'Absolute_Humidity(g/m³)',
    'Absolute_Humidity(g/m³)_Exterior',

]



# Ensure plotting columns exist; filter to those present
present_cols = [c for c in cols_to_plot if c in df.columns]
if not present_cols:
    print("None of the requested columns were found in the file. Available columns:", df.columns.tolist(), file=sys.stderr)
    sys.exit(1)


# Create plot
plt.style.use("dark_background")
fig, ax1 = plt.subplots(figsize=(12, 6))

colors = ["tab:blue", "tab:orange", "tab:red"]
# We'll plot the first two series on ax1 and the remaining on a twin y-axis if scales differ.
# This approach keeps the plot readable when ranges differ.
if len(present_cols) <= 2:
    for c, color in zip(present_cols, colors):
        ax1.plot(df.index, df[c], label=c, color=color)
    ax1.set_ylabel(", ".join(present_cols))
else:
    # Plot first two on ax1
    for c, color in zip(present_cols[:2], colors):
        ax1.plot(df.index, df[c], label=c, color=color)
    ax1.set_ylabel(" / ".join(present_cols[:2]))

    # Create a secondary axis for the remaining columns
    ax2 = ax1.twinx()
    for c, color in zip(present_cols[2:], colors[2:]):
        ax2.plot(df.index, df[c], label=c, color=color, linestyle="--")
    ax2.set_ylabel(" / ".join(present_cols[2:]))

# Formatting
ax1.set_xlabel("Timestamp")
ax1.set_title("Humedad Absoluta Exterior vs Interior")
fig.autofmt_xdate(rotation=35)
# Build a combined legend
lines, labels = ax1.get_legend_handles_labels()
if 'ax2' in locals():
    l2, lab2 = ax2.get_legend_handles_labels()
    lines += l2
    labels += lab2
ax1.legend(lines, labels, loc="upper left", fontsize="small")

plt.tight_layout()
# Save and show
out_file = file_path.with_suffix(".png")
plt.savefig(today_str + "_" + "HumedadAbs Int Ext.png", dpi=150)
print(f"Saved plot to {out_file}")





plt.show()








    
