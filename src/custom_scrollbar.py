from tkinter import Canvas

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