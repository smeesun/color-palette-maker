import customtkinter as ctk
import tkinter as tk
from PIL import ImageGrab
import sqlite3


# ======================================
# テーマ設定
# ======================================
ctk. set_appearance_mode("Light")
ctk. set_default_color_theme("blue")


# ======================================
# ツールチップ(COLpama本体と同じもの)
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
# タググループ(既存選択肢＋その他＋新規追加)
# ======================================
class TagGroup:

    def __init__(self, parent, title, options, font_name = "ふてほど丸ゴシック"):

        self. selected = None
        self. buttons = {}
        self. font_name = font_name

        ctk. CTkLabel(
            parent,
            text = f"-{title}-",
            font = (font_name, 16, "bold"),
            text_color = "#555555"
        ). pack(anchor = "w", padx = 15, pady = (15, 5))

        self. row = ctk. CTkFrame(parent, fg_color = "transparent")
        self. row. pack(anchor = "w", padx = 15, pady = (0, 5))

        # 既存の選択肢を先に並べる
        for option in options:
            self. add_option_button(option)

        # 「その他」固定ボタン
        self. other_btn = ctk. CTkButton(
            self. row,
            text = "その他",
            width = 70,
            corner_radius = 50,
            fg_color = "#e6a5f8",
            hover_color = "#866091",
            text_color = "white",
            font = (font_name, 14),
            command = lambda: self. select("その他")
        )
        self. other_btn. pack(side = "left", padx = 5)
        self. buttons["その他"] = self. other_btn

        # 「新規」入力欄(常に一番右端)
        self. new_entry = ctk. CTkEntry(
            self. row,
            width = 70,
            placeholder_text = "新規",
            placeholder_text_color = "#dddddd"
        )
        self. new_entry. pack(side = "left", padx = 5)


    # ======================================
    # 選択肢ボタンを1つ追加する(「その他」より前に挿入)
    # ======================================
    def add_option_button(self, option):

        btn = ctk. CTkButton(
            self. row,
            text = option,
            width = 70,
            corner_radius = 50,
            fg_color = "#e6a5f8",
            hover_color = "#866091",
            text_color = "white",
            font = (self. font_name, 14),
            command = lambda o = option: self. select(o)
        )

        if hasattr(self, "other_btn"):
            btn. pack(side = "left", padx = 5, before = self. other_btn)
        else:
            btn. pack(side = "left", padx = 5)

        self. buttons[option] = btn


    def select(self, option):

        if self. selected == option:
            return

        if self. selected is not None:
            self. buttons[self. selected]. configure(
                fg_color = "#e6a5f8",
                hover_color = "#866091",
                text_color = "white"
            )

        self. selected = option

        self. buttons[option]. configure(
            fg_color = "#ff6f9f",
            hover_color = "#ff6f9f",
            text_color = "white"
        )


    def reset(self):

        for btn in self. buttons. values():
            btn. configure(
                fg_color = "#e6a5f8",
                hover_color = "#866091",
                text_color = "white"
            )

        self. selected = None
        self. new_entry. delete(0, "end")


    # ======================================
    # 「新規」欄に入力があればボタン化して選択状態にする
    # 戻り値: このグループで実際に使うタグ名
    # ======================================
    def apply_new_tag_if_any(self):

        new_text = self. new_entry. get(). strip()

        if new_text:
            if new_text not in self. buttons:
                self. add_option_button(new_text)

            self. select(new_text)

        return self. selected


