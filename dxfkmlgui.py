import tkinter as tk
from tkinter import filedialog, messagebox
from functools import partial
import ezdxf
import simplekml
from pyproj import Transformer

def dxf_to_kml(input_file, output_file):
    try:
        # Read the DXF file
        doc = ezdxf.readfile(input_file)

        # Create a KML object
        kml = simplekml.Kml()

        # Define the coordinate system transformation
        transformer = Transformer.from_crs("EPSG:32646", "EPSG:4326", always_xy=True)

        # Iterate through each entity in the DXF file
        for entity in doc.modelspace().query('LINE CIRCLE POLYLINE LWPOLYLINE'):
            if entity.dxftype() == 'LINE':
                # Convert LINE entity to KML LineString
                line = kml.newlinestring(name='Line')
                line.coords = [(point[0], point[1], 0) for point in transformer.itransform([(entity.dxf.start[0], entity.dxf.start[1], 0)])]
                line.altitudemode = simplekml.AltitudeMode.relativetoground
            elif entity.dxftype() == 'CIRCLE':
                # Convert CIRCLE entity to KML Point
                circle = kml.newpoint(name='Circle')
                circle.coords = [(point[0], point[1], 0) for point in transformer.itransform([(entity.dxf.center[0], entity.dxf.center[1], 0)])]
                circle.altitudemode = simplekml.AltitudeMode.relativetoground
            elif entity.dxftype() in ('POLYLINE', 'LWPOLYLINE'):
                # Convert POLYLINE or LWPOLYLINE entity to KML LineString
                polyline = kml.newlinestring(name='Polyline')
                polyline.coords = [(point[0], point[1], 0) for point in transformer.itransform([(vertex[0], vertex[1], 0) for vertex in entity.get_points()])]
                polyline.altitudemode = simplekml.AltitudeMode.relativetoground

        # Save the KML file
        kml.save(output_file)
        messagebox.showinfo("Conversion Complete", "DXF to KML conversion successful.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def browse_input_file(entry):
    file_path = filedialog.askopenfilename(filetypes=[("DXF Files", "*.dxf")])
    entry.delete(0, tk.END)
    entry.insert(tk.END, file_path)

def browse_output_file(entry):
    file_path = filedialog.asksaveasfilename(defaultextension=".kml", filetypes=[("KML Files", "*.kml")])
    entry.delete(0, tk.END)
    entry.insert(tk.END, file_path)

def convert_dxf_to_kml(input_file, output_file):
    if input_file and output_file:
        dxf_to_kml(input_file, output_file)
    else:
        messagebox.showerror("Error", "Please select input and output files.")

def create_gui():
    window = tk.Tk()
    window.title("DXF to KML Converter")

    input_file_label = tk.Label(window, text="Input DXF File:")
    input_file_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)

    input_file_entry = tk.Entry(window, width=50)
    input_file_entry.grid(row=0, column=1, padx=5, pady=5)

    input_file_button = tk.Button(window, text="Browse", command=partial(browse_input_file, input_file_entry))
    input_file_button.grid(row=0, column=2, padx=5, pady=5)

    output_file_label = tk.Label(window, text="Output KML File:")
    output_file_label.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)

    output_file_entry = tk.Entry(window, width=50)
    output_file_entry.grid(row=1, column=1, padx=5, pady=5)

    output_file_button = tk.Button(window, text="Browse", command=partial(browse_output_file, output_file_entry))
    output_file_button.grid(row=1, column=2, padx=5, pady=5)

    convert_button = tk.Button(window, text="Convert", command=partial(convert_dxf_to_kml, input_file_entry.get(), output_file_entry.get()))
    convert_button = tk.Button(window, text="Convert", command=lambda: convert_dxf_to_kml(input_file_entry.get(), output_file_entry.get()))
    convert_button.grid(row=2, column=1, padx=5, pady=10)

    window.mainloop()

# Run the GUI
create_gui()
