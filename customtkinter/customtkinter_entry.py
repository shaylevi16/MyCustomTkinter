import tkinter
import sys

from .customtkinter_frame import CTkFrame
from .appearance_mode_tracker import AppearanceModeTracker
from .customtkinter_color_manager import CTkColorManager


class CTkEntry(tkinter.Frame):
    def __init__(self,
                 master=None,
                 bg_color=None,
                 fg_color=CTkColorManager.ENTRY,
                 text_color=CTkColorManager.TEXT,
                 corner_radius=10,
                 width=120,
                 height=25,
                 *args,
                 **kwargs):
        super().__init__(master=master)

        AppearanceModeTracker.add(self.change_appearance_mode)
        self.appearance_mode = AppearanceModeTracker.get_mode()  # 0: "Light" 1: "Dark"

        self.bg_color = self.detect_color_of_master() if bg_color is None else bg_color
        self.fg_color = self.bg_color if fg_color is None else fg_color
        self.text_color = text_color

        self.width = width
        self.height = height

        self.corner_radius = self.calc_optimal_corner_radius(corner_radius)  # optimise for less artifacts

        if self.corner_radius*2 > self.height:
            self.corner_radius = self.height/2
        elif self.corner_radius*2 > self.width:
            self.corner_radius = self.width/2

        self.configure(width=self.width, height=self.height)

        self.canvas = tkinter.Canvas(master=self,
                                     highlightthicknes=0,
                                     width=self.width,
                                     height=self.height)
        self.canvas.place(x=0, y=0)

        self.entry = tkinter.Entry(master=self,
                                   bd=0,
                                   highlightthicknes=0,
                                   *args, **kwargs)
        self.entry.place(relx=0.5, rely=0.5, relwidth=0.8, anchor=tkinter.CENTER)

        self.fg_parts = []

        self.draw()

    def destroy(self):
        AppearanceModeTracker.remove(self.change_appearance_mode)
        super().destroy()

    def detect_color_of_master(self):
        if isinstance(self.master, CTkFrame):
            return self.master.fg_color
        else:
            return self.master.cget("bg")

    @staticmethod
    def calc_optimal_corner_radius(user_corner_radius):
        if sys.platform == "darwin":
            return user_corner_radius  # on macOS just use given value (canvas has Antialiasing)
        else:
            user_corner_radius = 0.5 * round(user_corner_radius / 0.5)  # round to 0.5 steps

            # make sure the value is always with .5 at the end for smoother corners
            if user_corner_radius == 0:
                return 0
            elif user_corner_radius % 1 == 0:
                return user_corner_radius + 0.5
            else:
                return user_corner_radius

    def draw(self):
        self.canvas.delete("all")
        self.fg_parts = []

        if sys.platform == "darwin":
            oval_size_corr_br = 0
        else:
            oval_size_corr_br = -1  # correct canvas oval draw size on bottom and right by 1 pixel (too large otherwise)

        # frame_border
        self.fg_parts.append(self.canvas.create_oval(0,
                                                     0,
                                                     self.corner_radius*2 + oval_size_corr_br,
                                                     self.corner_radius*2 + oval_size_corr_br))
        self.fg_parts.append(self.canvas.create_oval(self.width-self.corner_radius*2,
                                                     0,
                                                     self.width + oval_size_corr_br,
                                                     self.corner_radius*2 + oval_size_corr_br))
        self.fg_parts.append(self.canvas.create_oval(0,
                                                     self.height-self.corner_radius*2,
                                                     self.corner_radius*2 + oval_size_corr_br,
                                                     self.height + oval_size_corr_br))
        self.fg_parts.append(self.canvas.create_oval(self.width-self.corner_radius*2,
                                                     self.height-self.corner_radius*2,
                                                     self.width + oval_size_corr_br,
                                                     self.height + oval_size_corr_br))

        self.fg_parts.append(self.canvas.create_rectangle(0, self.corner_radius,
                                                          self.width, self.height-self.corner_radius))
        self.fg_parts.append(self.canvas.create_rectangle(self.corner_radius, 0,
                                                          self.width-self.corner_radius, self.height))

        for part in self.fg_parts:
            if type(self.fg_color) == tuple:
                self.canvas.itemconfig(part, fill=self.fg_color[self.appearance_mode], width=0)
            else:
                self.canvas.itemconfig(part, fill=self.fg_color, width=0)

        if type(self.bg_color) == tuple:
            self.canvas.configure(bg=self.bg_color[self.appearance_mode])
        else:
            self.canvas.configure(bg=self.bg_color)

        if type(self.fg_color) == tuple:
            self.entry.configure(bg=self.fg_color[self.appearance_mode],
                                 highlightcolor=self.fg_color[self.appearance_mode])
        else:
            self.entry.configure(bg=self.fg_color,
                                 highlightcolor=self.fg_color)

        if type(self.text_color) == tuple:
            self.entry.configure(fg=self.text_color[self.appearance_mode],
                                 insertbackground=self.text_color[self.appearance_mode])
        else:
            self.entry.configure(fg=self.text_color,
                                 insertbackground=self.text_color)

    def config(self, *args, **kwargs):
        self.configure(*args, **kwargs)

    def configure(self, *args, **kwargs):
        super().configure(*args, **kwargs)

    def change_appearance_mode(self, mode_string):
        if mode_string.lower() == "dark":
            self.appearance_mode = 1
        elif mode_string.lower() == "light":
            self.appearance_mode = 0

        if isinstance(self.master, CTkFrame):
            self.bg_color = self.master.fg_color
        else:
            self.bg_color = self.master.cget("bg")

        self.draw()

    def delete(self, *args, **kwargs):
        return self.entry.delete(*args, **kwargs)

    def insert(self, *args, **kwargs):
        return self.entry.insert(*args, **kwargs)

    def get(self):
        return self.entry.get()

