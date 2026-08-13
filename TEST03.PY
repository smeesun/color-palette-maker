import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageGrab, ImageTk, ImageDraw
import colorsys
import math
import sqlite3
import random


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

        # アプリのウィンドウ右端からはみ出る場合は、その分だけ左にずらす
        tw. update_idletasks()
        tip_width = tw. winfo_width()

        root = self. widget. winfo_toplevel()
        window_right = root. winfo_rootx() + root. winfo_width()

        if x + tip_width > window_right:
            x = window_right - tip_width - 10

        tw. wm_geometry(f"+{x}+{y}")


    def hide_tip(self, event = None):

        if self. tip_window:
            self. tip_window. destroy()
            self. tip_window = None


# ======================================
# 単一選択ボタングループ
# ======================================
class SingleSelectGroup:

    def __init__(self, parent, title, options, font_name="ふてほど丸ゴシック", on_change=None, display_labels=None):

        self. selected = None
        self. buttons = {}
        self. disabled_options = set()
        self. on_change = on_change
        self. font_name = font_name
        self. display_labels = display_labels or {}

        ctk. CTkLabel(
            parent,
            text = f"-{title}-",
            font = (font_name, 16, "bold"),
            text_color = "#555555"
        ). pack(anchor = "w", padx = 15, pady = (15, 5))

        # ------------------------------------
        # 固定の選択肢(4個ごとに折り返す。1行に詰め込みすぎるとボタンが
        # ウィンドウ幅からはみ出るため)
        # ------------------------------------
        self. option_area = ctk. CTkFrame(parent, fg_color = "transparent")
        self. option_area. pack(anchor = "w", padx = 15, pady = (0, 3))

        self. option_count = 0
        self. current_option_row = None

        for option in options:
            self. add_option_button(option)

        # ------------------------------------
        # データ登録ツール側で追加されたカスタムタグ専用エリア(4個ごとに折り返す)
        # カスタムタグが1つも無いカテゴリだと中身が空のままになるが、CTkFrameは
        # width/height未指定だと空でも200×200pxのデフォルトサイズを確保してしまうため、
        # 明示的にheightを指定しておく(中身が増えれば自動で広がる)
        # ------------------------------------
        self. extra_area = ctk. CTkFrame(parent, fg_color = "transparent", height = 1)
        self. extra_area. pack(anchor = "w", padx = 15, pady = (0, 3))

        self. extra_count = 0
        self. current_extra_row = None

        # ------------------------------------
        # 「その他」はカスタムタグより後ろ、常に一番最後に来るように別枠にする
        # ------------------------------------
        self. other_area = ctk. CTkFrame(parent, fg_color = "transparent")
        self. other_area. pack(anchor = "w", padx = 15, pady = (0, 5))

        self. add_button(self. other_area, "その他")


    # ======================================
    # ボタンを1つ作って、指定した行(parent_row)に配置する
    # 表示ラベルはdisplay_labelsに指定があればそちらを使う(選択される値は常にoption)
    # ======================================
    def add_button(self, parent_row, option):

        btn = ctk. CTkButton(
            parent_row,
            text = self. display_labels. get(option, option),
            width = 64,
            corner_radius = 50,
            fg_color = "#e6a5f8",
            hover_color = "#866091",
            text_color = "white",
            font = (self. font_name, 13),
            command = lambda o = option: self. select(o)
        )
        btn. pack(side = "left", padx = 3)

        self. buttons[option] = btn

        return btn


    # ======================================
    # 固定の選択肢を1つ追加する(4個ごとに折り返す)
    # ======================================
    def add_option_button(self, option):

        if self. option_count % 4 == 0:
            self. current_option_row = ctk. CTkFrame(self. option_area, fg_color = "transparent")
            self. current_option_row. pack(anchor = "w", pady = (0, 3))

        self. add_button(self. current_option_row, option)
        self. option_count += 1


    # ======================================
    # データ登録ツールで追加されたカスタムタグのボタンを1つ追加する(4個たまるごとに新しい行を作る)
    # ======================================
    def add_extra_option(self, text):

        if text in self. buttons:
            return

        if self. extra_count % 4 == 0:
            self. current_extra_row = ctk. CTkFrame(self. extra_area, fg_color = "transparent")
            self. current_extra_row. pack(anchor = "w", pady = (0, 3))

        self. add_button(self. current_extra_row, text)
        self. extra_count += 1


    def select(self, option):

        # グレーアウト中のボタンは押せない
        if option in self. disabled_options:
            return

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

        if self. on_change is not None:
            self. on_change()

    # ======================================
    # グループを初期状態(未選択・グレーアウトなし)に戻す
    # ======================================
    def reset(self):

        for btn in self. buttons. values():
            btn. configure(
                state = "normal",
                fg_color = "#e6a5f8",
                hover_color = "#866091",
                text_color = "white"
            )

        self. selected = None
        self. disabled_options = set()


    # ======================================
    # 選択だけを解除する(グレーアウト状態には触れない、カテゴリ連動で使う)
    # ======================================
    def clear_selection(self):

        if self. selected is not None:
            prev = self. selected
            self. selected = None

            self. buttons[prev]. configure(
                fg_color = "#e6a5f8",
                hover_color = "#866091",
                text_color = "white"
            )


    # ======================================
    # 1つのボタンを有効／グレーアウトに切り替える(カテゴリ連動で使う)
    # ======================================
    def set_enabled(self, option, enabled):

        if enabled:
            self. disabled_options. discard(option)

            if self. selected == option:
                self. buttons[option]. configure(
                    state = "normal",
                    fg_color = "#ff6f9f",
                    hover_color = "#ff6f9f",
                    text_color = "white"
                )
            else:
                self. buttons[option]. configure(
                    state = "normal",
                    fg_color = "#e6a5f8",
                    hover_color = "#866091",
                    text_color = "white"
                )
        else:
            self. disabled_options. add(option)

            self. buttons[option]. configure(
                state = "disabled",
                fg_color = "#dddddd",
                hover_color = "#dddddd",
                text_color = "#aaaaaa"
            )


    # ======================================
    # グループ内の全ボタンを有効化する(絞り込み条件が無い時に使う)
    # ======================================
    def enable_all(self):

        for option in self. buttons:
            self. set_enabled(option, True)
    


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
        # SQLite接続(データ登録ツールと同じcolpama.dbを参照する)
        # カテゴリの絞り込み(グレーアウト)判定に使う
        # ======================================
        self. conn = sqlite3. connect("colpama.db")
        self. cursor = self. conn. cursor()

        # 自分で保存するプリセット枠(1〜9)を、アプリを閉じても消えないように保存しておくテーブル
        self. cursor. execute("""
            CREATE TABLE IF NOT EXISTS my_preset_slots (
                slot INTEGER PRIMARY KEY,
                name TEXT,
                base_hex TEXT,
                accent_hex TEXT,
                sub_hex TEXT
            )
        """)
        self. conn. commit()

        # 既存のcolpama.dbにregion_tags列が無ければ追加する(カテゴリに「地域」を追加した際の移行措置)
        self. cursor. execute("PRAGMA table_info(presets)")
        existing_columns = {row[1] for row in self. cursor. fetchall()}

        if "region_tags" not in existing_columns:
            self. cursor. execute("ALTER TABLE presets ADD COLUMN region_tags TEXT")
            self. conn. commit()

        # 過去に「トーン」という名前で保存されたカスタムタグを「イメージ」に付け替える(カテゴリ名変更に伴う移行措置)
        self. cursor. execute("UPDATE custom_tags SET group_name = 'イメージ' WHERE group_name = 'トーン'")
        self. conn. commit()


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

        # ------------------------------------
        # 「この色で調べる」の結果画面(普段は非表示、GO!を押した時だけ表示する)
        # ------------------------------------
        self. select_result_frame = ctk. CTkFrame(self, fg_color = "white")

        # ------------------------------------
        # 上段：戻る／大きく見る
        # ------------------------------------
        select_result_top_row = ctk. CTkFrame(self. select_result_frame, fg_color = "transparent")
        select_result_top_row. pack(fill = "x", padx = 10, pady = (10, 0))

        back_from_result_btn = ctk. CTkButton(
            select_result_top_row,
            text = "← 戻る",
            width = 80,
            height = 30,
            corner_radius = 50,
            fg_color = "#e6a5f8",
            hover_color = "#866091",
            text_color = "white",
            font = ("マメロン 5 Hi Regular", 13),
            command = self. close_select_result
        )
        back_from_result_btn. pack(side = "left")

        detail_btn = ctk. CTkButton(
            select_result_top_row,
            text = "🔍",
            width = 40,
            height = 30,
            corner_radius = 50,
            fg_color = "#e6a5f8",
            hover_color = "#866091",
            text_color = "white",
            command = lambda: self. open_detail_view(self. current_result_row, "select_result")
        )
        detail_btn. pack(side = "right")

        ToolTip(detail_btn, "拡大して詳しく見る")

        # ------------------------------------
        # 下段：スクショ／プリセットに登録(🔍と同じ右寄せ)
        # ------------------------------------
        select_result_second_row = ctk. CTkFrame(self. select_result_frame, fg_color = "transparent")
        select_result_second_row. pack(fill = "x", padx = 10, pady = (6, 0))

        register_result_btn = ctk. CTkButton(
            select_result_second_row,
            text = "📚",
            width = 40,
            height = 30,
            corner_radius = 50,
            fg_color = "#e6a5f8",
            hover_color = "#866091",
            text_color = "white",
            command = self. register_result_to_preset
        )
        register_result_btn. pack(side = "right")

        ToolTip(register_result_btn, "プリセットに登録")

        screenshot_result_btn = ctk. CTkButton(
            select_result_second_row,
            text = "📷",
            width = 40,
            height = 30,
            corner_radius = 50,
            fg_color = "#e6a5f8",
            hover_color = "#866091",
            text_color = "white",
            command = self. screenshot_select_result
        )
        screenshot_result_btn. pack(side = "right", padx = (0, 6))

        ToolTip(screenshot_result_btn, "スクショ保存")

        ctk. CTkLabel(
            self. select_result_frame,
            text = "おすすめ3色",
            font = ("ふてほど丸ゴシック", 22, "bold")
        ). pack(pady = (20, 20))

        self. circle_row = ctk. CTkFrame(self. select_result_frame, fg_color = "transparent")
        self. circle_row. pack(pady = (0, 10))

        self. result_circles = {}
        self. result_hex_labels = {}

        for key, label_text in (("base", "メインカラー"), ("accent", "アクセント"), ("sub", "サブ")):
            col = ctk. CTkFrame(self. circle_row, fg_color = "transparent")
            col. pack(side = "left", padx = 8)

            ctk. CTkLabel(
                col,
                text = label_text,
                font = ("ふてほど丸ゴシック", 15),
                text_color = "#777777"
            ). pack(pady = (0, 6))

            circle = ctk. CTkLabel(
                col,
                text = "",
                width = 110,
                height = 110,
                corner_radius = 55,
                fg_color = "#FFFFFF"
            )
            circle. pack()

            hex_label = ctk. CTkLabel(
                col,
                text = "#FFFFFF",
                font = ("ふてほど丸ゴシック", 15),
                text_color = "#555555"
            )
            hex_label. pack(pady = (8, 0))

            self. result_circles[key] = circle
            self. result_hex_labels[key] = hex_label

        ctk. CTkLabel(
            self. select_result_frame,
            text = "-COLOR BALANCE-",
            font = ("マメロン 5 Hi Regular", 16, "bold"),
            text_color = "#555555"
        ). pack(pady = (25, 10))

        self. result_bar_frame = ctk. CTkFrame(self. select_result_frame, fg_color = "transparent", width = 340, height = 40)
        self. result_bar_frame. pack_propagate(False)
        self. result_bar_frame. pack(pady = (0, 10))

        self. result_bar_segments = {}

        for key in ("base", "accent", "sub"):
            seg = ctk. CTkLabel(
                self. result_bar_frame,
                text = "",
                text_color = "white",
                font = ("ふてほど丸ゴシック", 12, "bold"),
                fg_color = "#FFFFFF"
            )
            seg. pack(side = "left", fill = "y")

            self. result_bar_segments[key] = seg

        # ------------------------------------
        # メインカラーが同じ配色が他にもある時だけ出す「ほかのカラーを見てみる」
        # ------------------------------------
        self. other_base_section = ctk. CTkFrame(self. select_result_frame, fg_color = "transparent")

        self. other_base_go_btn = self. build_go_section(
            self. other_base_section,
            "メインカラーに合うほかのカラーを見てみる",
            self. on_other_base_go
        )

        self. other_base_matches = []

        # GO!結果画面をどのセクションから開いたか(「← 戻る」でその場所に戻すため)
        self. result_source = "select"

        self. space()


        # ------------------------------------
        # 🔍「拡大して詳しく見る」の詳細ページ
        # (セレクト/カテゴリ/ラッキーカラーどの結果画面からも共通で開く。開いている間だけウィンドウを横広・縦やや短めにする)
        # ------------------------------------
        self. detail_frame = ctk. CTkFrame(self, fg_color = "white")

        detail_top_row = ctk. CTkFrame(self. detail_frame, fg_color = "transparent")
        detail_top_row. pack(fill = "x", padx = 20, pady = (15, 0))

        detail_back_btn = ctk. CTkButton(
            detail_top_row,
            text = "← 戻る",
            width = 80,
            height = 30,
            corner_radius = 50,
            fg_color = "#e6a5f8",
            hover_color = "#866091",
            text_color = "white",
            font = ("マメロン 5 Hi Regular", 13),
            command = self. close_detail_view
        )
        detail_back_btn. pack(side = "left")

        detail_register_btn = ctk. CTkButton(
            detail_top_row,
            text = "📚",
            width = 40,
            height = 30,
            corner_radius = 50,
            fg_color = "#e6a5f8",
            hover_color = "#866091",
            text_color = "white",
            command = self. register_detail_result_to_preset
        )
        detail_register_btn. pack(side = "right")

        ToolTip(detail_register_btn, "プリセットに登録")

        detail_screenshot_btn = ctk. CTkButton(
            detail_top_row,
            text = "📷",
            width = 40,
            height = 30,
            corner_radius = 50,
            fg_color = "#e6a5f8",
            hover_color = "#866091",
            text_color = "white",
            command = self. screenshot_detail_result
        )
        detail_screenshot_btn. pack(side = "right", padx = (0, 6))

        ToolTip(detail_screenshot_btn, "スクショ保存")

        ctk. CTkLabel(
            self. detail_frame,
            text = "おすすめ3色",
            font = ("ふてほど丸ゴシック", 20, "bold")
        ). pack(pady = (15, 20))

        self. detail_circle_row = ctk. CTkFrame(self. detail_frame, fg_color = "transparent")
        self. detail_circle_row. pack(pady = (0, 10))

        self. detail_circles = {}
        self. detail_code_buttons = {}

        for key, label_text in (("base", "メインカラー"), ("accent", "アクセント"), ("sub", "サブ")):
            col = ctk. CTkFrame(self. detail_circle_row, fg_color = "transparent")
            col. pack(side = "left", padx = 4)

            ctk. CTkLabel(
                col,
                text = label_text,
                font = ("ふてほど丸ゴシック", 13),
                text_color = "#777777"
            ). pack(pady = (0, 8))

            circle = ctk. CTkLabel(
                col,
                text = "",
                width = 150,
                height = 150,
                corner_radius = 75,
                fg_color = "#FFFFFF"
            )
            circle. pack()

            code_btn = ctk. CTkButton(
                col,
                text = "#FFFFFF",
                width = 90,
                height = 26,
                corner_radius = 6,
                fg_color = "white",
                hover_color = "#f0f0f0",
                text_color = "black",
                border_width = 1,
                border_color = "black",
                font = ("ふてほど丸ゴシック", 11)
            )
            code_btn. pack(pady = (10, 0))

            # 押した時に表示されている文字をそのままコピーする(常に今表示中の色になる)
            code_btn. configure(command = lambda b = code_btn: self. copy_preset_color(b. cget("text")))

            ToolTip(code_btn, "コピーする")

            self. detail_circles[key] = circle
            self. detail_code_buttons[key] = code_btn

        ctk. CTkLabel(
            self. detail_frame,
            text = "-COLOR BALANCE-",
            font = ("マメロン 5 Hi Regular", 15, "bold"),
            text_color = "#555555"
        ). pack(pady = (20, 10))

        self. detail_bar_frame = ctk. CTkFrame(self. detail_frame, fg_color = "transparent", width = 480, height = 46)
        self. detail_bar_frame. pack_propagate(False)
        self. detail_bar_frame. pack(pady = (0, 20))

        self. detail_bar_segments = {}

        for key in ("base", "accent", "sub"):
            seg = ctk. CTkLabel(
                self. detail_bar_frame,
                text = "",
                text_color = "white",
                font = ("ふてほど丸ゴシック", 13, "bold"),
                fg_color = "#FFFFFF"
            )
            seg. pack(side = "left", fill = "y")

            self. detail_bar_segments[key] = seg

        # ------------------------------------
        # 広告POP風のサンプルイメージ(この3色をCOLOR BALANCEの比率で使うとこんな感じ、という見本)
        # ------------------------------------
        mockup_border = ctk. CTkFrame(
            self. detail_frame,
            fg_color = "white",
            border_width = 2,
            border_color = "#d0d0d0",
            corner_radius = 12
        )
        mockup_border. pack(pady = (0, 15))

        self. detail_mockup_label = ctk. CTkLabel(mockup_border, text = "", width = 480, height = 200)
        self. detail_mockup_label. pack(padx = 8, pady = 8)

        self. current_result_row = None
        self. current_recommend_row = None
        self. detail_return_to = "scroll"


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
        self. image_group = SingleSelectGroup(
            self. category_frame,
            title = "イメージ",
            options = ["ビビッド", "ネオン", "くすみ", "パステル", "ポップ", "ナチュラル", "クール", "エレガント", "アース", "ヴィンテージ"],
            on_change = self. refresh_category_filters
        )

        self. season_group = SingleSelectGroup(
            self. category_frame,
            title = "季節",
            options = ["春", "夏", "秋", "冬"],
            on_change = self. refresh_category_filters
        )

        self. era_group = SingleSelectGroup(
            self. category_frame,
            title = "年代",
            options = ["70's", "80's", "90's", "00's"],
            on_change = self. refresh_category_filters
        )

        self. region_group = SingleSelectGroup(
            self. category_frame,
            title = "地域",
            options = ["南米・メキシコ", "北欧", "地中海", "アフリカン", "中東・モロッコ", "東アジア", "南国・トロピカル"],
            on_change = self. refresh_category_filters,
            display_labels = {
                "南米・メキシコ": "南米",
                "中東・モロッコ": "中東",
                "南国・トロピカル": "南国",
            }
        )

        # データ登録ツールで追加されたカスタムタグを、同じ内容で下に復元する
        self. load_custom_category_tags(self. image_group, "イメージ")
        self. load_custom_category_tags(self. season_group, "季節")
        self. load_custom_category_tags(self. era_group, "年代")
        self. load_custom_category_tags(self. region_group, "地域")

        # 起動直後は何も選ばれていないので、この時点では全ボタンが有効なままになる
        self. refresh_category_filters()

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
        # 9枠分のデータ(colorsがNoneのうちは「まだ登録されていない」枠)
        self. preset_data = [
            {"colors": None, "name": ""} for _ in range(9)
        ]

        # 保存済みのプリセット枠があれば読み込む(アプリを再起動しても消えないように)
        self. cursor. execute("SELECT slot, name, base_hex, accent_hex, sub_hex FROM my_preset_slots")

        for slot, name, base_hex, accent_hex, sub_hex in self. cursor. fetchall():
            if 0 <= slot < 9:
                self. preset_data[slot] = {
                    "colors": [base_hex, accent_hex, sub_hex],
                    "name": name or ""
                }

        self. current_preset_page = 0

        # タブ(1〜9)の行
        self. preset_tab_buttons = []

        preset_tab_row = ctk. CTkFrame(
            self. preset_frame,
            fg_color = "transparent"
        )
        preset_tab_row. pack(fill = "x", padx = 15, pady = (10, 0))

        for i in range(9):
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


        # ------------------------------------
        # 「ラッキーカラーを見る」文言＋GOボタン(押すたびに完全ランダムで1件選ぶ)
        # セレクト/カテゴリと違い、別画面には移動せずこのセクション内で完結させる
        # ------------------------------------
        self. recommend_go_btn = self. build_go_section(
            self. recommend_frame,
            "ラッキーカラーを見る",
            self. on_recommend_go
        )

        # ------------------------------------
        # 結果表示エリア(最初は非表示。GO!を押すとここに3色が表示される)
        # ------------------------------------
        self. recommend_result_area = ctk. CTkFrame(self. recommend_frame, fg_color = "transparent")

        ctk. CTkLabel(
            self. recommend_result_area,
            text = "おすすめ3色",
            font = ("ふてほど丸ゴシック", 22, "bold")
        ). pack(pady = (10, 20))

        self. recommend_circle_row = ctk. CTkFrame(self. recommend_result_area, fg_color = "transparent")
        self. recommend_circle_row. pack(pady = (0, 10))

        self. recommend_circles = {}
        self. recommend_hex_labels = {}

        for key, label_text in (("base", "メインカラー"), ("accent", "アクセント"), ("sub", "サブ")):
            col = ctk. CTkFrame(self. recommend_circle_row, fg_color = "transparent")
            col. pack(side = "left", padx = 8)

            ctk. CTkLabel(
                col,
                text = label_text,
                font = ("ふてほど丸ゴシック", 15),
                text_color = "#777777"
            ). pack(pady = (0, 6))

            circle = ctk. CTkLabel(
                col,
                text = "",
                width = 110,
                height = 110,
                corner_radius = 55,
                fg_color = "#FFFFFF"
            )
            circle. pack()

            hex_label = ctk. CTkLabel(
                col,
                text = "#FFFFFF",
                font = ("ふてほど丸ゴシック", 15),
                text_color = "#555555"
            )
            hex_label. pack(pady = (8, 0))

            self. recommend_circles[key] = circle
            self. recommend_hex_labels[key] = hex_label

        ctk. CTkLabel(
            self. recommend_result_area,
            text = "-COLOR BALANCE-",
            font = ("マメロン 5 Hi Regular", 16, "bold"),
            text_color = "#555555"
        ). pack(pady = (5, 10))

        self. recommend_bar_frame = ctk. CTkFrame(self. recommend_result_area, fg_color = "transparent", width = 340, height = 40)
        self. recommend_bar_frame. pack_propagate(False)
        self. recommend_bar_frame. pack(pady = (0, 10))

        self. recommend_bar_segments = {}

        for key in ("base", "accent", "sub"):
            seg = ctk. CTkLabel(
                self. recommend_bar_frame,
                text = "",
                text_color = "white",
                font = ("ふてほど丸ゴシック", 12, "bold"),
                fg_color = "#FFFFFF"
            )
            seg. pack(side = "left", fill = "y")

            self. recommend_bar_segments[key] = seg

        # ------------------------------------
        # 🔍拡大／📷スクショ／📚プリセット登録(戻るボタンは無し)
        # ------------------------------------
        recommend_action_row = ctk. CTkFrame(self. recommend_result_area, fg_color = "transparent")
        recommend_action_row. pack(pady = (0, 10))

        recommend_detail_btn = ctk. CTkButton(
            recommend_action_row,
            text = "🔍",
            width = 40,
            height = 30,
            corner_radius = 50,
            fg_color = "#e6a5f8",
            hover_color = "#866091",
            text_color = "white",
            command = lambda: self. open_detail_view(self. current_recommend_row, "scroll")
        )
        recommend_detail_btn. pack(side = "left", padx = 4)

        ToolTip(recommend_detail_btn, "拡大して詳しく見る")

        recommend_screenshot_btn = ctk. CTkButton(
            recommend_action_row,
            text = "📷",
            width = 40,
            height = 30,
            corner_radius = 50,
            fg_color = "#e6a5f8",
            hover_color = "#866091",
            text_color = "white",
            command = self. screenshot_recommend_result
        )
        recommend_screenshot_btn. pack(side = "left", padx = 4)

        ToolTip(recommend_screenshot_btn, "スクショ保存")

        recommend_register_btn = ctk. CTkButton(
            recommend_action_row,
            text = "📚",
            width = 40,
            height = 30,
            corner_radius = 50,
            fg_color = "#e6a5f8",
            hover_color = "#866091",
            text_color = "white",
            command = self. register_recommend_result_to_preset
        )
        recommend_register_btn. pack(side = "left", padx = 4)

        ToolTip(recommend_register_btn, "プリセットに登録")

        # ------------------------------------
        # 「違うカラーも見てみる」文言＋GOボタン(再度押すとまたランダムに選び直す)
        # ------------------------------------
        self. recommend_again_btn = self. build_go_section(
            self. recommend_result_area,
            "違うカラーも見てみる",
            self. on_recommend_go
        )


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

        self. show_toast("コピーしました")

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
            font = ("マメロン 5 Hi Regular", 14),
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

        row = self. find_similar_preset(self. current_hex)

        if row is None:
            print("まだ配色データが登録されていません")
            return

        self. result_source = "select"
        self. show_select_result(row)


    # ======================================
    # HEX同士の近さを距離として計算する(RGB空間でのユークリッド距離)
    # ======================================
    def color_distance(self, hex_a, hex_b):

        ra, ga, ba = self. hex_to_rgb(hex_a)
        rb, gb, bb = self. hex_to_rgb(hex_b)

        return ((ra - rb) ** 2 + (ga - gb) ** 2 + (ba - bb) ** 2) ** 0.5


    def hex_to_rgb(self, hex_color):

        hex_color = hex_color. lstrip("#")

        return (
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16),
        )


    # ======================================
    # 指定した色に一番近いベース色を持つ配色をcolpama.dbから探す
    # 完全一致があればその中からランダムに1件、無ければ一番近い色の中からランダムに1件返す
    # ======================================
    def find_similar_preset(self, target_hex):

        self. cursor. execute("""
            SELECT id, base_hex, base_pct, accent_hex, accent_pct, sub_hex, sub_pct
            FROM presets
        """)
        rows = self. cursor. fetchall()

        if not rows:
            return None

        exact_matches = [r for r in rows if r[1]. lower() == target_hex. lower()]

        if exact_matches:
            return random. choice(exact_matches)

        best_distance = None
        best_rows = []

        for r in rows:
            distance = self. color_distance(target_hex, r[1])

            if best_distance is None or distance < best_distance:
                best_distance = distance
                best_rows = [r]
            elif distance == best_distance:
                best_rows. append(r)

        return random. choice(best_rows)


    # ======================================
    # GO!結果画面の中身を、検索結果の配色で埋める(セレクト・カテゴリ共通)
    # ======================================
    def render_select_result(self, row):

        current_id, base_hex = row[0], row[1]

        self. current_result_row = row

        self. apply_result_colors(row, self. result_circles, self. result_hex_labels, self. result_bar_segments)

        # 同じベース色を持つ他の配色があるかを調べて、あるボタンだけ表示する
        self. other_base_matches = self. get_other_base_matches(base_hex, current_id)

        if self. other_base_matches:
            self. other_base_section. pack(pady = (10, 10))
        else:
            self. other_base_section. pack_forget()


    # ======================================
    # 検索結果(row)の3色を、指定した円・コード表示・比率バーに反映する
    # (セレクト/カテゴリの結果画面、ラッキーカラーの結果表示で共通して使う)
    # ======================================
    def apply_result_colors(self, row, circles, hex_labels, bar_segments, bar_width = 340):

        _id, base_hex, base_pct, accent_hex, accent_pct, sub_hex, sub_pct = row

        hexes = {"base": base_hex, "accent": accent_hex, "sub": sub_hex}
        pcts = {"base": base_pct, "accent": accent_pct, "sub": sub_pct}

        for key in ("base", "accent", "sub"):
            circles[key]. configure(fg_color = hexes[key])
            hex_labels[key]. configure(text = hexes[key]. upper())

            seg_width = max(1, round(bar_width * pcts[key] / 100))
            bar_segments[key]. configure(width = seg_width, fg_color = hexes[key])

        return hexes


    # ======================================
    # ベース色が同じで、今表示している配色とは別のものをcolpama.dbから探す
    # ======================================
    def get_other_base_matches(self, base_hex, exclude_id):

        self. cursor. execute("""
            SELECT id, base_hex, base_pct, accent_hex, accent_pct, sub_hex, sub_pct
            FROM presets
            WHERE base_hex = ? AND id != ?
        """, (base_hex, exclude_id))

        return self. cursor. fetchall()


    # ======================================
    # 「メインカラーに合うほかのカラーを見てみる」ボタンの処理
    # ======================================
    def on_other_base_go(self):

        if not self. other_base_matches:
            return

        new_row = random. choice(self. other_base_matches)
        self. render_select_result(new_row)


    # ======================================
    # GO!結果画面を表示する(セレクト・カテゴリ共通。普段見えているスクロール部分を隠す)
    # ======================================
    def show_select_result(self, row):

        self. render_select_result(row)

        self. scroll. pack_forget()
        self. select_result_frame. pack(fill = "both", expand = True)


    # ======================================
    # GO!結果画面：戻るボタンの処理(result_sourceに応じて元のセクションに戻す)
    # ======================================
    def close_select_result(self):

        self. select_result_frame. pack_forget()
        self. scroll. pack(fill = "both", expand = True)

        if self. result_source == "category":
            self. scroll_category()
        else:
            self. scroll_select()


    # ======================================
    # GO!結果表示：3色プレビュー＋比率バーをスクショ保存する
    # (セレクト/カテゴリの結果画面、ラッキーカラーの結果表示で共通して使う)
    # ======================================
    def screenshot_result_area(self, circle_row, bar_frame, default_filename):

        self. update()

        x = min(circle_row. winfo_rootx(), bar_frame. winfo_rootx())
        y = circle_row. winfo_rooty()

        right = max(
            circle_row. winfo_rootx() + circle_row. winfo_width(),
            bar_frame. winfo_rootx() + bar_frame. winfo_width()
        )
        bottom = bar_frame. winfo_rooty() + bar_frame. winfo_height()

        screenshot = ImageGrab. grab(bbox = (x, y, right, bottom), all_screens = True)

        file_path = filedialog. asksaveasfilename(
            defaultextension = ".png",
            filetypes = [("PNG画像", "*.png")],
            initialfile = default_filename
        )

        if file_path:
            screenshot. save(file_path)


    def screenshot_select_result(self):

        self. screenshot_result_area(self. circle_row, self. result_bar_frame, "recommend.png")


    # ======================================
    # 🔍「拡大して詳しく見る」：詳細ページを開く(row=表示する検索結果、return_to=戻り先)
    # ======================================
    def open_detail_view(self, row, return_to):

        if row is None:
            return

        self. detail_return_to = return_to

        hexes = self. apply_result_colors(row, self. detail_circles, self. detail_code_buttons, self. detail_bar_segments, bar_width = 480)

        mockup_image = self. generate_mockup_image(hexes["base"], hexes["accent"], hexes["sub"])
        self. detail_mockup_photo = ctk. CTkImage(
            light_image = mockup_image,
            dark_image = mockup_image,
            size = (480, 200)
        )
        self. detail_mockup_label. configure(image = self. detail_mockup_photo, text = "")

        if return_to == "select_result":
            self. select_result_frame. pack_forget()
        else:
            self. scroll. pack_forget()

        self. geometry("700x740")
        self. detail_frame. pack(fill = "both", expand = True)


    # ======================================
    # 🔍詳細ページ：戻るボタンの処理(開いた時の元の場所に戻し、ウィンドウサイズも戻す)
    # ======================================
    def close_detail_view(self):

        self. detail_frame. pack_forget()
        self. geometry("400x690")

        if self. detail_return_to == "select_result":
            self. select_result_frame. pack(fill = "both", expand = True)
        else:
            self. scroll. pack(fill = "both", expand = True)


    # ======================================
    # 🔍詳細ページ：色見本のイメージ画像を作る
    # (3色をCOLOR BALANCEの比率で使うとどんな雰囲気になるかの、広告POP風のサンプル)
    # ======================================
    def generate_mockup_image(self, base_hex, accent_hex, sub_hex, width = 480, height = 200):

        image = Image. new("RGB", (width, height), base_hex)
        draw = ImageDraw. Draw(image)

        # アクセント色の絵の具ストロークを2〜3個、ランダムな位置・大きさで
        for _ in range(3):
            w = random. randint(int(width * 0.35), int(width * 0.55))
            h = random. randint(int(height * 0.45), int(height * 0.75))
            x = random. randint(-w // 3, width - w * 2 // 3)
            y = random. randint(-h // 3, height - h * 2 // 3)

            draw. ellipse([x, y, x + w, y + h], fill = accent_hex)

        # サブ色の小さい丸を散らす
        for _ in range(7):
            r = random. randint(8, 18)
            x = random. randint(0, width)
            y = random. randint(0, height)

            draw. ellipse([x - r, y - r, x + r, y + r], fill = sub_hex)

        return image


    # ======================================
    # 🔍詳細ページ：今表示している3色をスクショ保存する
    # ======================================
    def screenshot_detail_result(self):

        self. screenshot_result_area(self. detail_circle_row, self. detail_bar_frame, "recommend.png")


    # ======================================
    # 🔍詳細ページ：今表示している3色を、選択中のプリセット枠に登録する
    # ======================================
    def register_detail_result_to_preset(self):

        self. register_colors_to_preset(self. detail_circles)


    # ======================================
    # GO!結果表示：今表示している3色を、選択中のプリセット枠に登録する
    # (セレクト/カテゴリの結果画面、ラッキーカラーの結果表示で共通して使う)
    # ======================================
    def register_colors_to_preset(self, circles):

        # 開いているタブではなく、空いている一番若い番号のスロットに登録する
        target_index = None

        for i, data in enumerate(self. preset_data):
            if data["colors"] is None:
                target_index = i
                break

        if target_index is None:
            self. show_toast("プリセットに空きがないため登録できません")
            return

        colors = [
            circles["base"]. cget("fg_color"),
            circles["accent"]. cget("fg_color"),
            circles["sub"]. cget("fg_color"),
        ]

        self. preset_data[target_index]["colors"] = colors

        self. save_preset_slot(target_index)
        self. render_preset_page()

        self. show_toast(f"プリセット {target_index + 1} に登録しました")


    def register_result_to_preset(self):

        self. register_colors_to_preset(self. result_circles)


    # ======================================
    # プリセット：1枠分のデータをcolpama.dbに保存する(アプリを閉じても残るように)
    # ======================================
    def save_preset_slot(self, index):

        data = self. preset_data[index]

        if data["colors"] is None:
            self. cursor. execute("DELETE FROM my_preset_slots WHERE slot = ?", (index,))
        else:
            self. cursor. execute("""
                INSERT INTO my_preset_slots (slot, name, base_hex, accent_hex, sub_hex)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(slot) DO UPDATE SET
                    name = excluded. name,
                    base_hex = excluded. base_hex,
                    accent_hex = excluded. accent_hex,
                    sub_hex = excluded. sub_hex
            """, (index, data["name"], data["colors"][0], data["colors"][1], data["colors"][2]))

        self. conn. commit()


    # ======================================
    # 画面中央に大きくメッセージを出し、2秒待ってからフェードアウトする通知
    # ======================================
    def show_toast(self, message):

        toast = tk. Toplevel(self)
        toast. wm_overrideredirect(True)
        toast. attributes("-topmost", True)

        # 角丸の外側(四隅)を透過させる。対応していない環境ではそのまま単色の背景になる
        transparent_key = "#123456"
        is_transparent = True

        try:
            toast. configure(bg = transparent_key)
            toast. attributes("-transparentcolor", transparent_key)
        except tk. TclError:
            is_transparent = False

        label_kwargs = dict(
            text = message,
            font = ("マメロン 5 Hi Regular", 16, "bold"),
            fg_color = "#ff6f9f",
            text_color = "white",
            corner_radius = 20,
            width = 260,
            height = 70
        )

        if is_transparent:
            label_kwargs["bg_color"] = transparent_key

        label = ctk. CTkLabel(toast, **label_kwargs)
        label. pack(padx = 4, pady = 4)

        toast. update_idletasks()

        w = toast. winfo_width()
        h = toast. winfo_height()

        x = self. winfo_rootx() + (self. winfo_width() - w) // 2
        y = self. winfo_rooty() + (self. winfo_height() - h) // 2

        toast. wm_geometry(f"+{x}+{y}")
        toast. attributes("-alpha", 1.0)

        def fade(opacity = 1.0):
            if opacity <= 0:
                toast. destroy()
                return

            toast. attributes("-alpha", opacity)
            toast. after(50, lambda: fade(opacity - 0.1))

        toast. after(2000, fade)


    # ======================================
    # セレクトの色を初期状態(白)に戻す
    # ======================================
    def reset_select(self):

        self. apply_color("#FFFFFF")
        self. sync_picker_from_hex("#FFFFFF")


    # ======================================
    # カテゴリ：データ登録ツールで追加されたカスタムタグを、そのカテゴリの下に復元する
    # ======================================
    def load_custom_category_tags(self, group, group_name):

        self. cursor. execute(
            "SELECT tag FROM custom_tags WHERE group_name = ? ORDER BY id ASC",
            (group_name,)
        )

        for (tag,) in self. cursor. fetchall():
            group. add_extra_option(tag)


    # ======================================
    # カテゴリ：選んだ内容に応じて、季節・年代・地域の選択肢を段階的に絞り込む(その他は常に選択可)
    # 「その他」が選ばれている段は絞り込みの条件に使わない(そのカテゴリでは絞らない、という意味なので)
    # ======================================
    def refresh_category_filters(self):

        conditions = {"tone_tags": self. image_group. selected}

        allowed_season = self. get_allowed_tags("season_tags", conditions)
        self. apply_category_gate(self. season_group, allowed_season)
        conditions["season_tags"] = self. season_group. selected

        allowed_era = self. get_allowed_tags("era_tags", conditions)
        self. apply_category_gate(self. era_group, allowed_era)
        conditions["era_tags"] = self. era_group. selected

        allowed_region = self. get_allowed_tags("region_tags", conditions)
        self. apply_category_gate(self. region_group, allowed_region)


    # ======================================
    # カテゴリ：colpama.dbに登録された配色から、指定した条件と一緒に登録のあるタグの集合を調べる
    # 条件が無ければNoneを返す(絞り込みなし＝全部有効の意味)
    # ======================================
    def get_allowed_tags(self, target_column, conditions):

        where_clauses = []
        params = []

        for column, tag in conditions. items():
            if tag and tag != "その他":
                where_clauses. append(f"(',' || {column} || ',') LIKE ?")
                params. append(f"%,{tag},%")

        if not where_clauses:
            return None

        query = f"SELECT {target_column} FROM presets WHERE " + " AND ". join(where_clauses)
        self. cursor. execute(query, params)

        allowed = set()

        for (tags_value,) in self. cursor. fetchall():
            for tag in (tags_value or ""). split(","):
                tag = tag. strip()

                if tag:
                    allowed. add(tag)

        return allowed


    # ======================================
    # カテゴリ：絞り込み結果(allowed_tags)をボタンの有効／グレーアウトに反映する
    # allowed_tagsがNoneの時は絞り込み無し(全部有効)
    # ======================================
    def apply_category_gate(self, group, allowed_tags):

        if allowed_tags is None:
            group. enable_all()
            return

        # 選択解除を先に行う。グレーアウトより後にやると、選択解除時の「普通の紫色」への
        # 戻し処理が、直後のグレーアウト表示を上書きしてしまう(ボタンの色は紫のまま
        # 文字だけグレーになる)ため、必ずこの順番にする
        if group. selected is not None and group. selected != "その他" and group. selected not in allowed_tags:
            group. clear_selection()

        for option in group. buttons:
            enabled = (option == "その他") or (option in allowed_tags)
            group. set_enabled(option, enabled)


    # ======================================
    # 「このチョイスで調べる」ボタンの処理
    # ======================================
    def on_category_go(self):

        if not self. has_any_category_selected():
            self. show_toast("条件を1つ以上選んでください")
            return

        row = self. find_preset_by_category()

        if row is None:
            self. show_toast("条件に合う配色が見つかりませんでした")
            return

        self. result_source = "category"
        self. show_select_result(row)


    # ======================================
    # カテゴリ：4カテゴリのうち何か1つでも選ばれているか(「その他」は条件扱いしない)
    # ======================================
    def has_any_category_selected(self):

        return any(
            group. selected is not None and group. selected != "その他"
            for group in (self. image_group, self. season_group, self. era_group, self. region_group)
        )


    # ======================================
    # カテゴリ：選ばれている条件(未選択・「その他」は絞り込みに使わない)を
    # すべて満たす配色をcolpama.dbから探す。複数あればランダムに1件返す
    # ======================================
    def find_preset_by_category(self):

        conditions = []
        params = []

        for group, column in (
            (self. image_group, "tone_tags"),
            (self. season_group, "season_tags"),
            (self. era_group, "era_tags"),
            (self. region_group, "region_tags"),
        ):
            tag = group. selected

            if tag and tag != "その他":
                conditions. append(f"(',' || {column} || ',') LIKE ?")
                params. append(f"%,{tag},%")

        if not conditions:
            return None

        query = """
            SELECT id, base_hex, base_pct, accent_hex, accent_pct, sub_hex, sub_pct
            FROM presets
            WHERE """ + " AND ". join(conditions)

        self. cursor. execute(query, params)
        rows = self. cursor. fetchall()

        if not rows:
            return None

        return random. choice(rows)


    # ======================================
    # 「ラッキーカラーを見る」「違うカラーも見てみる」ボタンの処理
    # (条件なし、押すたびに完全ランダムで1件選ぶ。別画面には移らずこのセクション内で完結)
    # ======================================
    def on_recommend_go(self):

        row = self. find_random_preset()

        if row is None:
            self. show_toast("まだ配色データが登録されていません")
            return

        self. render_recommend_result(row)

        # GO!ボタンは常に1つだけにする(1回目のボタンは結果が出たら隠し、
        # 以降は結果の下の「違うカラーも見てみる」のGO!だけを使う)
        self. recommend_go_btn. pack_forget()
        self. recommend_result_area. pack(fill = "x")


    # ======================================
    # ラッキーカラーの結果表示エリアを、検索結果の配色で埋める
    # ======================================
    def render_recommend_result(self, row):

        self. current_recommend_row = row

        self. apply_result_colors(row, self. recommend_circles, self. recommend_hex_labels, self. recommend_bar_segments)


    # ======================================
    # colpama.dbからランダムに1件選ぶ(ラッキーカラー用、絞り込み条件なし)
    # ======================================
    def find_random_preset(self):

        self. cursor. execute("""
            SELECT id, base_hex, base_pct, accent_hex, accent_pct, sub_hex, sub_pct
            FROM presets
        """)
        rows = self. cursor. fetchall()

        if not rows:
            return None

        return random. choice(rows)


    # ======================================
    # ラッキーカラーの結果表示：3色プレビュー＋比率バーをスクショ保存する
    # ======================================
    def screenshot_recommend_result(self):

        self. screenshot_result_area(self. recommend_circle_row, self. recommend_bar_frame, "lucky_color.png")


    # ======================================
    # ラッキーカラーの結果表示：今表示している3色を、選択中のプリセット枠に登録する
    # ======================================
    def register_recommend_result_to_preset(self):

        self. register_colors_to_preset(self. recommend_circles)


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

        # 登録済みならその色、まだ登録されていなければ空(仮の色は出さない)
        colors = data["colors"] if data["colors"] is not None else []

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

        ToolTip(camera_btn, "スクショ保存")

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
            font = ("マメロン 5 Hi Regular", 14),
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
        # カラーコード表示(クリックでコピーできるコード欄、色ごとに1個)
        # ------------------------------------
        code_row = ctk. CTkFrame(self. preset_content_frame, fg_color = "transparent")
        code_row. pack(pady = (0, 10))

        for color in colors:
            code_btn = ctk. CTkButton(
                code_row,
                text = color. upper(),
                width = 90,
                height = 28,
                corner_radius = 6,
                fg_color = "white",
                hover_color = "#f0f0f0",
                text_color = "black",
                border_width = 1,
                border_color = "black",
                font = ("ふてほど丸ゴシック", 12),
                command = lambda c = color. upper(): self. copy_preset_color(c)
            )
            code_btn. pack(side = "left", padx = 5)

            ToolTip(code_btn, "コピーする")


    # ======================================
    # プリセット：名前だけを現在のページに登録する(3色は📚ボタンから登録されたものをそのまま残す)
    # ======================================
    def register_current_preset(self):

        name = self. preset_name_entry. get(). strip()

        self. preset_data[self. current_preset_page]["name"] = name

        if self. preset_data[self. current_preset_page]["colors"] is not None:
            self. save_preset_slot(self. current_preset_page)

        self. render_preset_page()

        self. show_toast("名前を変更しました")


    # ======================================
    # プリセット：現在のページを削除(未登録状態に戻す)
    # ======================================
    def delete_current_preset(self):

        self. preset_data[self. current_preset_page] = {"colors": None, "name": ""}
        self. save_preset_slot(self. current_preset_page)
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


#=============クラス直下（__init__の外）のものはここまで


    # ======================================
    # ホームへ戻る
    # ======================================
    def go_home(self):

        # 🔍詳細ページ・GO!の結果画面が開いていたら閉じて、普段のスクロール画面に戻す
        self. detail_frame. pack_forget()
        self. geometry("400x690")

        self. select_result_frame. pack_forget()
        self. scroll. pack(fill = "both", expand = True)

        self. scroll. _parent_canvas. yview_moveto(0)

        #ホームボタン押すと全部リセットする
        self. reset_select()
        self. image_group. reset()
        self. season_group. reset()
        self. era_group. reset()
        self. region_group. reset()
        self. recommend_result_area. pack_forget()
        self. recommend_go_btn. pack(pady = (0, 15))


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