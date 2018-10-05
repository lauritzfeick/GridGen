import os
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from GridBuilder import compute_gridstr
from typing import List
from MonitorLayout import MonitorLayout


def btn_callback_add_psd(grid_counter, psd_paths, listbox):
    try:
        paths = filedialog.askopenfilenames()
        for path in paths:
            path = os.path.abspath(path)
            psd_paths.append(path)
            listbox.insert(END, "{0}   \t{1}".format(grid_counter, os.path.basename(path)))
            grid_counter += 1
    except ValueError:
        pass
    print(psd_paths)


def btn_callback_rm_psd(grid_counter:int, psd_paths:List[str], listbox):
    """
    Removes the last monitor from the setup.
    """
    grid_counter -= 1
    listbox.delete(END)
    del psd_paths[-1]


def btn_callback_run(psd_paths:List[str], layout_str:str):
    f = filedialog.asksaveasfile(mode='w', defaultextension=".grid")
    monitor_layouts = MonitorLayout.parse_layout(layout_str)
    grid = compute_gridstr(monitor_layouts, psd_paths)
    f.write(grid)
    f.close()
    print("fin")


def GUI():
    psd_paths = []
    grid_counter = -1

    root = Tk()
    root.title("Grid Generator")
    icon = PhotoImage(file='ico.gif')
    root.tk.call('wm', 'iconphoto', root._w, icon)
    root.wm_resizable(width=FALSE, height=FALSE)

    n_cols0 = 0
    font = 'Arial'
    font_size = 20

    # 1st row:
    lstbx = Listbox(root, height=5, width=50)
    lstbx.grid(row=1, column=0, columnspan=3)
    lstbx.config(font=(font, font_size))

    # 0th row:
    btn_psd = ttk.Button(root, text="Add psd-file", command=lambda:btn_callback_add_psd(len(psd_paths), psd_paths, lstbx))
    btn_psd.grid(row=0, column=n_cols0, sticky=W)
    n_cols0 += 1

    btn_rm_psd = ttk.Button(root, text="Remove last psd-file", \
                            command=lambda:btn_callback_rm_psd(grid_counter, psd_paths, lstbx))
    btn_rm_psd.grid(row=0, column=n_cols0, sticky=W)
    n_cols0 += 1

    # 2nd row:
    lbl_layout = ttk.Label(root, text='Define layout here:')
    lbl_layout.grid(row=2, column=0, sticky=W)

    # 3rd row:
    txt_input_layout = Text(root, height=5, width=50)
    txt_input_layout.grid(row=3, column=0, columnspan=3)
    txt_input_layout.config(font=(font, font_size))

    # 4th row:
    btn_run = ttk.Button(root, text="Compute", width=40, command=lambda:btn_callback_run(psd_paths, txt_input_layout.get("0.0",END)))
    btn_run.grid(row=4, column=0, columnspan=3, sticky=W)
    lbl_status = ttk.Label

    root.mainloop()


def main():
    GUI()


if __name__ == "__main__":
    main()