# ======================================
# データ登録ツール本体
# ======================================
class DataEntryApp(ctk. CTk):

    def __init__(self):
        super(). __init__()

        self. geometry("420x750")
        self. title("COLpama データ登録ツール")
        self. configure(fg_color = "#3b1d35")

        # ------------------------------------
        # SQLite接続(COLpama本体と同じファイルを使う)
        # ------------------------------------
        self. conn = sqlite3. connect("colpama.db")
        self. cursor = self. conn. cursor()

        self. cursor. execute("""
            CREATE TABLE IF NOT EXISTS presets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                base_hex TEXT,
                base_pct INTEGER,
                accent_hex TEXT,
                accent_pct INTEGER,
                sub_hex TEXT,
                sub_pct INTEGER,
                tags TEXT
            )
        """)
        self. conn. commit()

        self. registered_count = self. get_current_count()

        # ------------------------------------
        # スクロールエリア
        # ------------------------------------
        self. scroll = ctk. CTkScrollableFrame(self, fg_color = "white")
        self. scroll. pack(fill = "both", expand = True, padx = 10, pady = 10)

        # 登録件数表示
        self. count_label = ctk. CTkLabel(
            self. scroll,
            text = f"登録済み: {self. registered_count}件",
            font = ("ふてほど丸ゴシック", 14),
            text_color = "#555555"
        )
        self. count_label. pack(pady = (0, 10))

        # 名前欄
        ctk. CTkLabel(
            self. scroll,
            text = "名前",
            font = ("ふてほど丸ゴシック", 14)
        ). pack(anchor = "w", padx = 10)

        self. name_entry = ctk. CTkEntry(self. scroll, width = 200, placeholder_text = "NoTitle")
        self. name_entry. pack(anchor = "w", padx = 10, pady = (0, 15))

        # 3色分の入力欄(ベース/アクセント/サブ)
        self. color_widgets = {}

        self. build_color_row("base", "ベース", 70)
        self. build_color_row("accent", "アクセント", 10)
        self. build_color_row("sub", "サブ", 20)

        # タグ選択
        self. tone_group = TagGroup(self. scroll, "トーン", ["ビビッド", "ネオン", "くすみ", "パステル"])
        self. era_group = TagGroup(self. scroll, "年代", ["70's", "80's", "90's", "00's"])
        self. season_group = TagGroup(self. scroll, "季節", ["春", "夏", "秋", "冬"])

        # 登録ボタン
        self. register_btn = ctk. CTkButton(
            self. scroll,
            text = "この配色を登録",
            width = 200,
            corner_radius = 50,
            fg_color = "#ff6f6f",
            hover_color = "#e35555",
            text_color = "white",
            font = ("ふてほど丸ゴシック", 16, "bold"),
            command = self. register_entry
        )
        self. register_btn. pack(pady = 20)


    # ======================================
    # 現在の登録件数を取得
    # ======================================
    def get_current_count(self):

        self. cursor. execute("SELECT COUNT(*) FROM presets")
        return self. cursor. fetchone()[0]


    # ======================================
    # 比率を決定する(手打ち欄があればそちらを優先)
    # ======================================
    def get_pct(self, key):

        widgets = self. color_widgets[key]
        override = widgets["override_entry"]. get(). strip()

        if override:
            try:
                return int(override)
            except ValueError:
                print("比率は数字で入力してください")
                return widgets["default_pct"]

        return widgets["default_pct"]


    # ======================================
    # 色1つぶんの入力欄(スポイト＋コード欄＋比率)を作る
    # ======================================
    def build_color_row(self, key, label_text, default_pct):

        row = ctk. CTkFrame(self. scroll, fg_color = "transparent")
        row. pack(fill = "x", padx = 10, pady = 5)

        ctk. CTkLabel(
            row,
            text = label_text,
            width = 60,
            font = ("ふてほど丸ゴシック", 14),
            text_color = "#555555"
        ). pack(side = "left")

        eyedropper_btn = ctk. CTkButton(
            row,
            text = "💉",
            width = 36,
            corner_radius = 50,
            fg_color = "#e6a5f8",
            hover_color = "#866091",
            text_color = "white",
            command = lambda k = key: self. start_eyedropper(k)
        )
        eyedropper_btn. pack(side = "left", padx = 5)

        ToolTip(eyedropper_btn, "スポイト")

        hex_entry = ctk. CTkEntry(row, width = 90, placeholder_text = "#FFFFFF")
        hex_entry. pack(side = "left", padx = 5)
        hex_entry. bind("<Return>", lambda e, k = key: self. on_hex_entry_enter(k))

        preview = ctk. CTkLabel(
            row,
            text = "",
            width = 30,
            height = 30,
            corner_radius = 6,
            fg_color = "#FFFFFF"
        )
        preview. pack(side = "left", padx = 5)

        # 既定の比率(コード欄のすぐ右隣に表示、固定値)
        ctk. CTkLabel(
            row,
            text = f"{default_pct}%",
            width = 40,
            font = ("ふてほど丸ゴシック", 13),
            text_color = "#555555"
        ). pack(side = "left", padx = 5)

        # 手打ちで上書きしたい時だけ使う欄(一番右端、優先される)
        override_entry = ctk. CTkEntry(row, width = 50, placeholder_text = "%指定")
        override_entry. pack(side = "left", padx = 5)

        self. color_widgets[key] = {
            "hex_entry": hex_entry,
            "preview": preview,
            "default_pct": default_pct,
            "override_entry": override_entry
        }


    # ======================================
    # スポイト機能(COLpama本体と同じ仕組み)
    # ======================================
    def start_eyedropper(self, key):

        if hasattr(self, "overlay") and self. overlay. winfo_exists():
            return

        self. eyedropper_target = key

        self. overlay = tk. Toplevel(self)
        self. overlay. attributes("-alpha", 0.01)
        self. overlay. attributes("-topmost", True)
        self. overlay. overrideredirect(True)
        self. overlay. configure(cursor = "crosshair")

        vx = self. winfo_vrootx()
        vy = self. winfo_vrooty()
        vw = self. winfo_vrootwidth()
        vh = self. winfo_vrootheight()

        self. overlay. geometry(f"{vw}x{vh}+{vx}+{vy}")

        self. overlay. bind("<Button-1>", self. pick_color)
        self. overlay. bind("<Escape>", self. cancel_eyedropper)

        self. overlay. focus_force()


    def pick_color(self, event):

        screenshot = ImageGrab. grab(
            bbox = (event. x_root, event. y_root, event. x_root + 1, event. y_root + 1),
            all_screens = True
        )
        rgb = screenshot. getpixel((0, 0))
        hex_color = "#{:02x}{:02x}{:02x}". format(*rgb[:3])

        self. apply_color(self. eyedropper_target, hex_color)
        self. overlay. destroy()


    def cancel_eyedropper(self, event = None):

        self. overlay. destroy()


    # ======================================
    # 色を反映する(スポイト・手入力共通)
    # ======================================
    def apply_color(self, key, hex_color):

        widgets = self. color_widgets[key]

        widgets["hex_entry"]. delete(0, "end")
        widgets["hex_entry"]. insert(0, hex_color)
        widgets["preview"]. configure(fg_color = hex_color)


    def on_hex_entry_enter(self, key):

        value = self. color_widgets[key]["hex_entry"]. get(). strip()

        if not value. startswith("#"):
            value = "#" + value

        if len(value) == 7:
            try:
                int(value[1:], 16)
                self. apply_color(key, value)
            except ValueError:
                print("無効なカラーコードです")


    # ======================================
    # 入力内容をSQLiteに登録する
    # ======================================
    def register_entry(self):

        name = self. name_entry. get(). strip() or "NoTitle"

        base_hex = self. color_widgets["base"]["hex_entry"]. get(). strip()
        accent_hex = self. color_widgets["accent"]["hex_entry"]. get(). strip()
        sub_hex = self. color_widgets["sub"]["hex_entry"]. get(). strip()

        if not (base_hex and accent_hex and sub_hex):
            print("3色すべて入力してください")
            return

        base_pct = self. get_pct("base")
        accent_pct = self. get_pct("accent")
        sub_pct = self. get_pct("sub")

        # 新規タグがあればボタン化してから、実際に使うタグ名を取得
        tone_tag = self. tone_group. apply_new_tag_if_any()
        era_tag = self. era_group. apply_new_tag_if_any()
        season_tag = self. season_group. apply_new_tag_if_any()

        tags = ",". join(filter(None, [tone_tag, era_tag, season_tag]))

        self. cursor. execute("""
            INSERT INTO presets (name, base_hex, base_pct, accent_hex, accent_pct, sub_hex, sub_pct, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, base_hex, base_pct, accent_hex, accent_pct, sub_hex, sub_pct, tags))

        self. conn. commit()

        self. registered_count += 1
        self. count_label. configure(text = f"登録済み: {self. registered_count}件")

        self. clear_form()


    # ======================================
    # 次の1件を入力しやすいようにフォームをリセット
    # ======================================
    def clear_form(self):

        self. name_entry. delete(0, "end")

        for key in self. color_widgets:
            self. color_widgets[key]["hex_entry"]. delete(0, "end")
            self. color_widgets[key]["preview"]. configure(fg_color = "#FFFFFF")
            self. color_widgets[key]["override_entry"]. delete(0, "end")

        self. tone_group. reset()
        self. era_group. reset()
        self. season_group. reset()


app = DataEntryApp()
app. mainloop()