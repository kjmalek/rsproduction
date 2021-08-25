import tkinter as tk
import tkinter.ttk as ttk

from . import update


class CSVTab(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.tab = ttk.Frame(self.parent)
        self.parent.add(self.tab, text='CSV')

        # Build CSV Update Tab in the GUI
        # Set a variable to listen for user selection of "Add" or "Update"
        self.csv_state = tk.IntVar()
        # Build a radiobutton for selecting "Add"
        self.csv_add = ttk.Radiobutton(self.tab, variable=self.csv_state, value=1, command=lambda: self.csv_enable())
        self.csv_add.grid(row=0, column=0, sticky='ne')
        # Build a radiobutton for selecting "Update"
        self.csv_up = ttk.Radiobutton(self.tab, variable=self.csv_state, value=2, command=lambda: self.csv_enable())
        self.csv_up.grid(row=1, column=0, sticky='ne')
        # Build a frame for the "Add form
        self.csv_add_frame = ttk.LabelFrame(self.tab, text="Add")
        self.csv_add_frame.grid(row=0, column=1, sticky='nw')
        # Build a frame for the "Update" form
        self.csv_up_frame = ttk.LabelFrame(self.tab, text="Update")
        self.csv_up_frame.grid(row=1, column=1, sticky='nw')

        # Fill the "Add" frame with an input form
        # ADD - DSPACE COLLECTION CSV: input
        ttk.Label(self.csv_add_frame, text="DSpace Collection CSV: ").grid(row=0, column=0, sticky='e')
        self.add_csv_entry = ttk.Entry(self.csv_add_frame)
        self.add_csv_entry.grid(row=0, column=1, sticky='w', ipadx=38)
        self.add_csv_browse = ttk.Button(self.csv_add_frame, text="Browse", command=lambda: self.csv_add_select())
        self.add_csv_browse.grid(row=0, column=2, sticky='w')

        # ADD - EXPORT TO: input
        ttk.Label(self.csv_add_frame, text="Export to: ").grid(row=1, column=0, sticky='e')
        self.add_ex = tk.StringVar()
        self.add_ex_entry = ttk.Entry(self.csv_add_frame)
        self.add_ex.set(self.add_ex_entry)
        self.add_ex_entry.grid(row=1, column=1, sticky='w', ipadx=38)
        self.add_ex_browse = ttk.Button(self.csv_add_frame, text="Save As", command=lambda: self.add_ex_select())
        self.add_ex_browse.grid(row=1, column=2, sticky='w')

        # ADD - PROCESS CSV button for running the add_csv_process function
        self.add_csv_button = ttk.Button(self.csv_add_frame, text="Process CSV", command=lambda: self.add_csv_process())
        self.add_csv_button.grid(row=2, column=2, sticky='e')

        # Fill the "Update" frame with an input form
        # UPDATE - DSPACE FINAL COLLECTION CSV: input
        ttk.Label(self.csv_up_frame, text="DSpace Final Collection CSV: ").grid(row=0, column=0, sticky='ne')
        self.ds_final_entry = ttk.Entry(self.csv_up_frame)
        self.ds_final_entry.grid(row=0, column=1, sticky='w', ipadx=24)
        self.ds_final_browse = ttk.Button(self.csv_up_frame, text="Browse", command=lambda: self.ds_final_select())
        self.ds_final_browse.grid(row=0, column=2)

        # UPDATE - SCALAR MEDIA CSV: input
        ttk.Label(self.csv_up_frame, text="Scalar Media CSV: ").grid(row=1, column=0, sticky='ne')
        self.scalar_media_entry = ttk.Entry(self.csv_up_frame)
        self.scalar_media_entry.grid(row=1, column=1, sticky='w', ipadx=24)
        self.scalar_media_browse = ttk.Button(self.csv_up_frame, text='Browse',
                                              command=lambda: self.scalar_media_select())
        self.scalar_media_browse.grid(row=1, column=2)

        # UPDATE - SCALAR PAGES CSV: input
        ttk.Label(self.csv_up_frame, text="Scalar Pages CSV: ").grid(row=2, column=0, sticky='ne')
        self.scalar_pages_entry = ttk.Entry(self.csv_up_frame)
        self.scalar_pages_entry.grid(row=2, column=1, sticky='w', ipadx=24)
        self.scalar_pages_browse = ttk.Button(self.csv_up_frame, text="Browse",
                                              command=lambda: self.scalar_pages_select())
        self.scalar_pages_browse.grid(row=2, column=2)

        # UPDATE - EXPORT MEDIA CSV TO: input
        ttk.Label(self.csv_up_frame, text="Export Media CSV to: ").grid(row=3, column=0, sticky='ne')
        self.media_ex_entry = ttk.Entry(self.csv_up_frame)
        self.media_ex_entry.grid(row=3, column=1, sticky='w', ipadx=24)
        self.media_ex_browse = ttk.Button(self.csv_up_frame, text="Save As", command=lambda: self.media_ex_select())
        self.media_ex_browse.grid(row=3, column=2)

        # UPDATE - EXPORT PAGES CSV TO: input
        ttk.Label(self.csv_up_frame, text="Export Pages CSV to: ").grid(row=4, column=0, sticky='ne')
        self.pages_ex_entry = ttk.Entry(self.csv_up_frame)
        self.pages_ex_entry.grid(row=4, column=1, sticky='w', ipadx=24)
        self.pages_ex_browse = ttk.Button(self.csv_up_frame, text="Save As", command=lambda: self.pages_ex_select())
        self.pages_ex_browse.grid(row=4, column=2)

        # UPDATE - PROCESS CSVS button for running the up_csv_process function
        self.up_csv_button = ttk.Button(self.csv_up_frame, text="Process CSVs", command=lambda: self.up_csv_process())
        self.up_csv_button.grid(row=5, column=2)

        # Disable the "Add" and "Update" frames until a user makes a selection.
        for child in self.csv_add_frame.winfo_children():
            child.configure(state=tk.DISABLED)
        for child in self.csv_up_frame.winfo_children():
            child.configure(state=tk.DISABLED)

    def csv_enable(self):
        """Disable and Enable frames based on user radiobutton selection."""
        state = self.csv_state.get()
        if state == 1:
            for child in self.csv_add_frame.winfo_children():
                child.configure(state=tk.NORMAL)
            for child in self.csv_up_frame.winfo_children():
                child.configure(state=tk.DISABLED)
        if state == 2:
            for child in self.csv_add_frame.winfo_children():
                child.configure(state=tk.DISABLED)
            for child in self.csv_up_frame.winfo_children():
                child.configure(state=tk.NORMAL)

    def csv_add_select(self):
        """Update the entry for "DSpace Collection CSV" with user input through a filedialog."""
        csv_add_select = tk.filedialog.askopenfilename(initialdir='./',
                                                       filetypes=[("comma-separated values file", "*.csv")])
        self.add_csv_entry.delete(0, last=200)
        self.add_csv_entry.insert(0, csv_add_select)

    def add_ex_select(self):
        """Update the entry for "Export to" with user input through filedialog."""
        add_ex_select = tk.filedialog.asksaveasfilename(initialdir='./', defaultextension=".csv")
        self.add_ex_entry.delete(0, last=200)
        self.add_ex_entry.insert(0, add_ex_select)
        self.add_ex.set(add_ex_select)

    def add_csv_process(self):
        """Get values inputted into form and run those values through the update.newMedia function."""
        dcsv = self.add_csv_entry.get()
        scsv = self.add_ex.get()
        update.newMedia(dcsv, scsv)
        tk.filedialog.askopenfilename(initialfile=scsv)

    def ds_final_select(self):
        """Update the entry for "DSpace Final Collection CSV" with user input from filedialog."""
        ds_final_select = tk.filedialog.askopenfilename(initialdir='./',
                                                        filetypes=[("comma-separated values file", "*.csv")])
        self.ds_final_entry.delete(0, last=200)
        self.ds_final_entry.insert(0, ds_final_select)

    def scalar_media_select(self):
        """Update the entry for "Scalar Media CSV" with user input from filedialog."""
        scalar_media_select = tk.filedialog.askopenfilename(initialdir='./',
                                                            filetypes=[("comma-separated values file", "*.csv")])
        self.scalar_media_entry.delete(0, last=200)
        self.scalar_media_entry.insert(0, scalar_media_select)

    def scalar_pages_select(self):
        """Update the entry for "Scalar Pages CSV" with user input from filedialog."""
        scalar_pages_select = tk.filedialog.askopenfilename(initialdir='./',
                                                            filetypes=[("comma-separated values file", "*.csv")])
        self.scalar_pages_entry.delete(0, last=200)
        self.scalar_pages_entry.insert(0, scalar_pages_select)

    def media_ex_select(self):
        """Update the entry for "Export Media CSV to" with user input from filedialog."""
        self.media_ex_select = tk.filedialog.asksaveasfilename(initialdir='./', defaultextension='.csv')
        self.media_ex_entry.delete(0, last=200)
        self.media_ex_entry.insert(0, media_ex_select)

    def pages_ex_select(self):
        """Update the entry for "Export Pages CSV to" with user input from filedialog."""
        pages_ex_select = tk.filedialog.asksaveasfilename(initialdir='./', defaultextension='.csv')
        self.pages_ex_entry.delete(0, last=200)
        self.pages_ex_entry.insert(0, pages_ex_select)

    def up_csv_process(self):
        """Get values inputted into form and run those values through update.updateMedia,
        update.inventoryUpdates, and update.updatePages."""
        ds_final = self.ds_final_entry.get()
        scalar_media = self.scalar_media_entry.get()
        scalar_pages = self.scalar_pages_entry.get()
        media_ex = self.media_ex_entry.get()
        pages_ex = self.pages_ex_entry.get()
        update.updateMedia(ds_final, scalar_media, media_ex)
        update.inventoryUpdates(scalar_media, media_ex)
        update.updatePages(scalar_pages, pages_ex)
        tk.filedialog.askopenfilename(initialfile=media_ex)
        tk.filedialog.askopenfilename(initialfile=pages_ex)