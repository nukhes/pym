import os
from tkinter import *
import tkinter.filedialog
from tkinter import simpledialog
import pastebin_handler

class CustomScrollbar(Canvas):
    def __init__(self, master, **kwargs):
        kwargs.setdefault("width", 14)
        kwargs.setdefault("bd", 0)
        kwargs.setdefault("highlightthickness", 0)
        super().__init__(master, **kwargs)
        self.command = None
        self.thumb = self.create_rectangle(0, 0, 0, 0, fill="#555", outline="")
        self.bind("<Button-1>", self.on_press)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<Configure>", lambda e: self.redraw())
        self.y_top = 0.0
        self.y_bottom = 1.0
        self.click_offset = 0.0

    def set(self, first, last):
        self.y_top = float(first)
        self.y_bottom = float(last)
        self.redraw()

    def redraw(self):
        h = self.winfo_height()
        w = self.winfo_width()
        if h == 0: return
        y0 = self.y_top * h
        y1 = self.y_bottom * h
        if y1 - y0 < 20:
            y1 = y0 + 20
            if y1 > h:
                y0 = h - 20
                y1 = h
        self.coords(self.thumb, 2, y0, w-2, y1)

    def on_press(self, event):
        h = self.winfo_height()
        if h == 0: return
        y_frac = event.y / h
        if self.y_top <= y_frac <= self.y_bottom:
            self.click_offset = y_frac - self.y_top
            self.dragging = True
        else:
            self.dragging = False
            if self.command:
                new_top = y_frac - (self.y_bottom - self.y_top)/2
                self.command("moveto", new_top)

    def on_drag(self, event):
        if not getattr(self, 'dragging', False): return
        h = self.winfo_height()
        if h == 0: return
        y_frac = event.y / h
        new_top = y_frac - self.click_offset
        if self.command:
            self.command("moveto", new_top)
    
    def config(self, **kwargs):
        if "command" in kwargs:
            self.command = kwargs.pop("command")
        super().config(**kwargs)

root = Tk()
root.title("pym")
root.geometry("800x600")

config_file = os.path.join(os.path.expanduser("~"), ".pymrc")

api_key = ""
current_font_size = 12
current_font_family = "Courier"
is_dark_theme = False

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

def saveas():
    t = text_area.get("1.0", "end-1c")
    path = tkinter.filedialog.asksaveasfilename()
    if path:
        with open(path, "w+") as output:
            output.write(t)
            root.title(f"pym - {path}")

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

def save_to_pastebin():
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

load_config()

menubar = Menu(root, bd=0, activeborderwidth=0, relief="flat")

file_menu = Menu(menubar, tearoff=0)
file_menu.add_command(label="save", command=saveas, accelerator="ctrl+s")
file_menu.add_command(label="save2pastebin", command=save_to_pastebin)
file_menu.add_separator()
file_menu.add_command(label="exit", command=root.quit)
menubar.add_cascade(label="file", menu=file_menu)

settings_menu = Menu(menubar, tearoff=0)
settings_menu.add_command(label="pastebin_api_key", command=set_pastebin_api_key)
settings_menu.add_command(label="font_family", command=change_font_family)
settings_menu.add_command(label="font_size", command=change_font_size)
settings_menu.add_command(label="toggle_theme", command=toggle_theme)
menubar.add_cascade(label="settings", menu=settings_menu)

root.config(menu=menubar)

main_frame = Frame(root)
main_frame.pack(fill="both", expand=True)

scrollbar = CustomScrollbar(main_frame)
scrollbar.pack(side="right", fill="y")

line_numbers = Text(main_frame, width=4, padx=5, takefocus=0, bd=0, highlightthickness=0, background="#f0f0f0", state="disabled")
line_numbers.pack(side="left", fill="y")
line_numbers.tag_configure("right", justify="right")

text_area = Text(main_frame, wrap="none", undo=True, bd=0, highlightthickness=0)
text_area.pack(side="left", fill="both", expand=True)

update_font()
apply_theme()

scrollbar.config(command=sync_scroll)
def on_text_scroll(*args):
    scrollbar.set(*args)
    line_numbers.yview_moveto(args[0])
text_area.config(yscrollcommand=on_text_scroll)
text_area.bind("<KeyRelease>", update_line_numbers)

text_area.bind("<Control-a>", selectall)
text_area.bind("<Control-s>", lambda x: saveas())

update_line_numbers()

root.mainloop()