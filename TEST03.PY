import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageGrab, ImageTk
import colorsys
import math


# ======================================
# テーマ設定
# ======================================
ctk. set_appearance_mode("Light")
ctk. set_default_color_theme("blue")

# ======================================
# ツールチップ
# ======================================
class ToolTip:

    def __init__(self, widget, text):
        self. widget = widget
        self. text = text
        self. tip_window = None

        widget. bind("<Enter>", self. show_tip)
        widget. bind("<Leave>", self. hide_tip)


    def show_tip(self, event = None):

        if self. tip_window or not self. text:
            return

        x = self. widget. winfo_rootx() + 10
        y = self. widget. winfo_rooty() + self. widget. winfo_height() + 5

        self. tip_window = tw = tk. Toplevel(self. widget)
        tw. wm_overrideredirect(True)
        tw. wm_geometry(f"+{x}+{y}")

        label = tk. Label(
            tw,
            text = self. text,
            background = "#FFFFFF",
            foreground = "black",
            relief = "solid",
            borderwidth = 1,
            padx = 6,
            pady = 2
        )
        label. pack()


    def hide_tip(self, event = None):

        if self. tip_window:
            self. tip_window. destroy()
            self. tip_window = None


# ======================================
# 単一選択ボタングループ
# ======================================
class SingleSelectGroup:

    def __init__(self, parent, title, options, font_name="ふてほど丸ゴシック"):

        self. selected = None
        self. buttons = {}

        ctk. CTkLabel(
            parent,
            text = f"-{title}-",
            font = (font_name, 16, "bold"),
            text_color = "#555555"
        ). pack(anchor = "w", padx = 15, pady = (15, 5))

        row = ctk. CTkFrame(parent, fg_color = "transparent")
        row. pack(anchor = "w", padx = 15, pady = (0, 5))

        for option in options:
            btn = ctk. CTkButton(
                row,
                text = option,
                width = 70,
                corner_radius = 50,
                fg_color = "#e6a5f8",
                hover_color = "#866091",
                text_color = "white",
                font = (font_name, 14),
                command = lambda o = option: self. select(o)
            )
            btn. pack(side = "left", padx = 5)

            self. buttons[option] = btn

    def select(self, option):

        # すでに選ばれているボタンをもう一度押しても何もしない
        if self. selected == option:
            return

        # 前に選ばれていたボタンがあれば、普通の紫に戻す
        if self. selected is not None:
            self. buttons[self. selected]. configure(
                fg_color = "#e6a5f8",
                hover_color = "#866091",
                text_color = "white"
            )

        # 今回選ばれたボタンをピンクにする
        self. selected = option

        self. buttons[option]. configure(

            fg_color = "#ff6f9f",
            hover_color = "#ff6f9f",
            text_color = "white",

        )

    # ======================================
    # グループを初期状態(未選択)に戻す
    # ======================================
    def reset(self):

        for btn in self. buttons. values():
            btn. configure(
                fg_color = "#e6a5f8",
                hover_color = "#866091",
                text_color = "white"
            )

        self. selected = None
    


