import os
import platform
import shutil
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as tkfd

from . import scalarize


class ManuscriptTab(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.tab = ttk.Frame(self.parent)
        self.parent.add(self.tab, text='Manuscript')

        #  Select the manuscript file
        self.frame1 = tk.Frame(self.tab, width=400, height=20)
        self.frame1.pack(fill="both", expand="true", padx=10)
        ttk.Label(self.frame1, text="Manuscript: ").pack(side="left")
        self.man_file = tk.StringVar(self.frame1)
        self.entry = ttk.Entry(self.frame1)
        self.entry.pack(side="left", fill="x", expand="true")
        self.man_file_button = ttk.Button(self.frame1, text="Browse",
                                          command=lambda: self.man_file_browse()).pack(side="left")

        self.frame2 = tk.Frame(self.tab, width=420, height=20)
        self.frame2.pack(fill="both", expand="true", padx=10)
        self.man_media_state = tk.IntVar(self.frame2)
        self.man_media_opt = ttk.Checkbutton(self.frame2, variable=self.man_media_state)
        self.man_media_opt.pack(side="left", anchor="n")
        self.frame2A = ttk.Labelframe(self.frame2, text="Include Media", width=400, height=20)
        self.frame2A.pack(fill="both", expand="true", side="left")

        self.frame2A1 = ttk.Frame(self.frame2A, width=400, height=20)
        self.frame2A1.pack(fill="both", expand="true", padx=10)
        self.isbn = tk.StringVar()
        ttk.Label(self.frame2A1, text="Project ISBN:").pack(side="left")
        self.isbn_entry = ttk.Entry(self.frame2A1, textvariable=self.isbn, width=13).pack(side="left")

        self.frame2A2 = ttk.Frame(self.frame2A, width=400, height=20)
        self.frame2A2.pack(fill="both", expand="true", padx=10)
        self.ing_method = tk.IntVar()
        ttk.Label(self.frame2A2, text="Import Method:").pack(side="left")
        self.saf = ttk.Radiobutton(self.frame2A2, text="Simple Archive Format",
                                   variable=self.ing_method, value=1).pack(side="left", padx=10)
        self.api = ttk.Radiobutton(self.frame2A2, text="REST API", variable=self.ing_method,
                                   value=2).pack(side="left", padx=10)

        self.frame2A3 = ttk.Frame(self.frame2A, width=400, height=20)
        self.frame2A3.pack(fill="both", expand="true", padx=10)

        self.ext_media = tk.IntVar()
        self.frame2A3B = ttk.Checkbutton(self.frame2A3, variable=self.ext_media)
        self.frame2A3B.pack(side="left", anchor="n", pady=10)
        self.frame2A3C = ttk.Labelframe(self.frame2A3, text="Use External Media", width=400, height=20)
        self.frame2A3C.pack(fill="both", expand="true", side="left", pady=10)

        self.frame2A3C1 = ttk.Frame(self.frame2A3C, width=400, height=20)
        self.frame2A3C1.pack(fill="both", expand="true", padx=10)
        self.media = tk.StringVar()
        ttk.Label(self.frame2A3C1, text="Media Folder:").pack(side="left")
        self.media_entry = ttk.Entry(self.frame2A3C1, textvariable=self.media)
        self.media_entry.pack(side="left", fill="x", expand="true")
        self.media_button = ttk.Button(self.frame2A3C1, text="Browse", command=lambda: self.media_browse())
        self.media_button.pack(side="left")

        # Select the level of processing for media files
        self.frame2A3C2 = ttk.Frame(self.frame2A3C, width=400, height=20)
        self.frame2A3C2.pack(fill="both", expand="true", padx=10)
        self.process = tk.IntVar()
        self.process.set(1)
        ttk.Label(self.frame2A3C2, text="Media Processing:").pack(side="left")
        self.proc_none = ttk.Radiobutton(self.frame2A3C2, text="None", variable=self.process, value=1)
        self.proc_none.pack(side="left", padx=10, fill="x", expand="true")
        self.proc_conv = ttk.Radiobutton(self.frame2A3C2, text="Convert only", variable=self.process, value=2)
        self.proc_conv.pack(side="left", padx=10, fill="x", expand="true")
        self.proc_opt = ttk.Radiobutton(self.frame2A3C2, text="Optimize", variable=self.process, value=3)
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

        self.frame3 = ttk.Frame(self.tab, width=400, height=20)
        self.frame3.pack(fill="both", expand="true", padx=10)
        self.status = tk.StringVar()
        self.status.set("Waiting for a submission...")
        self.status_display = ttk.Label(self.frame3, textvariable=self.status)
        self.status_display.pack(side="left")
        self.button = ttk.Button(self.frame3, text="RUN", command=lambda: self.run(), width=20).pack(side="right")

    def man_file_browse(self):
        """Select manuscript file using file dialog"""
        self.entry.insert(0, "./")
        man_file_select = tkfd.askopenfilename(initialdir='./', filetypes=[("Word Document", "*.docx")])
        self.entry.delete(0, "end")
        self.entry.insert(0, man_file_select)
        self.man_file.set(man_file_select)

    def media_browse(self):
        """Select media folder using file dialog"""
        self.media_entry.insert(0, "./")
        media_select = tk.filedialog.askdirectory(initialdir='./')
        self.media_entry.delete(0, "end")
        self.media_entry.insert(0, media_select)
        self.media.set(media_select)

    def run(self):
        self.status.set("Processing...")
        try:
            man_file = self.man_file.get()
            isbn = self.isbn.get()
            ing_method = self.ing_method.get()
            man_filename = os.path.basename(man_file)
            out_dir = os.path.splitext(man_filename)[0]
            os.makedirs(out_dir)
            if self.man_media_state.get() == 0:
                scalarize.no_media(man_file, out_dir)
                tk.filedialog.askopenfile(mode='r', initialdir=out_dir)
            elif self.man_media_state.get() == 1:
                media_dir = self.media.get()
                process_opt = self.process.get()
                if ing_method == 1:
                    scalarize.saf_media(man_file, out_dir, isbn, media_dir, process_opt)
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
                    submit = ttk.Button(popframe4, text="SUBMIT", command=lambda: apisub(man_file, out_dir, isbn,
                                                                                         media_dir, process_opt))
                    submit.pack()

                    def apisub(man_file, out_dir, isbn, media_dir, process_opt):
                        handle = collection.get()
                        email = email_var.get()
                        password = password_var.get()
                        scalarize.api_media(man_file, out_dir, isbn, media_dir, process_opt, handle, email, password)
                        popup.destroy()
                        self.status.set("Done!")
                        self.status_display.update()
                        tk.filedialog.askopenfile(mode='r', initialdir=out_dir)

                    popup.mainloop()

        except:
            self.status.set("Error. The process was not completed.")