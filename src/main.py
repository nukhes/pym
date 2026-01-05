import os
from tkinter import *
import tkinter.filedialog
from tkinter import simpledialog
import pastebin_handler
from tkinter import ttk, messagebox
from explorer import FileExplorer
from custom_scrollbar import CustomScrollbar

root = Tk()
root.title("pym")
root.geometry("800x600")

config_file = os.path.join(os.path.expanduser("~"), ".pymrc")

api_key = ""
current_font_size = 12
current_font_family = "Courier"
is_dark_theme = False
is_dirty = False
current_file_path = None

theme_light = {
    "bg": "white", "fg": "black", "insert": "black", 
    "line_bg": "#f0f0f0", "line_fg": "black",
    "sb_bg": "#f0f0f0", "sb_fg": "#cdcdcd"
}
theme_dark = {
    "bg": "#1e1e1e", "fg": "#d4d4d4", "insert": "white", 
    "line_bg": "#252526", "line_fg": "#858585",
    "sb_bg": "#252526", "sb_fg": "#424242"
}

def save_config():
    try:
        with open(config_file, "w") as f:
            f.write(f"font_family: {current_font_family}\n")
            f.write(f"font_size: {current_font_size}\n")
            f.write(f"pastebin_api_key: {api_key}\n")
            f.write(f"dark_theme: {is_dark_theme}\n")
    except Exception as e:
        print(f"error saving config: {e}")

def load_config():
    global api_key, current_font_size, current_font_family, is_dark_theme
    
    if not os.path.exists(config_file):
        return

    try:
        with open(config_file, "r") as f:
            for line in f:
                if ":" in line:
                    key, val = line.strip().split(":", 1)
                    val = val.strip()
                    
                    if key == "font_family":
                        current_font_family = val
                    elif key == "font_size":
                        current_font_size = int(val)
                    elif key == "pastebin_api_key":
                        api_key = val
                    elif key == "dark_theme":
                        is_dark_theme = (val == "True")
    except Exception as e:
        print(f"error loading config: {e}")

def popup(message, is_error=False):
    title, bg_color = ("error", "#ffebee") if is_error else ("success", "#e8f5e9")
    win = Toplevel(root)
    win.title(title)
    win.resizable(False, False)
    win.geometry("350x150")

    win.configure(bg=bg_color)

    frame = Frame(win, bg=bg_color)
    frame.pack(expand=True, fill="both", padx=20, pady=20)
    
    Label(frame, text=message, bg=bg_color, wraplength=300, justify="center").pack(pady=10)
    Button(frame, text="ok", command=win.destroy, width=10).pack(side="bottom")

    win.transient(root)
    win.grab_set()
    root.wait_window(win)

def selectall(event=None):
    text_area.tag_add("sel", "1.0", "end")
    return "break"

def prompt_save():
    global is_dirty
    if not is_dirty:
        return True

    result = messagebox.askyesnocancel("pym", "you have unsaved changes. do you want to save them?")
    if result is True:
        return save()
    elif result is False:
        return True
    else:
        return False


def toggle_explorer():
    if explorer_frame.winfo_viewable():
        main_pane.remove(explorer_frame)
    else:
        main_pane.add(explorer_frame, width=250, before=editor_frame)

def load_file(path):
    global current_file_path, is_dirty
    with open(path, "r") as file:
        text_area.delete("1.0", "end")
        text_area.insert("1.0", file.read())
        root.title(f"pym - {path}")
        current_file_path = path
        is_dirty = False
        text_area.edit_modified(False)
        update_line_numbers()

def saveas(event=None):
    global is_dirty, current_file_path
    t = text_area.get("1.0", "end-1c")
    path = tkinter.filedialog.asksaveasfilename(initialfile=current_file_path)
    if path:
        with open(path, "w+") as output:
            output.write(t)
            root.title(f"pym - {path}")
            is_dirty = False
            current_file_path = path
            text_area.edit_modified(False)
            return True
    return False

def save(event=None):
    if current_file_path and os.path.exists(current_file_path):
        global is_dirty
        t = text_area.get("1.0", "end-1c")
        with open(current_file_path, "w") as output:
            output.write(t)
            is_dirty = False
            text_area.edit_modified(False)
            return True
    else:
        return saveas()

def new_file(event=None):
    global current_file_path, is_dirty
    if not prompt_save():
        return
    text_area.delete("1.0", "end")
    root.title("pym")
    current_file_path = None
    is_dirty = False
    text_area.edit_modified(False)
    update_line_numbers()

def open_file(event=None):
    global current_file_path, is_dirty
    if not prompt_save():
        return
    path = tkinter.filedialog.askopenfilename()
    if path:
        load_file(path)

def on_explorer_click(path):
    if not prompt_save():
        return
    load_file(path)


def set_pastebin_api_key():
    global api_key
    k = simpledialog.askstring("settings", "pastebin api key", parent=root)
    if k:
        api_key = k.strip().replace("'", "").replace('"', "")
        save_config()

def change_font_family():
    global current_font_family
    f = simpledialog.askstring("settings", "font family (e.g. courier, arial)", parent=root, initialvalue=current_font_family)
    if f:
        current_font_family = f
        update_font()
        save_config()

def change_font_size():
    global current_font_size
    size = simpledialog.askinteger("settings", "font size", parent=root, initialvalue=current_font_size)
    if size:
        current_font_size = size
        update_font()
        save_config()