# ======================================
# アプリ本体
# ======================================
class App(ctk. CTk):

    def __init__(self):
        super().__init__()

        # ======================================
        # ウィンドウ設定
        # ======================================
        self. geometry("400x690")
        self. title("COLpama")

        # サイズ固定
        self. resizable(False, False)

        # 背景の色指定
        self. configure(fg_color = "#3b1d35")


        # ======================================
        # ヘッダー（固定）
        # ======================================
        header = ctk. CTkFrame(
            self,
            height=40,
            fg_color = "#dddddd"
        )
        header. pack(fill = "x")


        home_btn = ctk. CTkButton(
            header,
            text = "🏠 COLpama",
            width = 80,
            fg_color = "#e8aedd",
            hover_color = "#e358c7",
            text_color = "white",
            corner_radius = 20,
            command = self. go_home
        )

        home_btn. pack(
            side = "left",
            padx = 5,
            pady = 5
        )
        
        ToolTip(home_btn, "トップへ戻る")


        # ======================================
        # スクロールエリア
        # ======================================
        self. scroll = ctk.CTkScrollableFrame(
            self,
            fg_color = "white",
            corner_radius = 0
        )

        self. scroll. pack(
            fill = "both",
            expand = True
        )

        # ======================================
        # ↓ここからコンテンツを追加していく
        # ======================================

        # ======================================
        # トップ画像
        # ======================================
        image = Image. open("images/COLpama_top.png")

        image = image. resize((380, 260))


        self. top_image = ctk. CTkImage(
            light_image = image,
            dark_image = image,
            size = (380, 260)
        )


        image_label = ctk. CTkLabel(
            self. scroll,
            text = "",
            image = self. top_image
        )

        image_label. pack(
            pady = 10
        )


        # ======================================
        # TOPメニューボタン
        # ======================================

        menu_frame = ctk. CTkFrame(
            self. scroll,
            fg_color = "transparent"
        )

        menu_frame. pack(
            pady = 10
        )


        # 1段目
        btn1 = ctk. CTkButton(
            menu_frame,
            text = "セレクト",
            font = ("あめふりドロップス無料版", 16),
            width = 150,
            corner_radius = 50,
            fg_color = "#e6a5f8",
            hover_color = "#866091",
            text_color = "white",
            command = self.scroll_select
        )

        btn1. grid(
            row = 0,
            column = 0,
            padx = 5,
            pady = 5
        )


        btn2 = ctk.CTkButton(
            menu_frame,
            text = "カテゴリ",
            font = ("あめふりドロップス無料版", 16),
            width = 150,
            corner_radius = 50,
            fg_color = "#e6a5f8",
            hover_color = "#866091",
            text_color = "white",
            command = self. scroll_category
        )

        btn2. grid(
            row = 0,
            column = 1,
            padx = 5,
            pady = 5
        )


        # 2段目
        btn3 = ctk. CTkButton(
            menu_frame,
            text = "プリセット",
            font = ("あめふりドロップス無料版", 16),
            width = 150,
            corner_radius = 50,
            fg_color = "#e6a5f8",
            hover_color = "#866091",
            text_color = "white",
            command = self. scroll_preset
        )

        btn3. grid(
            row = 1,
            column = 0,
            padx = 5,
            pady = 5
        )


        btn4 = ctk. CTkButton(
            menu_frame,
            text = "ラッキーカラー",
            font = ("あめふりドロップス無料版", 16),
            width = 150,
            corner_radius = 50,
            fg_color = "#e6a5f8",
            hover_color = "#866091",
            text_color = "white",
            command = self. scroll_recommend
        )

        btn4. grid(
            row = 1,
            column = 1,
            padx = 5,
            pady = 5
        )

        self. space()


# ======================================
# サブタイトル
# ======================================
        # ======================================
        # セレクト
        # ======================================

        # セクションの枠
        self. select_frame = ctk. CTkFrame(
            self. scroll,
            fg_color = "white"
        )

        self. select_frame. pack(
            fill = "x",
            pady = 10
        )

        # 上ライン
        self. section_line(self. select_frame)

        # タイトル
        ctk. CTkLabel(
            self. select_frame,
            text = "セレクト",
            font = ("あめふりドロップス無料版", 22, "bold")
        ). pack(anchor = "w", padx = 15, pady = 8)

        # ------------------------------------
        # 下ライン
        self. section_line(self. select_frame)

        # 余白
        ctk. CTkFrame(
            self. select_frame, 
            height = 12, 
            fg_color = "transparent"
        ). pack(fill = "x")


