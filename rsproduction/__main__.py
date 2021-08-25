import tkinter as tk
import tkinter.ttk as ttk
import shutil

from . import manuscript_tab
from . import media_tab
from . import csv_tab
# import webarchiveTab

class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.tab_control = ttk.Notebook(self.parent)
        pandoc = shutil.which("pandoc")
        if pandoc is not None:
            self.manuscripttab = manuscript_tab.ManuscriptTab(self.tab_control)
        self.mediatab = media_tab.MediaTab(self.tab_control)
        self.csvtab = csv_tab.CSVTab(self.tab_control)
        # self.webarchivetab = wat.WebArchiveTab(self.tab_control)
        self.tab_control.pack(expand=1, fill="both")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("RavenSpace Production Tool")
    MainApplication(root).pack(expand=1, fill="both")
    root.mainloop()
