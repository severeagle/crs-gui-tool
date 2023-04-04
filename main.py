import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import pandas as pd
import geopandas as gpd
import shapely


def transform_data(df,input_cols, output_cols):
    df['coords'] = df.apply(
        lambda row: shapely.geometry.Point(row[input_cols[0]], row[input_cols[1]])
        if pd.notna(row['E (ETRS-TM35FIN)']) and pd.notna(row['N (ETRS-TM35FIN)']) else None,
        axis=1
    )
    gdf = gpd.GeoDataFrame(df, geometry='coords').set_crs('epsg:3067')
    gdf = gdf.to_crs('epsg:4326')
    gdf[output_cols[0]] = gdf.geometry.y
    gdf[output_cols[1]] = gdf.geometry.x
    gdf = gdf.drop('coords',axis=1)
    return gdf

class CRSTransformApp(tk.Tk):
    def __init__(self) -> None:
        super(CRSTransformApp, self).__init__()
        self.title("Scrollable Radio Buttons")
        self.maxsize(500,500)
        self.minsize(500,500)

        self.upper_frame = tk.Frame(self, bg='red')
        filedialog_button = tk.Button(self.upper_frame, text='Select File', command=self.open_file_dialog).pack(side='left')
        header_label = tk.Label(self.upper_frame, text="Header Row:").pack(side='left')
        self.header_value = tk.Entry(self.upper_frame, width=3)
        self.header_value.insert(0, 1)#.pack(side='left')
        self.header_value.pack(side='left')
        self.upper_frame.pack()

        # Create a canvas and scrollbar
        self.canvas = tk.Canvas(self, width=300, height=200)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        # Configure canvas and scrollbar
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Lowerframe
        self.lower_frame = tk.Frame(self, bg='blue', width=100)
        self.run_button = tk.Button(self.lower_frame, text="Run", command=self.run_pipeline, disabledforeground='white')
        self.run_button.configure(state="disabled")
        self.run_button.pack()
        self.lower_frame.pack(side='bottom')

    def run_pipeline(self):
        try:
            geom_cols = [self.check_var_long.get(),self.check_var_lat.get()]
            transform_cols = [x+'_transform' for x in geom_cols]
            gdf = transform_data(self.df,geom_cols,transform_cols)
            gdf.to_excel("valmis.xlsx", index=False)
            #self.scrollable_frame.delete("all")
        except:
            tk.messagebox.showinfo(message="Failed, try again...")


        
    def open_file_dialog(self):
        filepath = filedialog.askopenfilename()
        file_extention = filepath.split('.')[-1]
        if file_extention in ['xls','xlsx','csv']:
            try:
                header_row = int(self.header_value.get())-1
            except Exception:
                header_row = 0
            self.df = pd.read_excel(filepath,header=header_row) if file_extention in ['xlsx','xls'] else pd.read_csv(filepath, header=header_row)
            self.checks = {}
            longitude_lab = tk.Label(self.scrollable_frame, text='Longitude (E/W)',width=15).grid(row=0,column=1)
            latitude_lab = tk.Label(self.scrollable_frame, text='Latitude (N/S)',width=15).grid(row=0,column=2)
            self.check_var_long = tk.StringVar(value="")
            self.check_var_lat = tk.StringVar(value="")
            for i,col in enumerate(self.df.columns):
                colname = tk.Label(self.scrollable_frame,text=col,width=15)
                colname.grid(row=i+1,column=0)
                longitude = tk.Radiobutton(self.scrollable_frame, variable=self.check_var_long,width=2,value=col).grid(row=i+1,column=1)
                latitude = tk.Radiobutton(self.scrollable_frame, variable=self.check_var_lat,width=2,value=col).grid(row=i+1,column=2)
        self.run_button.configure(state="normal")               

if __name__=='__main__':
    app = CRSTransformApp()
    app.mainloop()