# ======================================
# セレクト機能
# ====================================== 
        # 左右を横並びにするための行
        select_row = ctk. CTkFrame(
            self. select_frame,
            fg_color = "transparent"
        )
        select_row. pack(
            anchor = "w",
            padx = 15,
            pady = (0, 15),
            fill = "x"
        )

        # ------------------------------------
        # 左側：スポイト＋カラーコード欄
        # ------------------------------------
        self. current_hex = "#FFFFFF"

        select_content = ctk. CTkFrame(
            select_row,
            fg_color = "transparent"
        )
        select_content. pack(side = "left", anchor = "n")

        # スポイトボタン
        self. eyedropper_btn = ctk. CTkButton(
            select_content,
            text = "💉",
            width = 80,
            corner_radius = 50,
            fg_color = "#e6a5f8",
            hover_color = "#866091",
            text_color = "white",
            command = self. start_eyedropper
        )
        self. eyedropper_btn. pack(anchor = "w", pady = (0, 10))

        ToolTip(self. eyedropper_btn, "スポイト")

        hex_row = ctk. CTkFrame(
            select_content,
            fg_color = "transparent"
        )
        hex_row. pack(anchor = "w")

        self. hex_entry = ctk. CTkEntry(
            hex_row,
            width = 80,
            placeholder_text = "#FFFFFF"
        )
        self. hex_entry. pack(side = "left")
        self. hex_entry. bind("<Return>", self. on_hex_entry_enter)

        self. copy_btn = ctk. CTkButton(
            hex_row,
            text = "📝",
            width = 40,
            corner_radius = 50,
            fg_color = "#e6a5f8",
            hover_color = "#866091",
            text_color = "white",
            command = self. copy_hex_code
        )
        self. copy_btn. pack(side = "left", padx = (5, 0))

        ToolTip(self. copy_btn, "コピーする")

        # ------------------------------------
        # 右側：カラーピッカー（ホイール＋四角）
        # ------------------------------------
        self. wheel_size = 190
        self. wheel_thickness = 22
        self. square_size = 100

        self. current_hue = 0.0
        self. current_sat = 1.0
        self. current_val = 1.0

        self. ring_indicator_id = None
        self. square_indicator_id = None

        picker_frame = ctk.CTkFrame(
            select_row,
            fg_color = "transparent"
        )
        picker_frame. pack(side = "left", anchor = "n", padx = (20, 0))

        self. wheel_canvas = tk.Canvas(
            picker_frame,
            width = self. wheel_size,
            height = self. wheel_size,
            highlightthickness = 0,
            bg = "white",
            cursor = "circle"
        )
        self. wheel_canvas. pack()

        # リング画像を生成して貼り付け
        wheel_img = self.build_color_wheel_image(self. wheel_size, self. wheel_thickness)
        self. wheel_photo = ImageTk. PhotoImage(wheel_img)
        self. wheel_canvas. create_image(0, 0, image = self. wheel_photo, anchor = "nw")

        # 四角（彩度・明度）画像
        self. square_photo = None
        self. square_image_id = None
        self. draw_sv_square()

        # 選択位置の白丸（初期表示）
        self.update_indicators()

        # クリック・ドラッグで色を選択
        self. wheel_canvas. bind("<Button-1>", self. on_wheel_click)
        self. wheel_canvas. bind("<B1-Motion>", self. on_wheel_click)

        # ------------------------------------
        # 色プレビュー（大きく・中央）
        # ------------------------------------
        self. color_preview = ctk. CTkLabel(
            self. select_frame,
            text = "",
            width = 200,
            height = 80,
            corner_radius = 12,
            fg_color = self. current_hex,
            border_width = 0,
            border_color = "black"
        )
        self. color_preview.pack(pady=(20, 15))

        self. update_preview_border(self. current_hex)

        # ------------------------------------
        # 「この色で調べる」文言＋GOボタン
        # ------------------------------------
        self. select_go_btn = self. build_go_section(
            self. select_frame,
            "この色で調べる",
            self. on_select_go
        )

        self. space()


        # ======================================
        # 工事中画像（後々削除）🐻
        # ======================================
        self. prep_image = self. load_preparation_image()


        # ======================================
        # カテゴリ
        # ======================================

        # セクションの枠
        self. category_frame = ctk. CTkFrame(
            self. scroll,
            fg_color = "white"
        )

        self. category_frame. pack(
            fill = "x",
            pady = 10
        )

        # 上ライン
        self. section_line(self. category_frame)

        # タイトル
        ctk. CTkLabel(
            self. category_frame,
            text = "カテゴリ",
            font = ("あめふりドロップス無料版", 22, "bold")
        ). pack(anchor = "w", padx = 15, pady = 8)

        # ------------------------------------
        # 下ライン
        self. section_line(self. category_frame)


# ======================================
# カテゴリ機能
# ====================================== 
        # ------------------------------------
        # カテゴリ選択グループ
        # ------------------------------------
        self. tone_group = SingleSelectGroup(
            self. category_frame,
            title = "トーン",
            options = ["ビビッド", "ネオン", "くすみ", "パステル"]
        )

        self. era_group = SingleSelectGroup(
            self. category_frame,
            title = "年代",
            options = ["70's", "80's", "90's", "00's"]
        )

        self. season_group = SingleSelectGroup(
            self. category_frame,
            title = "季節",
            options = ["春", "夏", "秋", "冬"]
        )

        # ------------------------------------
        # 「このチョイスで調べる」文言＋GOボタン
        # ------------------------------------
        self. category_go_btn = self. build_go_section(
            self. category_frame,
            "このチョイスで調べる",
            self. on_category_go
        )


        self. space()


        # ======================================
        # プリセット
        # ======================================

        self. preset_frame = ctk. CTkFrame(
            self. scroll,
            fg_color = "white"
        )

        self. preset_frame. pack(
            fill = "x",
            pady = 10
        )

        # 上ライン
        self. section_line(self. preset_frame)

        ctk. CTkLabel(
            self. preset_frame,
            text = "プリセット",
            font = ("あめふりドロップス無料版", 22, "bold")
        ). pack(anchor="w", padx=15)

        # 下ライン
        self. section_line(self. preset_frame)


