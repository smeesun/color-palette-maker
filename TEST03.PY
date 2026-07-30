import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageGrab



# ======================================
# テーマ設定
# ======================================
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

# ======================================
# ツールチップ
# ======================================
class ToolTip:

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None

        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)


    def show_tip(self, event=None):

        if self.tip_window or not self.text:
            return

        x = self.widget.winfo_rootx() + 10
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            tw,
            text=self.text,
            background="#FFFFFF",
            foreground="black",
            relief="solid",
            borderwidth=1,
            padx=6,
            pady=2
        )
        label.pack()


    def hide_tip(self, event=None):

        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        # ======================================
        # ウィンドウ設定
        # ======================================
        self.geometry("400x760")
        self.title("COLpama")

        # サイズ固定
        self.resizable(False, False)

        # 背景の色指定
        self.configure(fg_color="#3b1d35")


        # ======================================
        # ヘッダー（固定）
        # ======================================
        header = ctk.CTkFrame(
            self,
            height=40,
            fg_color="#dddddd"
        )
        header.pack(fill="x")


        home_btn = ctk.CTkButton(
            header,
            text="🏠 COLpama",
            width=80,
            fg_color="#e8aedd",
            hover_color="#e358c7",
            text_color="white",
            corner_radius=20,
            command=self.go_home
        )

        home_btn.pack(
            side="left",
            padx=5,
            pady=5
        )


        # ======================================
        # スクロールエリア
        # ======================================
        self.scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="white",
            corner_radius=0
        )

        self.scroll.pack(
            fill="both",
            expand=True
        )

        # ======================================
        # ↓ここからコンテンツを追加していく
        # ======================================

        # ======================================
        # トップ画像
        # ======================================
        image = Image.open("images/COLpama_top.png")

        image = image.resize((380, 260))


        self.top_image = ctk.CTkImage(
            light_image=image,
            dark_image=image,
            size=(380, 260)
        )


        image_label = ctk.CTkLabel(
            self.scroll,
            text="",
            image=self.top_image
        )

        image_label.pack(
            pady=10
        )


        # ======================================
        # TOPメニューボタン
        # ======================================

        menu_frame = ctk.CTkFrame(
            self.scroll,
            fg_color="transparent"
        )

        menu_frame.pack(
            pady=10
        )


        # 1段目
        btn1 = ctk.CTkButton(
            menu_frame,
            text="セレクト",
            font=("あめふりドロップス無料版", 16),
            width=150,
            corner_radius=50,
            fg_color="#e6a5f8",
            hover_color="#866091",
            text_color="white",
            command=self.scroll_select
        )

        btn1.grid(
            row=0,
            column=0,
            padx=5,
            pady=5
        )


        btn2 = ctk.CTkButton(
            menu_frame,
            text="カテゴリ",
            font=("あめふりドロップス無料版", 16),
            width=150,
            corner_radius=50,
            fg_color="#e6a5f8",
            hover_color="#866091",
            text_color="white",
            command=self.scroll_category
        )

        btn2.grid(
            row=0,
            column=1,
            padx=5,
            pady=5
        )


        # 2段目
        btn3 = ctk.CTkButton(
            menu_frame,
            text="プリセット",
            font=("あめふりドロップス無料版", 16),
            width=150,
            corner_radius=50,
            fg_color="#e6a5f8",
            hover_color="#866091",
            text_color="white",
            command=self.scroll_preset
        )

        btn3.grid(
            row=1,
            column=0,
            padx=5,
            pady=5
        )


        btn4 = ctk.CTkButton(
            menu_frame,
            text="ラッキーカラー",
            font=("あめふりドロップス無料版", 16),
            width=150,
            corner_radius=50,
            fg_color="#e6a5f8",
            hover_color="#866091",
            text_color="white",
            command=self.scroll_recommend
        )

        btn4.grid(
            row=1,
            column=1,
            padx=5,
            pady=5
        )

        self.space()