def update_font():
    font_spec = (current_font_family, current_font_size)
    text_area.config(font=font_spec)
    line_numbers.config(font=font_spec)

def apply_theme():
    colors = theme_dark if is_dark_theme else theme_light
    text_area.config(bg=colors["bg"], fg=colors["fg"], insertbackground=colors["insert"])
    line_numbers.config(bg=colors["line_bg"], fg=colors["line_fg"])
    menubar.config(bg=colors["line_bg"], fg=colors["fg"])
    file_menu.config(bg=colors["line_bg"], fg=colors["fg"])
    settings_menu.config(bg=colors["line_bg"], fg=colors["fg"])
    scrollbar.config(bg=colors["sb_bg"])
    scrollbar.itemconfig(scrollbar.thumb, fill=colors["sb_fg"])

def toggle_theme():
    global is_dark_theme
    is_dark_theme = not is_dark_theme
    apply_theme()
    save_config()

def save2pastebin():
    if not api_key:
        popup("set a valid api_key in settings", True)
        return
    
    code = text_area.get("1.0", "end-1c")
    
    if not code.strip():
        popup("ensure your editor isnt empty", True)
        return

    success, result = pastebin_handler.upload(api_key, code)
    
    if success:
        root.clipboard_clear()
        root.clipboard_append(result)
        popup(f"copied to clipboard: \n{result}", False)
    else:
        popup(f"pastebin rejected: {result}", True)

def mark_dirty(event=None):
    global is_dirty
    is_dirty = True
    update_line_numbers()
    text_area.edit_modified(False)


def update_line_numbers(event=None):
    lines = text_area.get("1.0", "end-1c").count("\n") + 1
    line_content = "\n".join(str(i) for i in range(1, lines + 1))
    
    line_numbers.config(state="normal")
    line_numbers.delete("1.0", "end")
    line_numbers.insert("1.0", line_content)
    
    line_numbers.tag_add("right", "1.0", "end")
    
    line_numbers.config(state="disabled")
    sync_scroll()

def sync_scroll(*args):
    if args:
        line_numbers.yview(*args)
        text_area.yview(*args)
    else:
        current_pos = text_area.yview()[0]
        line_numbers.yview_moveto(current_pos)

def on_closing():
    if prompt_save():
        root.destroy()

load_config()

menubar = Menu(root, bd=0, activeborderwidth=0, relief="flat")

file_menu = Menu(menubar, tearoff=0)

file_menu.add_command(label="new file", command=new_file, accelerator="ctrl+n")
file_menu.add_command(label="open file", command=open_file, accelerator="ctrl+o")
file_menu.add_command(label="open folder", command=lambda: explorer.open_folder(), accelerator="ctrl+k")
file_menu.add_command(label="save", command=save, accelerator="ctrl+s")
file_menu.add_command(label="save2pastebin", command=save2pastebin)
file_menu.add_separator()
file_menu.add_command(label="exit", command=on_closing, accelerator="ctrl+q")
menubar.add_cascade(label="file", menu=file_menu)

view_menu = Menu(menubar, tearoff=0)
view_menu.add_command(label="toggle explorer", command=toggle_explorer)
menubar.add_cascade(label="view", menu=view_menu)

settings_menu = Menu(menubar, tearoff=0)
settings_menu.add_command(label="pastebin api key", command=set_pastebin_api_key)
settings_menu.add_command(label="font family", command=change_font_family)
settings_menu.add_command(label="font size", command=change_font_size)
settings_menu.add_command(label="toggle theme", command=toggle_theme)
menubar.add_cascade(label="settings", menu=settings_menu)

root.config(menu=menubar)

main_pane = PanedWindow(root, sashwidth=8, orient="horizontal")
main_pane.pack(fill="both", expand=True)

explorer_frame = Frame(main_pane)
main_pane.add(explorer_frame, width=250)

explorer = FileExplorer(explorer_frame, on_file_click=on_explorer_click)
explorer.pack(fill="both", expand=True)

editor_frame = Frame(main_pane)
main_pane.add(editor_frame)

scrollbar = CustomScrollbar(editor_frame)
scrollbar.pack(side="right", fill="y")

line_numbers = Text(editor_frame, width=4, padx=5, takefocus=0, bd=0, highlightthickness=0, background="#f0f0f0", state="disabled")
line_numbers.pack(side="left", fill="y")
line_numbers.tag_configure("right", justify="right")

text_area = Text(editor_frame, wrap="none", undo=True, bd=0, highlightthickness=0)
text_area.pack(side="left", fill="both", expand=True)

main_pane.paneconfigure(explorer_frame, minsize=100)
main_pane.paneconfigure(editor_frame, minsize=400)

update_font()
apply_theme()

scrollbar.config(command=sync_scroll)
def on_text_scroll(*args):
    scrollbar.set(*args)
    line_numbers.yview_moveto(args[0])
text_area.config(yscrollcommand=on_text_scroll)
text_area.bind("<<Modified>>", mark_dirty)

text_area.bind("<Control-a>", selectall)
text_area.bind("<Control-s>", save)
text_area.bind("<Control-n>", new_file)
text_area.bind("<Control-o>", open_file)
text_area.bind("<Control-k>", explorer.open_folder)
text_area.bind("<Control-q>", lambda e: on_closing())

root.protocol("WM_DELETE_WINDOW", on_closing)

update_line_numbers()

root.mainloop()