# ======================================
# プリセット機能
# ====================================== 
        # 仮の3色(ダミー、後で実際のGO!ボタンの結果に差し替え予定)
        self. dummy_palette = ["#ff6f9f", "#a5e6f8", "#e6a5f8"]

        # 6枠分のデータ(colorsがNoneのうちは「まだ登録されていない」枠)
        self. preset_data = [
            {"colors": None, "name": ""} for _ in range(6)
        ]

        self. current_preset_page = 0

        # タブ(1〜6)の行
        self. preset_tab_buttons = []

        preset_tab_row = ctk. CTkFrame(
            self. preset_frame,
            fg_color = "transparent"
        )
        preset_tab_row. pack(fill = "x", padx = 15, pady = (10, 0))

        for i in range(6):
            tab_btn = ctk. CTkButton(
                preset_tab_row,
                text = str(i + 1),
                width = 40,
                corner_radius = 0,
                fg_color = "white",
                hover_color = "#f0d9f5",
                text_color = "#555555",
                border_width = 1,
                border_color = "#d0d0d0",
                command = lambda i = i: self. switch_preset_page(i)
            )
            tab_btn. pack(side = "left")

            self. preset_tab_buttons. append(tab_btn)

        # ページの中身を入れる箱(タブを押すたびにこの中を描き直す)
        self. preset_content_frame = ctk. CTkFrame(
            self. preset_frame,
            fg_color = "white",
            border_width = 1,
            border_color = "#d0d0d0"
        )
        self. preset_content_frame. pack(fill = "x", padx = 15, pady = (0, 15))

        # 初期表示(1ページ目)
        self. switch_preset_page(0)


        self. space()


        # ======================================
        # ラッキーカラー
        # ======================================

        self. recommend_frame = ctk. CTkFrame(
            self. scroll,
            fg_color = "white"
        )

        self. recommend_frame. pack(
            fill = "x",
            pady = 10
        )

        # 上ライン
        self. section_line(self. recommend_frame)

        ctk. CTkLabel(
            self. recommend_frame,
            text = "ラッキーカラー",
            font = ("あめふりドロップス無料版", 22, "bold")
        ). pack()

        # 下ライン
        self. section_line(self. recommend_frame)


        # 工事中画像差し込み
        ctk. CTkLabel(
            self. recommend_frame,
            text = "",
            image = self. prep_image
        ). pack(pady = 10)


        self. space()
        