# ======================================
# サブタイトル
# ======================================
        # ======================================
        # セレクト
        # ======================================

        # セクションの枠
        self.select_frame = ctk.CTkFrame(
            self.scroll,
            fg_color="white"
        )

        self.select_frame.pack(
            fill="x",
            pady=10
        )

        # 上ライン
        self.section_line(self.select_frame)

        # タイトル
        ctk.CTkLabel(
            self.select_frame,
            text="セレクト",
            font=("あめふりドロップス無料版", 22, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=8
        )

        # ------------------------------------
        # 下ライン
        self. section_line(self.select_frame)

        # 余白
        ctk. CTkFrame(
            self. select_frame, 
            height = 12, 
            fg_color = "transparent"
        ). pack(fill = "x")



# ======================================
# セレクト機能
# ======================================    
        # ------------------------------------
        # 左側：スポイト＋カラーコード欄
        # ------------------------------------
        self. current_hex = "#FFFFFF"

        select_content = ctk. CTkFrame(
            self. select_frame,
            fg_color = "transparent"
        )
        select_content. pack(
            anchor = "w", 
            padx=15, 
            pady=(0, 15)
        )

        # スポイトボタン
        self.eyedropper_btn = ctk.CTkButton(
            select_content,
            text="💉",
            width=80,
            corner_radius=50,
            fg_color="#e6a5f8",
            hover_color="#866091",
            text_color="white",
            command=self.start_eyedropper
        )
        self.eyedropper_btn.pack(anchor="w", pady=(0, 10))

        ToolTip(self.eyedropper_btn, "スポイト")

        
        hex_row = ctk.CTkFrame(
            select_content,
            fg_color="transparent"
        )
        hex_row.pack(anchor="w")

        self.hex_entry = ctk.CTkEntry(
            hex_row,
            width=80,
            placeholder_text="#FFFFFF"
        )
        self.hex_entry.pack(side="left")
        self.hex_entry.bind("<Return>", self.on_hex_entry_enter)

        self.copy_btn = ctk.CTkButton(
            hex_row,
            text="📝",
            width=40,
            corner_radius=50,
            fg_color="#e6a5f8",
            hover_color="#866091",
            text_color="white",
            command=self.copy_hex_code
        )
        self.copy_btn.pack(side="left", padx=(5, 0))

        ToolTip(self.copy_btn, "コピーする")


        # 色プレビュー（拾った色を確認しやすいように追加）
        self.color_preview = ctk.CTkLabel(
            select_content,
            text="",
            width=40,
            height=40,
            fg_color=self.current_hex,
            corner_radius=8
        )
        self.color_preview.pack(anchor="w", pady=(10, 0))


        self.space()

        # ======================================
        # カテゴリ
        # ======================================

        self.category_frame = ctk.CTkFrame(
            self.scroll,
            fg_color="white"
        )

        self.category_frame.pack(
            fill="x",
            pady=10
        )

        # 上ライン
        self.section_line(self.category_frame)

        ctk.CTkLabel(
            self.category_frame,
            text="カテゴリ",
            font=("あめふりドロップス無料版", 22, "bold")
        ).pack(anchor="w", padx=15)

        # 下ライン
        self.section_line(self.category_frame)

        self.space()



        # ======================================
        # プリセット
        # ======================================

        self.preset_frame = ctk.CTkFrame(
            self.scroll,
            fg_color="white"
        )

        self.preset_frame.pack(
            fill="x",
            pady=10
        )

        # 上ライン
        self.section_line(self.preset_frame)

        ctk.CTkLabel(
            self.preset_frame,
            text="プリセット",
            font=("あめふりドロップス無料版", 22, "bold")
        ).pack(anchor="w", padx=15)

        # 下ライン
        self.section_line(self.preset_frame)

        self.space()



        # ======================================
        # ラッキーカラー
        # ======================================

        self.recommend_frame = ctk.CTkFrame(
            self.scroll,
            fg_color="white"
        )

        self.recommend_frame.pack(
            fill="x",
            pady=10
        )

        # 上ライン
        self.section_line(self.recommend_frame)

        ctk.CTkLabel(
            self.recommend_frame,
            text="ラッキーカラー",
            font=("あめふりドロップス無料版", 22, "bold")
        ).pack()

        # 下ライン
        self.section_line(self.recommend_frame)

        self.space()

    # ======================================
    # セクション用の区切り線（1本）
    # ======================================
    def section_line(self, parent):
        line = tk.Canvas(
            parent,
            height=1,
            bg="white",
            highlightthickness=0
        )
        line.create_line(
            0, 0, 1000, 0,
            fill="#d0d0d0",
             width=1
        )
        line.pack(fill="x", padx=10)

    # ======================================
    # スポイト機能
    # ======================================
    def start_eyedropper(self):

        # 画面全体を覆う透明なオーバーレイを作成
        self.overlay = tk.Toplevel(self)
        self.overlay.attributes("-fullscreen", True)
        self.overlay.attributes("-alpha", 0.01)   # ほぼ透明
        self.overlay.attributes("-topmost", True)
        self.overlay.configure(cursor="crosshair")

        self.overlay.bind("<Motion>", self.preview_color)
        self.overlay.bind("<Button-1>", self.pick_color)
        self.overlay.bind("<Escape>", self.cancel_eyedropper)

        self.overlay.focus_force()


    def get_pixel_color(self, x, y):

        # 1pxだけ切り取って取得（負荷軽減のため）
        screenshot = ImageGrab.grab(bbox=(x, y, x + 1, y + 1))
        rgb = screenshot.getpixel((0, 0))

        return "#{:02x}{:02x}{:02x}".format(*rgb[:3])


    def preview_color(self, event):

        # マウスが動くたびに呼ばれる（確定はしない）
        hex_color = self.get_pixel_color(event.x_root, event.y_root)

        self.hex_entry.delete(0, "end")
        self.hex_entry.insert(0, hex_color)
        self. color_preview. configure(fg_color = hex_color)

    
    def pick_color(self, event):

        # 左クリックされた瞬間に呼ばれる（確定する）
        hex_color = self.get_pixel_color(event.x_root, event.y_root)

        self.apply_color(hex_color)
        self.overlay.destroy()


    def cancel_eyedropper(self, event=None):

        self.overlay.destroy()

    # ======================================
    # コピー処理
    # ======================================
    def copy_hex_code(self):

        value = self.hex_entry.get().strip()

        self.clipboard_clear()
        self.clipboard_append(value)
        self.update()

    # ======================================
    # カラーコード反映
    # ======================================
    def apply_color(self, hex_color):

        self.current_hex = hex_color

        self.hex_entry.delete(0, "end")
        self.hex_entry.insert(0, hex_color)

        self.color_preview.configure(fg_color=hex_color)


    def on_hex_entry_enter(self, event=None):

        value = self.hex_entry.get().strip()

        if not value.startswith("#"):
            value = "#" + value

        # #RRGGBB形式かどうかの簡易チェック
        if len(value) == 7:
            try:
                int(value[1:], 16)
                self.apply_color(value)
            except ValueError:
                print("無効なカラーコードです")
        else:
            print("無効なカラーコードです")


    # ======================================
    # 空白スペース
    # ======================================
    def space(self):

        spacer = ctk.CTkFrame(
            self.scroll,
            height=70,
            fg_color="transparent"
        )

        spacer.pack()



    # ======================================
    # ホームへ戻る
    # ======================================
    def go_home(self):

        self.scroll._parent_canvas.yview_moveto(0)



    # ======================================
    # スクロール移動処理
    # ======================================
    def move_scroll(self, target):

        self.update()

        y = target.winfo_y()

        self.scroll._parent_canvas.yview_moveto(
            y / self.scroll._parent_canvas.bbox("all")[3]
        )



    def scroll_select(self):
        self.move_scroll(self.select_frame)


    def scroll_category(self):
        self.move_scroll(self.category_frame)


    def scroll_preset(self):
        self.move_scroll(self.preset_frame)


    def scroll_recommend(self):
        self.move_scroll(self.recommend_frame)



# ======================================
# アプリ起動
# ======================================
app = App()
app.mainloop()