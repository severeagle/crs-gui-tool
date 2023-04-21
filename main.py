import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import pandas as pd
import geopandas as gpd
import shapely
import os


def transform_data(df, input_cols, output_cols, crs_from, crs_to):
    df["coords"] = df.apply(
        lambda row: shapely.geometry.Point(row[input_cols[0]], row[input_cols[1]])
        if pd.notna(row[input_cols[0]]) and pd.notna(row[input_cols[1]])
        else None,
        axis=1,
    )
    gdf = gpd.GeoDataFrame(df, geometry="coords").set_crs(crs_from)
    gdf = gdf.to_crs(crs_to)
    gdf[output_cols[0]] = gdf.geometry.x
    gdf[output_cols[1]] = gdf.geometry.y
    gdf = gdf.drop("coords", axis=1)
    return gdf


class CRSTransformApp(tk.Tk):
    def __init__(self) -> None:
        """ 
            Setup
        """
        super(CRSTransformApp, self).__init__()
        self.title("CRS Tranformation App")
        self.configure(bg="#0022C0")
        self.maxsize(500, 500)
        self.minsize(500, 500)
        #self.iconphoto(False, tk.PhotoImage(file=os.path.join("static", "Logo1.png")))

        """
            Upper Frame
        """
        self.upper_frame = tk.Frame(self)
        # File selection button
        filedialog_button = tk.Button(
            self.upper_frame, text="Select File", command=self.open_file_dialog
        ).grid(row=0, column=0)
        # Header selection | Defines the row number in the excel file that contain the column names
        header_label = tk.Label(self.upper_frame, text="Header Row:").grid(row=0,column=1)
        self.header_value = tk.Entry(self.upper_frame, width=3)
        self.header_value.insert(0, 2)
        self.header_value.grid(row=0, column=2)

        # CRS | Coordinate Reference System
        crs_from_label = tk.Label(self.upper_frame, text="Original CRS").grid(row=1,column=0)
        self.crs_from_value = tk.Entry(self.upper_frame, width=10)
        self.crs_from_value.insert(0, "EPSG:3067")
        self.crs_from_value.grid(row=1, column=1)
        crs_fo_label = tk.Label(self.upper_frame, text="Transformed CRS").grid(row=2,column=0)
        self.crs_to_value = tk.Entry(self.upper_frame, width=10)
        self.crs_to_value.insert(0, "EPSG:4326")
        self.crs_to_value.grid(row=2,column=1)
        
        self.upper_frame.pack()

        """
            Lowerframe
        """
        self.lower_frame = tk.Frame(self)
        output_filename_label = tk.Label(self.lower_frame, text="Export filename:").grid(row=2,column=0, columnspan=3)
        self.output_filename = tk.Entry(self.lower_frame, width=20)
        self.output_filename.insert(0, "reagle_transformed_data")
        self.output_filename.grid(row=3, column=0, columnspan=3)
        lon_col_name_label = tk.Label(self.lower_frame, text="New lon column name:").grid(row=4,column=0, columnspan=3)
        self.lon_col_name_value = tk.Entry(self.lower_frame, width=10)
        self.lon_col_name_value.insert(0, "")
        self.lon_col_name_value.grid(row=5, column=0,columnspan=3)
        lat_col_name_label = tk.Label(self.lower_frame, text="New lat column name:").grid(row=6,column=0, columnspan=3)
        self.lat_col_name_value = tk.Entry(self.lower_frame, width=10)
        self.lat_col_name_value.insert(0, "")
        self.lat_col_name_value.grid(row=7, column=0,columnspan=3)
        self.run_button = tk.Button(
            self.lower_frame,
            text="Run",
            command=self.run_pipeline,
            disabledforeground="white",
        )
        self.run_button.configure(state="disabled")
        self.run_button.grid(row=0, column=0, columnspan=3)
        self.lower_frame.pack(side="bottom")
        self.output_filetype = tk.StringVar(value="csv")
        tk.Radiobutton(
            self.lower_frame,
            text="xlsx",
            variable=self.output_filetype,
            width=3,
            value="xlsx",
        ).grid(row=1, column=0)
        tk.Radiobutton(
            self.lower_frame,
            text="xls",
            variable=self.output_filetype,
            width=3,
            value="xls",
        ).grid(row=1, column=1)
        tk.Radiobutton(
            self.lower_frame,
            text="csv",
            variable=self.output_filetype,
            width=3,
            value="csv",
        ).grid(row=1, column=2)

        # Create a canvas and scrollbar
        self.canvas = tk.Canvas(self, width=300, height=200)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        # Configure canvas and scrollbar
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def run_pipeline(self):
        try:
            filename = self.output_filename.get()
            filetype = self.output_filetype.get()
            crs_from = self.crs_from_value.get()
            crs_to = self.crs_to_value.get()
            full_filename = filename + "." + filetype
            export_path = os.path.join(self.dir,full_filename)

            geom_cols = [self.check_var_long.get(), self.check_var_lat.get()]
            transform_cols = []
            for i,l in enumerate([self.lon_col_name_value, self.lat_col_name_value]):
                col_name = l.get()
                if len(col_name) != 0:
                    transform_cols.append(col_name)
                else:
                    transform_cols.append(geom_cols[i]+"_transform")
            
            gdf = transform_data(self.df, geom_cols, transform_cols, crs_from, crs_to)

            if filetype == "xlsx":
                gdf.to_excel(export_path, index=False)
            elif filetype == "xls":
                writer = pd.ExcelWriter(export_path, engine="openpyxl")
                gdf.to_excel(writer, sheet_name="Sheet1")
                writer.save()
            else:
                gdf.to_csv(export_path, index=False)
            tk.messagebox.showinfo(
                message=f"Succesfully created new file {full_filename}"
            )
        except Exception as e:
            tk.messagebox.showinfo(
                message=f"Transforming the coordinates failed with exception:\n\t{e}"
            )

    def open_file_dialog(self):
        try:
            filepath = filedialog.askopenfilename()
            self.dir = os.path.dirname(filepath)
            if len(filepath) == 0:
                return
            file_extention = filepath.split(".")[-1]
            if file_extention in ["xls", "xlsx", "csv"]:
                try:
                    header_row = int(self.header_value.get()) - 1
                except Exception:
                    header_row = 0
                self.df = (
                    pd.read_excel(filepath, header=header_row)
                    if file_extention in ["xlsx", "xls"]
                    else pd.read_csv(filepath, header=header_row)
                )
            else:
                tk.messagebox.showinfo(
                    message=f"Only filetypes: xlsx, xls and csv are allowed."
                )
                self.run_button.configure(state="disabled")
                return
        except Exception as e:
            tk.messagebox.showinfo(
                message=f"Reading the file failed with exception:\n\t{e}"
            )
            self.run_button.configure(state="disabled")
            return
        
        self.checks = {}
        longitude_lab = tk.Label(
            self.scrollable_frame, text="Longitude (E/W)", width=15
        ).grid(row=0, column=2)
        latitude_lab = tk.Label(
            self.scrollable_frame, text="Latitude (N/S)", width=15
        ).grid(row=0, column=3)
        self.check_var_long = tk.StringVar(value="")
        self.check_var_lat = tk.StringVar(value="")
        for i, col in enumerate(self.df.columns):
            colname = tk.Label(self.scrollable_frame, text=col, width=25)
            colname.grid(row=i + 1, column=0, columnspan=2)
            longitude = tk.Radiobutton(
                self.scrollable_frame,
                variable=self.check_var_long,
                width=2,
                value=col,
            ).grid(row=i + 1, column=2)
            latitude = tk.Radiobutton(
                self.scrollable_frame,
                variable=self.check_var_lat,
                width=2,
                value=col,
            ).grid(row=i + 1, column=3)
        self.run_button.configure(state="normal")


if __name__ == "__main__":
    app = CRSTransformApp()
    app.mainloop()