#=============クラス直下（__init__の外）のものはここに

    # ======================================
    # セクション用の区切り線（1本）
    # ======================================
    def section_line(self, parent):
        line = tk. Canvas(
            parent,
            height = 1,
            bg = "white",
            highlightthickness = 0
        )
        line. create_line(
            0, 0, 1000, 0,
            fill = "#d0d0d0",
            width = 1
        )
        line. pack(fill = "x", padx = 10)


    # ======================================
    # スポイト機能
    # ======================================
    def start_eyedropper(self):

        # 既に開いている場合は多重生成を防ぐ
        if hasattr(self, "overlay") and self. overlay. winfo_exists():
            return

        self. overlay = tk. Toplevel(self)
        self. overlay. attributes("-alpha", 0.01)   # ほぼ透明
        self. overlay. attributes("-topmost", True)
        self. overlay. overrideredirect(True)
        self. overlay. configure(cursor = "crosshair")

        # 全モニタ分の仮想デスクトップサイズを取得して覆う
        vx = self. winfo_vrootx()
        vy = self. winfo_vrooty()
        vw = self. winfo_vrootwidth()
        vh = self. winfo_vrootheight()

        self. overlay. geometry(f"{vw}x{vh}+{vx}+{vy}")

        self. overlay. bind("<Motion>", self. preview_color)
        self. overlay. bind("<Button-1>", self. pick_color)
        self. overlay. bind("<Escape>", self. cancel_eyedropper)

        self. overlay. focus_force()


    def get_pixel_color(self, x, y):

        # all_screens=True でマルチモニタに対応
        screenshot = ImageGrab. grab(bbox = (x, y, x + 1, y + 1), all_screens = True)
        rgb = screenshot. getpixel((0, 0))

        return "#{:02x}{:02x}{:02x}". format(*rgb[:3])


    def preview_color(self, event):

        # マウスが動くたびに呼ばれる（確定はしない）
        hex_color = self. get_pixel_color(event.x_root, event.y_root)

        self. hex_entry. delete(0, "end")
        self. hex_entry. insert(0, hex_color)
        self. color_preview. configure(fg_color = hex_color)
        self. update_preview_border(hex_color)
        self. sync_picker_from_hex(hex_color)

    
    def pick_color(self, event):

        # 左クリックされた瞬間に呼ばれる（確定する）
        hex_color = self. get_pixel_color(event.x_root, event.y_root)

        self. apply_color(hex_color)
        self. sync_picker_from_hex(hex_color)
        self. overlay. destroy()


    def cancel_eyedropper(self, event = None):

        self. overlay. destroy()


    # ======================================
    # コピー処理
    # ======================================
    def copy_hex_code(self):

        value = self. hex_entry. get(). strip()

        self. clipboard_clear()
        self. clipboard_append(value)
        self. update()


    # ======================================
    # プリセット：色ごとのコピー処理
    # ======================================
    def copy_preset_color(self, color):

        self. clipboard_clear()
        self. clipboard_append(color)
        self. update()

    # ======================================
    # カラーコード反映
    # ======================================
    def apply_color(self, hex_color):

        self. current_hex = hex_color

        self. hex_entry. delete(0, "end")
        self. hex_entry. insert(0, hex_color)

        self. color_preview. configure(fg_color = hex_color)
        self. update_preview_border(hex_color)

    def on_hex_entry_enter(self, event = None):

        value = self. hex_entry. get(). strip()

        if not value. startswith("#"):
            value = "#" + value

        # #RRGGBB形式かどうかの簡易チェック
        if len(value) == 7:
            try:
                int(value[1:], 16)
                self. apply_color(value)
                self. sync_picker_from_hex(value)
            except ValueError:
                print("無効なカラーコードです")
        else:
            print("無効なカラーコードです")


    # ======================================
    # 色プレビュー：白い時だけ縁をつける
    # ======================================
    def update_preview_border(self, hex_color):

        if hex_color.lower() == "#ffffff":
            self. color_preview. configure(border_width = 1, border_color = "black")
        else:
            self. color_preview. configure(border_width = 0)


    # ======================================
    # カラーピッカー：リング画像の生成
    # ======================================
    def build_color_wheel_image(self, size=190, thickness=22):

        image = Image. new("RGBA", (size, size), (0, 0, 0, 0))
        cx = cy = size / 2
        outer_r = size / 2
        inner_r = outer_r - thickness

        for y in range(size):
            for x in range(size):
                dx = x - cx
                dy = y - cy
                r = math. hypot(dx, dy)

                if inner_r <= r <= outer_r:
                    angle_cw = math. degrees(math. atan2(dx, -dy)) % 360
                    hue = (1 - angle_cw / 360) % 1

                    red, green, blue = colorsys. hsv_to_rgb(hue, 1, 1)

                    image. putpixel(
                        (x, y),
                        (int(red * 255), int(green * 255), int(blue * 255), 255)
                    )

        return image


    # ======================================
    # カラーピッカー：四角（彩度・明度）画像の生成
    # ======================================
    def build_sv_square_image(self, hue, size = 90):

        image = Image. new("RGB", (size, size))

        for y in range(size):
            value = 1 - (y / (size - 1))

            for x in range(size):
                sat = x / (size - 1)

                red, green, blue = colorsys. hsv_to_rgb(hue, sat, value)

                image. putpixel(
                    (x, y),
                    (int(red * 255), int(green * 255), int(blue * 255))
                )

        return image


    # ======================================
    # カラーピッカー：四角を描き直す（色相が変わった時）
    # ======================================
    def draw_sv_square(self):

        square_img = self. build_sv_square_image(self. current_hue, self. square_size)
        self. square_photo = ImageTk. PhotoImage(square_img)

        center = self. wheel_size / 2

        if self. square_image_id is None:
            self. square_image_id = self. wheel_canvas. create_image(
                center, center,
                image = self. square_photo,
                anchor = "center"
            )
        else:
            self. wheel_canvas. itemconfig(self. square_image_id, image = self. square_photo)


    # ======================================
    # カラーピッカー：クリック処理
    # ======================================
    def on_wheel_click(self, event):

        cx = cy = self. wheel_size / 2
        dx = event. x - cx
        dy = event. y - cy
        r = math. hypot(dx, dy)

        outer_r = self. wheel_size / 2
        inner_r = outer_r - self. wheel_thickness

        if inner_r <= r <= outer_r:
            # リング部分：色相を変更
            angle_cw = math. degrees(math. atan2(dx, -dy)) % 360
            self. current_hue = (1 - angle_cw / 360) % 1

            self. draw_sv_square()
            self. update_color_from_hsv()

        elif r < inner_r:
            # 四角部分：彩度・明度を変更
            half = self. square_size / 2

            local_x = dx + half
            local_y = dy + half

            local_x = max(0, min(self. square_size - 1, local_x))
            local_y = max(0, min(self. square_size - 1, local_y))

            self. current_sat = local_x / (self. square_size - 1)
            self. current_val = 1 - (local_y / (self. square_size - 1))

            self. update_color_from_hsv()

        self.update_indicators()


    # ======================================
    # カラーピッカー：選択位置に白丸を表示
    # ======================================
    def update_indicators(self):

        cx = cy = self. wheel_size / 2

        # --- リング側の白丸 ---
        outer_r = self. wheel_size / 2
        inner_r = outer_r - self. wheel_thickness
        mid_r = (inner_r + outer_r) / 2

        angle_cw = (1 - self. current_hue) * 360
        rad = math. radians(angle_cw)

        ring_x = cx + mid_r * math. sin(rad)
        ring_y = cy - mid_r * math. cos(rad)

        ring_radius = 6

        if self. ring_indicator_id is None:
            self. ring_indicator_id = self. wheel_canvas. create_oval(
                ring_x - ring_radius, ring_y - ring_radius,
                ring_x + ring_radius, ring_y + ring_radius,
                outline = "white", width = 2
            )
        else:
            self. wheel_canvas. coords(
                self. ring_indicator_id,
                ring_x - ring_radius, ring_y - ring_radius,
                ring_x + ring_radius, ring_y + ring_radius
            )
            self. wheel_canvas. tag_raise(self. ring_indicator_id)

        # --- 四角側の白丸 ---
        half = self. square_size / 2

        local_x = self. current_sat * (self. square_size - 1)
        local_y = (1 - self. current_val) * (self. square_size - 1)

        square_x = cx - half + local_x
        square_y = cy - half + local_y

        square_radius = 5

        if self. square_indicator_id is None:
            self. square_indicator_id = self. wheel_canvas. create_oval(
                square_x - square_radius, square_y - square_radius,
                square_x + square_radius, square_y + square_radius,
                outline = "white", width = 2
            )
        else:
            self. wheel_canvas. coords(
                self. square_indicator_id,
                square_x - square_radius, square_y - square_radius,
                square_x + square_radius, square_y + square_radius
            )
            self. wheel_canvas. tag_raise(self. square_indicator_id)


    # ======================================
    # HEX → HSV 変換
    # ======================================
    def hex_to_hsv(self, hex_color):

        hex_color = hex_color. lstrip("#")
        r = int(hex_color[0:2], 16) / 255
        g = int(hex_color[2:4], 16) / 255
        b = int(hex_color[4:6], 16) / 255

        return colorsys. rgb_to_hsv(r, g, b)


    # ======================================
    # HEXの色にピッカーの丸を同期させる
    # ======================================
    def sync_picker_from_hex(self, hex_color):

        h, s, v = self. hex_to_hsv(hex_color)

        self. current_hue = h
        self. current_sat = s
        self. current_val = v

        self. draw_sv_square()
        self. update_indicators()


    # ======================================
    # カラーピッカー：HSVから最終カラーを反映
    # ======================================
    def update_color_from_hsv(self):

        red, green, blue = colorsys. hsv_to_rgb(
            self. current_hue,
            self. current_sat,
            self. current_val
        )

        hex_color = "#{:02x}{:02x}{:02x}". format(
            int(red * 255), int(green * 255), int(blue * 255)
        )

        self. apply_color(hex_color)


    # ======================================
    # 「〇〇で調べる」文言＋GOボタンを1組作る
    # ======================================
    def build_go_section(self, parent, label_text, command):

        ctk. CTkLabel(
            parent,
            text = label_text,
            font = ("ふてほど丸ゴシック", 14),
            text_color = "#555555"
        ). pack(pady = (20, 8))

        btn = ctk. CTkButton(
            parent,
            text = "GO!",
            width = 100,
            corner_radius = 50,
            fg_color = "#ff6f6f",
            hover_color = "#e35555",
            text_color = "white",
            font = ("ふてほど丸ゴシック", 16, "bold"),
            command = command
        )
        btn. pack(pady = (0, 15))

        return btn


    # ======================================
    # 「この色で調べる」ボタンの処理（仮）
    # ======================================
    def on_select_go(self):

        print(f"この色で調べる: {self. current_hex}")


    # ======================================
    # セレクトの色を初期状態(白)に戻す
    # ======================================
    def reset_select(self):

        self. apply_color("#FFFFFF")
        self. sync_picker_from_hex("#FFFFFF")


    # ======================================
    # 「このチョイスで調べる」ボタンの処理（仮）
    # ======================================
    def on_category_go(self):

        print("トーン:", self.tone_group.selected)
        print("年代:", self.era_group.selected)
        print("季節:", self.season_group.selected)


    # ======================================
    # プリセット：表示するページを切り替える
    # ======================================
    def switch_preset_page(self, index):

        self. current_preset_page = index

        # タブの見た目を更新(選択中だけ可愛い色、他は白)
        for i, btn in enumerate(self. preset_tab_buttons):
            if i == index:
                btn. configure(fg_color = "#ff9fd0", text_color = "white")
            else:
                btn. configure(fg_color = "white", text_color = "#555555")

        self. render_preset_page()


    # ======================================
    # プリセット：現在のページの中身を描き直す
    # ======================================
    def render_preset_page(self):

        for widget in self. preset_content_frame. winfo_children():
            widget. destroy()

        data = self. preset_data[self. current_preset_page]

        # 登録済みならその色、まだなら仮の3色(候補)を表示
        colors = data["colors"] if data["colors"] is not None else self. dummy_palette

        # ------------------------------------
        # 上段：📷 スクショボタン ＋ 🗑️ 削除ボタン(右寄せ)
        # ------------------------------------
        top_row = ctk. CTkFrame(self. preset_content_frame, fg_color = "transparent")
        top_row. pack(fill = "x", padx = 10, pady = (10, 0))

        delete_btn = ctk. CTkButton(
            top_row,
            text = "🗑",
            width = 40,
            height = 32,
            corner_radius = 50,
            fg_color = "#dddddd",
            hover_color = "#cccccc",
            text_color = "black",
            anchor = "center",
            command = self. delete_current_preset
        )
        delete_btn. pack(side = "right", padx = (5, 0))

        ToolTip(delete_btn, "削除")

        camera_btn = ctk. CTkButton(
            top_row,
            text = "📷",
            width = 40,
            height = 32,
            corner_radius = 50,
            fg_color = "#dddddd",
            hover_color = "#cccccc",
            text_color = "black",
            anchor = "center",
            command = self. screenshot_current_preset
        )
        camera_btn. pack(side = "right")

        ToolTip(camera_btn, "スクショを撮る")

        # ------------------------------------
        # 名前欄 ＋ ✏️ 登録ボタン
        # ------------------------------------
        name_row = ctk. CTkFrame(self. preset_content_frame, fg_color = "transparent")
        name_row. pack(fill = "x", padx = 10, pady = (5, 10))

        ctk. CTkLabel(
            name_row,
            text = "名前",
            font = ("ふてほど丸ゴシック", 14),
            text_color = "#555555"
        ). pack(side = "left", padx = (0, 5))

        self. preset_name_entry = ctk. CTkEntry(
            name_row,
            width = 150,
            placeholder_text = "NoTitle",
            placeholder_text_color = "#dddddd"
        )
        self. preset_name_entry. pack(side = "left")

        if data["name"]:
            self. preset_name_entry. insert(0, data["name"])

        register_btn = ctk. CTkButton(
            name_row,
            text = "✏",
            width = 20,
            height = 28,
            corner_radius = 50,
            fg_color = "#e6a5f8",
            hover_color = "#866091",
            text_color = "white",
            anchor = "center",
            command = self. register_current_preset
        )
        register_btn. pack(side = "left", padx = (5, 0))

        ToolTip(register_btn, "名前を登録")

        # ------------------------------------
        # 3色スウォッチ
        # ------------------------------------
        self. preset_swatch_row = ctk. CTkFrame(self. preset_content_frame, fg_color = "transparent")
        self. preset_swatch_row. pack(pady = (5, 5))

        for color in colors:
            ctk. CTkLabel(
                self. preset_swatch_row,
                text = "",
                width = 80,
                height = 80,
                corner_radius = 8,
                fg_color = color
            ). pack(side = "left", padx = 5)

        # ------------------------------------
        # カラーコード表示 ＋ コピーボタン(色ごとに1組)
        # ------------------------------------
        code_row = ctk. CTkFrame(self. preset_content_frame, fg_color = "transparent")
        code_row. pack(pady = (0, 10))

        for color in colors:
            code_col = ctk. CTkFrame(code_row, width = 80, height = 30, fg_color = "transparent")
            code_col. pack_propagate(False)
            code_col. pack(side = "left", padx = 5)

            inner = ctk. CTkFrame(code_col, fg_color = "transparent")
            inner. pack(expand = True)

            ctk. CTkLabel(
                inner,
                text = color. upper(),
                font = ("ふてほど丸ゴシック", 11),
                text_color = "#555555"
            ). pack(side = "left")

            copy_btn = ctk. CTkButton(
                inner,
                text = "📝",
                width = 24,
                height = 24,
                corner_radius = 50,
                fg_color = "#e6a5f8",
                hover_color = "#866091",
                text_color = "white",
                command = lambda c = color. upper(): self. copy_preset_color(c)
            )
            copy_btn. pack(side = "left", padx = (3, 0))

            ToolTip(copy_btn, "コピーする")


    # ======================================
    # プリセット：名前と(仮の)3色を現在のページに登録する
    # ======================================
    def register_current_preset(self):

        name = self. preset_name_entry. get(). strip()

        self. preset_data[self. current_preset_page] = {
            "colors": list(self. dummy_palette),
            "name": name
        }

        self. render_preset_page()


    # ======================================
    # プリセット：現在のページを削除(未登録状態に戻す)
    # ======================================
    def delete_current_preset(self):

        self. preset_data[self. current_preset_page] = {"colors": None, "name": ""}
        self. render_preset_page()


    # ======================================
    # プリセット：現在の3色をスクリーンショットして保存
    # ======================================
    def screenshot_current_preset(self):

        self. update()

        x = self. preset_swatch_row. winfo_rootx()
        y = self. preset_swatch_row. winfo_rooty()
        w = self. preset_swatch_row. winfo_width()
        h = self. preset_swatch_row. winfo_height()

        screenshot = ImageGrab. grab(bbox = (x, y, x + w, y + h), all_screens = True)

        file_path = filedialog. asksaveasfilename(
            defaultextension = ".png",
            filetypes = [("PNG画像", "*.png")],
            initialfile = "palette.png"
        )

        if file_path:
            screenshot. save(file_path)


    # ======================================
    # 空白スペース
    # ======================================
    def space(self):

        spacer = ctk. CTkFrame(
            self. scroll,
            height = 70,
            fg_color = "transparent"
        )

        spacer. pack()


    # ======================================
    # 工事中画像の読み込み
    # ======================================
    def load_preparation_image(self):

        image = Image. open("images/preparation.png")
        image = image. resize((380, 600))

        return ctk. CTkImage(
            light_image = image,
            dark_image = image,
            size = (380, 600)
        )


#=============クラス直下（__init__の外）のものはここまで


    # ======================================
    # ホームへ戻る
    # ======================================
    def go_home(self):

        self. scroll. _parent_canvas. yview_moveto(0)

        #ホームボタン押すと全部リセットする
        self. reset_select()
        self. tone_group. reset()
        self. era_group. reset()
        self. season_group. reset()


    # ======================================
    # スクロール移動処理
    # ======================================
    def move_scroll(self, target):

        self. update()

        y = target. winfo_y()

        self. scroll. _parent_canvas. yview_moveto(
            y / self. scroll. _parent_canvas. bbox("all")[3]
        )



    def scroll_select(self):
        self. move_scroll(self. select_frame)


    def scroll_category(self):
        self. move_scroll(self. category_frame)


    def scroll_preset(self):
        self. move_scroll(self. preset_frame)


    def scroll_recommend(self):
        self. move_scroll(self. recommend_frame)



# ======================================
# アプリ起動
# ======================================
app = App()
app. mainloop()