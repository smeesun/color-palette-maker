import tkinter as tk
from tkinter import ttk, filedialog, colorchooser
from PIL import Image, ImageTk


class PaletteStudio:

    def __init__(self, root):

        self.root = root
        self.root.title("Palette Studio")
        self.root.geometry("1200x700")
        self.root.resizable(False, False)

        # 現在選択中の色
        self.current_color = "#FFFFFF"

        # パレット（3色）
        self.palette = [
            "#FFFFFF",
            "#FFFFFF",
            "#FFFFFF"
        ]

        self.create_widgets()
        

    # ------------------------------
    # GUI
    # ------------------------------

    def create_widgets(self):

        #============================
        # 左側
        #============================

        left = tk.Frame(self.root, width=420, padx=10, pady=10)
        left.pack(side="left", fill="y")

        # タイトル
        tk.Label(
            left,
            text="Palette Studio",
            font=("Yu Gothic UI", 20, "bold")
        ).pack(anchor="w", pady=(0,15))

        # プレビュー
        tk.Label(
            left,
            text="Color Preview",
            font=("Yu Gothic UI", 11)
        ).pack(anchor="w")

        self.preview = tk.Frame(
            left,
            width=200,
            height=120,
            bg=self.current_color,
            relief="solid",
            bd=1
        )
        self.preview.pack(pady=10)
        self.preview.pack_propagate(False)

        # HEX
        tk.Label(
            left,
            text="HEX"
        ).pack(anchor="w")

        self.hex_var = tk.StringVar(value=self.current_color)

        self.hex_entry = ttk.Entry(
            left,
            textvariable=self.hex_var,
            width=25
        )

        self.hex_entry.pack(anchor="w", pady=(0,10))
        self.hex_entry.bind("<Return>", self.hex_changed)
        self.hex_entry.bind("<FocusOut>", self.hex_changed)

        # RGB

        tk.Label(
            left,
            text="RGB"
        ).pack(anchor="w")

        rgb_frame = tk.Frame(left)
        rgb_frame.pack(anchor="w", pady=(0,15))

        self.r_var = tk.IntVar(value=255)
        self.g_var = tk.IntVar(value=255)
        self.b_var = tk.IntVar(value=255)

        ttk.Entry(rgb_frame,textvariable=self.r_var,width=5).grid(row=0,column=0,padx=2)
        ttk.Entry(rgb_frame,textvariable=self.g_var,width=5).grid(row=0,column=1,padx=2)
        ttk.Entry(rgb_frame,textvariable=self.b_var,width=5).grid(row=0,column=2,padx=2)

        # ボタン

        ttk.Button(
            left,
            text="カラーピッカー",
            command=self.pick_color
        ).pack(fill="x", pady=5)

        ttk.Button(
            left,
            text="画像を開く",
            command=self.open_image
        ).pack(fill="x", pady=5)

        ttk.Button(
            left,
            text="スポイト（準備中）"
        ).pack(fill="x", pady=5)

        # Palette

        tk.Label(
            left,
            text="Palette",
            font=("Yu Gothic UI", 12, "bold")
        ).pack(anchor="w", pady=(20,5))





        #============================
        # 右側
        #============================

        right = tk.Frame(self.root, padx=10, pady=10)
        right.pack(side="right", fill="both", expand=True)

        tk.Label(
            right,
            text="Image",
            font=("Yu Gothic UI",15,"bold")
        ).pack(anchor="w")

        self.canvas = tk.Canvas(
            right,
            width=700,
            height=620,
            bg="#dcdcdc"
        )

        self.canvas.pack()

        self.image = None


    # ------------------------------
    # カラーピッカー
    # ------------------------------

    def pick_color(self):

        color = colorchooser.askcolor()[1]

        if color:

            self.current_color = color

            self.hex_var.set(color)

            r = int(color[1:3],16)
            g = int(color[3:5],16)
            b = int(color[5:7],16)

            self.r_var.set(r)
            self.g_var.set(g)
            self.b_var.set(b)

            self.preview.config(bg=color)

    def hex_changed(self, event=None):

        color = self.hex_var.get().strip()

        # #が無ければ付ける
        if not color.startswith("#"):
            color = "#" + color

        # 形式チェック
        if len(color) != 7:
            return

        try:
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)

        except ValueError:
            return

        self.current_color = color.upper()

        self.preview.config(bg=self.current_color)

        self.hex_var.set(self.current_color)

        self.r_var.set(r)
        self.g_var.set(g)
        self.b_var.set(b)


    # ------------------------------
    # 画像を開く
    # ------------------------------

    def open_image(self):

        path = filedialog.askopenfilename(
            filetypes=[
                ("Image","*.png *.jpg *.jpeg *.bmp")
            ]
        )

        if not path:
            return

        img = Image.open(path)

        img.thumbnail((700,620))

        self.image = img

        self.photo = ImageTk.PhotoImage(img)

        self.canvas.delete("all")

        self.canvas.create_image(
            0,
            0,
            image=self.photo,
            anchor="nw"
        )


root = tk.Tk()

PaletteStudio(root)

root.mainloop()
def get_color_from_image(self, event):

    if self.image is None:
        return

    x = event.x
    y = event.y

    pixel = self.image.getpixel((x, y))

    r = pixel[0]
    g = pixel[1]
    b = pixel[2]

    hex_color = f"#{r:02X}{g:02X}{b:02X}"

    self.preview.config(bg=hex_color)

    self.hex_var.set(hex_color)

    self.r_var.set(r)
    self.g_var.set(g)
    self.b_var.set(b)
