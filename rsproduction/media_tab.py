import tkinter as tk
import tkinter.ttk as ttk
import shutil
import platform

from ravenspace_production_tool import inventory
from ravenspace_production_tool import saf_builder
from ravenspace_production_tool import dspace_api


class MediaTab(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.tab = ttk.Frame(self.parent)
        self.parent.add(self.tab, text='Media')

        #  Select the directory containing the new media
        self.frame1 = tk.Frame(self.tab, width=400, height=20)
        self.frame1.pack(fill="both", expand="true", padx=10)
        ttk.Label(self.frame1, text="Media Folder: ").pack(side="left")
        self.media = tk.StringVar(self.frame1)
        self.media_entry = ttk.Entry(self.frame1)
        self.media_entry.pack(side="left", fill="x", expand="true")
        self.media_button = ttk.Button(self.frame1, text="Browse", command=lambda: self.media_browse())
        self.media_button.pack(side="left")

        # Select the level of processing for media files
        self.frame2 = ttk.Frame(self.tab, width=400, height=20)
        self.frame2.pack(fill="both", expand="true", padx=10)
        self.process = tk.IntVar()
        ttk.Label(self.frame2, text="Media Processing:").pack(side="left")
        self.proc_none = ttk.Radiobutton(self.frame2, text="None", variable=self.process, value=1)
        self.proc_none.pack(side="left", padx=10, fill="x", expand="true")
        self.proc_conv = ttk.Radiobutton(self.frame2, text="Convert only", variable=self.process, value=2)
        self.proc_conv.pack(side="left", padx=10, fill="x", expand="true")
        self.proc_opt = ttk.Radiobutton(self.frame2, text="Optimize", variable=self.process, value=3)
        self.proc_opt.pack(side="left", padx=10, fill="x", expand="true")

        system = platform.system()
        if system == "Windows":
            self.im = shutil.which("magick")
        else:
            self.im = shutil.which("convert")
        self.ffmpeg = shutil.which("ffmpeg")
        if self.im is None or self.ffmpeg is None:
            self.process.set(1)
            self.proc_conv.configure(state=tk.DISABLED)
            self.proc_opt.configure(state=tk.DISABLED)

        self.import_frame = ttk.Frame(self.tab, width=400, height=20)
        self.import_frame.pack(fill="both", expand="true", padx=10)
        self.ing_method = tk.IntVar()
        ttk.Label(self.import_frame, text="Import Method:").pack(side="left")
        self.saf = ttk.Radiobutton(self.import_frame, text="Simple Archive Format",
                                   variable=self.ing_method, value=1).pack(side="left", padx=10)
        self.api = ttk.Radiobutton(self.import_frame, text="REST API", variable=self.ing_method,
                                   value=2).pack(side="left", padx=10)

        # Build frames for separate ingestion phases
        self.ing_phase = tk.IntVar()

        self.frame3 = ttk.Frame(self.tab, width=400, height=20)
        self.frame3.pack(fill="both", expand="true", padx=10)
        self.new = ttk.Radiobutton(self.frame3, variable=self.ing_phase, value=1, command=lambda: self.phase_enable())
        self.new.pack(side="left", anchor="n")

        self.frame3A = ttk.LabelFrame(self.frame3, text="New Items", width=400, height=20)
        self.frame3A.pack(fill="both", expand="true")

        self.frame3A1 = ttk.Frame(self.frame3A, width=400, height=20)
        self.frame3A1.pack(fill="both", expand="true", side="left", padx=10)
        self.project_label = ttk.Label(self.frame3A1, text="Project ISBN: ")
        self.project_label.pack(side="left")
        self.project_entry = ttk.Entry(self.frame3A1, width=20)
        self.project_entry.pack(side="left")

        self.frame3A2 = ttk.Frame(self.frame3A, width=400, height=20)
        self.frame3A2.pack(fill="both", expand="true", side="right", padx=10)
        self.series_label = ttk.Label(self.frame3A2, text="Next Available Series #:")
        self.series_label.pack(side="left")
        self.series_entry = ttk.Entry(self.frame3A2, width=5)
        self.series_entry.pack(side="left")

        self.frame4 = ttk.Frame(self.tab, width=400, height=20)
        self.frame4.pack(fill="both", expand="true", padx=10)
        self.update = ttk.Radiobutton(self.frame4, variable=self.ing_phase, value=2,
                                      command=lambda: self.phase_enable())
        self.update.pack(side="left", anchor="n")

        self.frame4A = ttk.Labelframe(self.frame4, text="Update Existing Items")
        self.frame4A.pack(fill="both", expand="true", side="left")

        self.frame4A1 = ttk.Frame(self.frame4A, width=400, height=20)
        self.frame4A1.pack(fill="both", expand="true", side="left", padx="10")
        self.csv_label = ttk.Label(self.frame4A1, text="DSpace CSV: ")
        self.csv_label.pack(side="left")
        self.csv = tk.StringVar()
        self.csv_entry = ttk.Entry(self.frame4A1)
        self.csv_entry.pack(side="left", fill="x", expand="true")
        self.csv_button = ttk.Button(self.frame4A1, text="Browse", command=lambda: self.csv_browse())
        self.csv_button.pack(side="left")

        self.frame5 = ttk.Frame(self.tab, width=400, height=20)
        self.frame5.pack(fill="both", expand="true", padx=10)
        self.status = tk.StringVar()
        self.status.set("Waiting for a submission...")
        self.status_display = ttk.Label(self.frame5, textvariable=self.status)
        self.status_display.pack(side="left")
        self.run_button = ttk.Button(self.frame5, text="RUN", command=lambda: self.run(), width=20)
        self.run_button.pack(side="right")

        for child in self.frame3A1.winfo_children():
            child.configure(state=tk.DISABLED)
        for child in self.frame3A2.winfo_children():
            child.configure(state=tk.DISABLED)
        for child in self.frame4A1.winfo_children():
            child.configure(state=tk.DISABLED)

    def media_browse(self):
        """Select media folder using file dialog"""
        self.media_entry.insert(0, "./")
        media_select = tk.filedialog.askdirectory(initialdir='./')
        self.media_entry.delete(0, "end")
        self.media_entry.insert(0, media_select)
        self.media.set(media_select)

    def phase_enable(self):
        """Disable and Enable ingestion phase frames based on user radiobutton selection."""
        phase = self.ing_phase.get()
        if phase == 1:
            for child in self.frame3A1.winfo_children():
                child.configure(state=tk.NORMAL)
            for child in self.frame3A2.winfo_children():
                child.configure(state=tk.NORMAL)
            for child in self.frame4A1.winfo_children():
                child.configure(state=tk.DISABLED)
        if phase == 2:
            for child in self.frame4A1.winfo_children():
                child.configure(state=tk.NORMAL)
            for child in self.frame3A1.winfo_children():
                child.configure(state=tk.DISABLED)
            for child in self.frame3A2.winfo_children():
                child.configure(state=tk.DISABLED)

    def csv_browse(self):
        """Update the entry for "DSpace CSV" with user input through a filedialog."""
        csv_select = tk.filedialog.askopenfilename(initialdir='./', filetypes=[("Comma Separated Values", "*.csv")])
        self.csv_entry.delete(0, "end")
        self.csv_entry.insert(0, csv_select)
        self.csv.set(csv_select)

    def run(self):
        self.status.set("Processing...")
        self.status_display.update()
        media_dir = self.media.get()
        process = self.process.get()
        phase = self.ing_phase.get()
        ing_method = self.ing_method.get()
        if phase == 1:
            project_id = self.project_entry.get()
            series_num = self.series_entry.get()
            out_dir = f'./{project_id}'
            sub_dir = shutil.copytree(media_dir, f'{out_dir}/temp/media')
            csv_inv = inventory.submitInventory(project_id, series_num, sub_dir, out_dir, process)
            if ing_method == 1:
                arc_dir = f'{out_dir}/temp/archives'
                SimpleArchiveBuilder.run(out_dir, sub_dir, arc_dir, csv_inv)
                self.status.set("Done!")
                tk.filedialog.askopenfile(mode='r', initialdir=out_dir)
            elif ing_method == 2:
                popup = tk.Toplevel()
                popup.title("DSpace Submission")

                popframe1 = tk.Frame(popup, width=400, height=20)
                popframe1.pack(fill="both", expand="true", padx=10, pady=2)
                l1 = ttk.Label(popframe1, text="Collection Handle:")
                l1.pack(side="left")
                collection = tk.StringVar()
                collection_entry = ttk.Entry(popframe1, textvariable=collection)
                collection_entry.pack(side="left")

                popframe2 = tk.Frame(popup, width=400, height=20)
                popframe2.pack(fill="both", expand="true", padx=10, pady=2)
                l2 = ttk.Label(popframe2, text="Email:")
                l2.pack(side="left")
                email_var = tk.StringVar()
                email_entry = ttk.Entry(popframe2, textvariable=email_var)
                email_entry.pack(side="left")

                popframe3 = tk.Frame(popup, width=400, height=20)
                popframe3.pack(fill="both", expand="true", padx=10, pady=2)
                l3 = ttk.Label(popframe3, text="Password:")
                l3.pack(side="left")
                password_var = tk.StringVar()
                pass_entry = ttk.Entry(popframe3, show='*', textvariable=password_var)
                pass_entry.pack(side="left")

                popframe4 = tk.Frame(popup, width=400, height=20)
                popframe4.pack(fill="both", expand="true", padx=10, pady=2)
                submit = ttk.Button(popframe4, text="SUBMIT", command=lambda: apisub(out_dir, csv_inv))
                submit.pack()

                def apisub(out_dir, csv_inv):
                    handle = collection.get()
                    email = email_var.get()
                    password = password_var.get()
                    dspace_api.ingest(out_dir, csv_inv, handle, email, password)
                    popup.destroy()
                    self.status.set("Done!")
                    tk.filedialog.askopenfile(mode='r', initialdir=out_dir)

                popup.mainloop()

        elif phase == 2:
            csvIn = self.csv.get()
            out_dir = f'./update'
            sub_dir = shutil.copytree(media_dir, f'{out_dir}/submission')
            inventory.updateInventory(csvIn, sub_dir, out_dir, process)
            self.status.set("Done")
            self.status_display.update()
            tk.filedialog.askopenfile(mode='r', initialdir=out_dir)
