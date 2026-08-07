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
# タググループ(既存選択肢＋その他＋新規追加、新規分は4個ごとに折り返す)
# ======================================
class TagGroup:

    def __init__(self, parent, title, options, font_name = "ふてほど丸ゴシック", on_new_tag = None):

        self. selected = []
        self. buttons = {}
        self. font_name = font_name
        self. on_new_tag = on_new_tag

        ctk. CTkLabel(
            parent,
            text = f"-{title}-",
            font = (font_name, 14, "bold"),
            text_color = "#555555"
        ). pack(anchor = "w", padx = 15, pady = (6, 2))

        # ------------------------------------
        # 1段目：既存の選択肢＋その他＋新規入力欄(常に折り返さない)
        # ------------------------------------
        self. header_row = ctk. CTkFrame(parent, fg_color = "transparent")
        self. header_row. pack(anchor = "w", padx = 15, pady = (0, 2))

        for option in options:
            self. add_button(self. header_row, option)

        # 「その他」固定ボタン
        self. other_btn = ctk. CTkButton(
            self. header_row,
            text = "その他",
            width = 56,
            height = 26,
            corner_radius = 50,
            fg_color = "#e6a5f8",
            hover_color = "#866091",
            text_color = "white",
            font = (font_name, 12),
            command = lambda: self. select("その他")
        )
        self. other_btn. pack(side = "left", padx = 4)
        self. buttons["その他"] = self. other_btn

        # 「新規」入力欄(常に一番右端)
        self. new_entry = ctk. CTkEntry(
            self. header_row,
            width = 56,
            height = 26,
            placeholder_text = "新規",
            placeholder_text_color = "#dddddd"
        )
        self. new_entry. pack(side = "left", padx = 4)

        # ------------------------------------
        # 2段目以降：新規タグ専用エリア(4個ごとに折り返す)
        # ------------------------------------
        self. new_tags_area = ctk. CTkFrame(parent, fg_color = "transparent", height = 150)
        self. new_tags_area. pack(anchor = "w", padx = 15, pady = (0, 2))

        self. new_tag_count = 0
        self. current_new_row = None


    # ======================================
    # ボタンを1つ作って、指定した行(parent_row)に配置する
    # ======================================
    def add_button(self, parent_row, text):

        btn = ctk. CTkButton(
            parent_row,
            text = text,
            width = 56,
            height = 26,
            corner_radius = 50,
            fg_color = "#e6a5f8",
            hover_color = "#866091",
            text_color = "white",
            font = (self. font_name, 12),
            command = lambda o = text: self. select(o)
        )
        btn. pack(side = "left", padx = 4)

        self. buttons[text] = btn

        return btn


    # ======================================
    # 新規タグを1つ追加する(4個たまるごとに新しい行を作る)
    # ======================================
    def add_new_tag_button(self, text):

        if self. new_tag_count % 4 == 0:
            self. current_new_row = ctk. CTkFrame(self. new_tags_area, fg_color = "transparent")
            self. current_new_row. pack(anchor = "w", pady = (0, 2))

        self. add_button(self. current_new_row, text)
        self. new_tag_count += 1


    def select(self, option):

        if self. selected is None:
            self. selected = []

        if option in self. selected:
            # すでに選ばれていれば解除
            self. selected. remove(option)

            self. buttons[option]. configure(
                fg_color = "#e6a5f8",
                hover_color = "#866091",
                text_color = "white"
            )
        else:
            # 選ばれていなければ追加
            self. selected. append(option)

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

        self. selected = []
        self. new_entry. delete(0, "end")


    # ======================================
    # 「新規」欄に入力があればボタン化して選択状態に追加する
    # ======================================
    def apply_new_tag_if_any(self):

        new_text = self. new_entry. get(). strip()

        if new_text:
            if new_text not in self. buttons:
                self. add_new_tag_button(new_text)

                # 次回起動時にも残るよう、呼び出し元(DataEntryApp)に保存を任せる
                if self. on_new_tag is not None:
                    self. on_new_tag(new_text)

            if self. selected is None:
                self. selected = []

            if new_text not in self. selected:
                self. selected. append(new_text)
                self. buttons[new_text]. configure(
                    fg_color = "#ff6f9f",
                    hover_color = "#ff6f9f",
                    text_color = "white"
                )

        return self. selected if self. selected else []


# ======================================
# データ登録ツール本体
# ======================================
class DataEntryApp(ctk. CTk):

    def __init__(self):
        super(). __init__()

        self. geometry("550x950")
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
                tone_tags TEXT,
                era_tags TEXT,
                season_tags TEXT
            )
        """)

        # カテゴリ(イメージ/季節/年代/地域)で「新規」欄から追加したタグを保存しておくテーブル
        # これが無いとアプリを再起動した時に追加したタグのボタンが消えてしまう
        self. cursor. execute("""
            CREATE TABLE IF NOT EXISTS custom_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_name TEXT,
                tag TEXT,
                UNIQUE(group_name, tag)
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

        self. registered_count = self. get_current_count()

        # ------------------------------------
        # 編集モード用の状態(データ一覧の行クリックで編集開始した時に使う)
        # ------------------------------------
        self. editing_id = None
        self. editing_extra_tags = {"image": [], "season": [], "era": [], "region": []}

        # ------------------------------------
        # データ一覧用の状態
        # ------------------------------------
        self. list_page_size = 30
        self. list_all_rows = []
        self. list_page_index = 0
        self. list_page_buttons = []
        self. list_sort_order = "new"  # "new"=新しい順 / "old"=古い順

        # ------------------------------------
        # スクロールエリア
        # ------------------------------------
        self. scroll = ctk. CTkScrollableFrame(self, fg_color = "white")
        self. scroll. pack(fill = "both", expand = True, padx = 10, pady = 10)

        # 登録件数表示
        self. count_label = ctk. CTkLabel(
            self. scroll,
            text = f"登録済み: {self. registered_count}件",
            font = ("ふてほど丸ゴシック", 12),
            text_color = "#555555"
        )
        self. count_label. pack(pady = (0, 6))

        # 名前欄(入力はさせない。次に何番として登録されるかを表示するだけ)
        ctk. CTkLabel(
            self. scroll,
            text = "名前",
            font = ("ふてほど丸ゴシック", 12)
        ). pack(anchor = "w", padx = 10)

        self. name_display = ctk. CTkLabel(
            self. scroll,
            text = str(self. registered_count + 1),
            width = 180,
            height = 26,
            corner_radius = 6,
            fg_color = "#eeeeee",
            text_color = "#555555",
            anchor = "w"
        )
        self. name_display. pack(anchor = "w", padx = 10, pady = (0, 8))

        # 3色分の入力欄(ベース/アクセント/サブ)
        self. color_widgets = {}

        self. build_color_row("base", "ベース", 70)
        self. build_color_row("accent", "アクセント", 10)
        self. build_color_row("sub", "サブ", 20)

        # タグ選択
        self. image_group = TagGroup(
            self. scroll, "イメージ",
            ["ビビッド", "ネオン", "くすみ", "パステル", "ポップ", "ナチュラル", "クール", "エレガント", "アース", "ヴィンテージ"],
            on_new_tag = lambda tag: self. save_custom_tag("イメージ", tag)
        )
        self. season_group = TagGroup(
            self. scroll, "季節", ["春", "夏", "秋", "冬"],
            on_new_tag = lambda tag: self. save_custom_tag("季節", tag)
        )
        self. era_group = TagGroup(
            self. scroll, "年代", ["70's", "80's", "90's", "00's"],
            on_new_tag = lambda tag: self. save_custom_tag("年代", tag)
        )
        self. region_group = TagGroup(
            self. scroll, "地域",
            ["南米・メキシコ", "北欧", "地中海", "アフリカン", "中東・モロッコ", "東アジア", "南国・トロピカル"],
            on_new_tag = lambda tag: self. save_custom_tag("地域", tag)
        )

        # 前回までに追加された新規タグを復元する(保存はここではしない)
        self. restore_custom_tags(self. image_group, "イメージ")
        self. restore_custom_tags(self. season_group, "季節")
        self. restore_custom_tags(self. era_group, "年代")
        self. restore_custom_tags(self. region_group, "地域")

        # 登録ボタン
        self. register_btn = ctk. CTkButton(
            self. scroll,
            text = "この配色を登録",
            width = 180,
            height = 34,
            corner_radius = 50,
            fg_color = "#ff6f6f",
            hover_color = "#e35555",
            text_color = "white",
            font = ("ふてほど丸ゴシック", 14, "bold"),
            command = self. register_entry
        )
        self. register_btn. pack(pady = (12, 2))

        # 編集中であることを示す表示(通常時は空文字で非表示状態)
        self. edit_status_label = ctk. CTkLabel(
            self. scroll,
            text = "",
            font = ("ふてほど丸ゴシック", 11),
            text_color = "#e35555"
        )
        self. edit_status_label. pack(pady = (0, 2))

        # 編集をやめるボタン(編集中のみ表示、普段は非表示)
        self. cancel_edit_btn = ctk. CTkButton(
            self. scroll,
            text = "編集をやめる",
            width = 140,
            height = 26,
            corner_radius = 50,
            fg_color = "#dddddd",
            hover_color = "#cccccc",
            text_color = "black",
            font = ("ふてほど丸ゴシック", 12),
            command = self. cancel_edit
        )
        # 最初は表示しない(編集開始時にpackする)

        # データ一覧ボタン
        self. list_btn = ctk. CTkButton(
            self. scroll,
            text = "データ一覧",
            width = 180,
            height = 34,
            corner_radius = 50,
            fg_color = "#e6a5f8",
            hover_color = "#866091",
            text_color = "white",
            font = ("ふてほど丸ゴシック", 14, "bold"),
            command = self. open_data_list
        )
        self. list_btn. pack(pady = (8, 20))


    # ======================================
    # 現在の登録件数を取得
    # ======================================
    def get_current_count(self):

        self. cursor. execute("SELECT COUNT(*) FROM presets")
        return self. cursor. fetchone()[0]


    # ======================================
    # カテゴリの「新規」欄から追加されたタグをcolpama.dbに保存する
    # ======================================
    def save_custom_tag(self, group_name, tag):

        self. cursor. execute(
            "INSERT OR IGNORE INTO custom_tags (group_name, tag) VALUES (?, ?)",
            (group_name, tag)
        )
        self. conn. commit()


    # ======================================
    # 起動時に、そのカテゴリで過去に追加された新規タグをボタンとして復元する
    # ======================================
    def restore_custom_tags(self, group, group_name):

        self. cursor. execute(
            "SELECT tag FROM custom_tags WHERE group_name = ? ORDER BY id ASC",
            (group_name,)
        )

        for (tag,) in self. cursor. fetchall():
            if tag not in group. buttons:
                group. add_new_tag_button(tag)


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
        row. pack(fill = "x", padx = 10, pady = 3)

        ctk. CTkLabel(
            row,
            text = label_text,
            width = 50,
            font = ("ふてほど丸ゴシック", 12),
            text_color = "#555555"
        ). pack(side = "left")

        eyedropper_btn = ctk. CTkButton(
            row,
            text = "💉",
            width = 30,
            height = 26,
            corner_radius = 50,
            fg_color = "#e6a5f8",
            hover_color = "#866091",
            text_color = "white",
            command = lambda k = key: self. start_eyedropper(k)
        )
        eyedropper_btn. pack(side = "left", padx = 4)

        ToolTip(eyedropper_btn, "スポイト")

        hex_entry = ctk. CTkEntry(row, width = 80, height = 26, placeholder_text = "#FFFFFF")
        hex_entry. pack(side = "left", padx = 4)
        hex_entry. bind("<Return>", lambda e, k = key: self. on_hex_entry_enter(k))

        preview = ctk. CTkLabel(
            row,
            text = "",
            width = 26,
            height = 26,
            corner_radius = 6,
            fg_color = "#FFFFFF"
        )
        preview. pack(side = "left", padx = 4)

        # 既定の比率(コード欄のすぐ右隣に表示、固定値)
        ctk. CTkLabel(
            row,
            text = f"{default_pct}%",
            width = 35,
            font = ("ふてほど丸ゴシック", 11),
            text_color = "#555555"
        ). pack(side = "left", padx = 4)

        # 手打ちで上書きしたい時だけ使う欄(一番右端、優先される)
        override_entry = ctk. CTkEntry(row, width = 45, height = 26, placeholder_text = "%指定")
        override_entry. pack(side = "left", padx = 4)

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

        # 名前は自動採番(次に登録される番号)。編集(更新)の時は元の値を変えない
        name = str(self. registered_count + 1)

        base_hex = self. color_widgets["base"]["hex_entry"]. get(). strip()
        accent_hex = self. color_widgets["accent"]["hex_entry"]. get(). strip()
        sub_hex = self. color_widgets["sub"]["hex_entry"]. get(). strip()

        if not (base_hex and accent_hex and sub_hex):
            print("3色すべて入力してください")
            return

        base_pct = self. get_pct("base")
        accent_pct = self. get_pct("accent")
        sub_pct = self. get_pct("sub")

        # 新規タグがあればボタン化してから、実際に使うタグ名をカテゴリ別に取得
        image_selected = self. image_group. apply_new_tag_if_any()
        season_selected = self. season_group. apply_new_tag_if_any()
        era_selected = self. era_group. apply_new_tag_if_any()
        region_selected = self. region_group. apply_new_tag_if_any()

        # 編集中の場合、元々付いていたが今のグループには存在しないタグを、同じカテゴリのまま保持しておく
        if self. editing_id is not None:
            for tag in self. editing_extra_tags["image"]:
                if tag not in image_selected:
                    image_selected. append(tag)

            for tag in self. editing_extra_tags["season"]:
                if tag not in season_selected:
                    season_selected. append(tag)

            for tag in self. editing_extra_tags["era"]:
                if tag not in era_selected:
                    era_selected. append(tag)

            for tag in self. editing_extra_tags["region"]:
                if tag not in region_selected:
                    region_selected. append(tag)

        tone_tags = ",". join(image_selected)
        era_tags = ",". join(era_selected)
        season_tags = ",". join(season_selected)
        region_tags = ",". join(region_selected)

        if self. editing_id is None:
            # 新規登録
            self. cursor. execute("""
                INSERT INTO presets (name, base_hex, base_pct, accent_hex, accent_pct, sub_hex, sub_pct, tone_tags, era_tags, season_tags, region_tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, base_hex, base_pct, accent_hex, accent_pct, sub_hex, sub_pct, tone_tags, era_tags, season_tags, region_tags))

            self. conn. commit()

            self. registered_count += 1
            self. count_label. configure(text = f"登録済み: {self. registered_count}件")
        else:
            # 既存データの上書き更新(名前欄は無いので元の名前はそのまま変更しない)
            self. cursor. execute("""
                UPDATE presets
                SET base_hex = ?, base_pct = ?, accent_hex = ?, accent_pct = ?, sub_hex = ?, sub_pct = ?,
                    tone_tags = ?, era_tags = ?, season_tags = ?, region_tags = ?
                WHERE id = ?
            """, (base_hex, base_pct, accent_hex, accent_pct, sub_hex, sub_pct, tone_tags, era_tags, season_tags, region_tags, self. editing_id))

            self. conn. commit()

        self. clear_form()


    # ======================================
    # 次の1件を入力しやすいようにフォームをリセット
    # ======================================
    def clear_form(self):

        self. name_display. configure(text = str(self. registered_count + 1))

        for key in self. color_widgets:
            self. color_widgets[key]["hex_entry"]. delete(0, "end")
            self. color_widgets[key]["preview"]. configure(fg_color = "#FFFFFF")
            self. color_widgets[key]["override_entry"]. delete(0, "end")

        self. image_group. reset()
        self. season_group. reset()
        self. era_group. reset()
        self. region_group. reset()

        # 編集モードだったら解除して、新規登録用の表示に戻す
        self. editing_id = None
        self. editing_extra_tags = {"image": [], "season": [], "era": [], "region": []}
        self. edit_status_label. configure(text = "")
        self. cancel_edit_btn. pack_forget()
        self. register_btn. configure(text = "この配色を登録")


    # ======================================
    # 編集をやめて、フォームを空の状態に戻す
    # ======================================
    def cancel_edit(self):

        self. clear_form()


    # ======================================
    # データ一覧の行を、上のフォームに読み込んで編集状態にする
    # ======================================
    def load_preset_for_edit(self, row):

        self. close_data_list()

        self. editing_id = row["id"]

        self. name_display. configure(text = str(row["no"]))

        self. apply_color("base", row["base_hex"])
        self. apply_color("accent", row["accent_hex"])
        self. apply_color("sub", row["sub_hex"])

        for key, pct in (
            ("base", row["base_pct"]),
            ("accent", row["accent_pct"]),
            ("sub", row["sub_pct"]),
        ):
            override_entry = self. color_widgets[key]["override_entry"]
            override_entry. delete(0, "end")
            override_entry. insert(0, str(pct))

        self. image_group. reset()
        self. season_group. reset()
        self. era_group. reset()
        self. region_group. reset()

        # カテゴリごとの列をそれぞれのグループに振り分ける。ボタンが無いタグ(古いカスタムタグなど)は
        # editing_extra_tags に退避しておき、更新登録の時に同じカテゴリのまま付け直す
        self. editing_extra_tags = {"image": [], "season": [], "era": [], "region": []}

        for extra_key, group, column in (
            ("image", self. image_group, "tone_tags"),
            ("season", self. season_group, "season_tags"),
            ("era", self. era_group, "era_tags"),
            ("region", self. region_group, "region_tags"),
        ):
            tags = [t for t in (row[column] or ""). split(",") if t]

            for tag in tags:
                if tag in group. buttons:
                    group. select(tag)
                else:
                    self. editing_extra_tags[extra_key]. append(tag)

        self. edit_status_label. configure(text = f"No.{row['no']}を編集中(登録すると上書きされます)")
        self. cancel_edit_btn. pack(pady = (0, 2), before = self. list_btn)
        self. register_btn. configure(text = "この内容で更新する")


    # ======================================
    # データ一覧：登録済みデータを1件削除する
    # ======================================
    def delete_preset(self, row_id):

        self. cursor. execute("DELETE FROM presets WHERE id = ?", (row_id,))
        self. conn. commit()

        self. registered_count = self. get_current_count()
        self. count_label. configure(text = f"登録済み: {self. registered_count}件")

        keep_page = self. list_page_index
        self. refresh_list_data()
        self. build_list_pagination(keep_page = keep_page)


    # ======================================
    # データ一覧：画面を開く(ウィンドウ最大化＋登録フォームを隠して一覧を表示)
    # ======================================
    def open_data_list(self):

        self. scroll. pack_forget()

        self. state("zoomed")

        if not hasattr(self, "list_frame"):
            self. build_list_frame()

        self. refresh_list_data()
        self. build_list_pagination()

        self. list_frame. pack(fill = "both", expand = True, padx = 10, pady = 10)


    # ======================================
    # データ一覧：画面を閉じて登録フォームに戻す(ウィンドウも元のサイズに戻す)
    # ======================================
    def close_data_list(self):

        if hasattr(self, "list_frame"):
            self. list_frame. pack_forget()

        self. state("normal")
        self. geometry("550x950")

        self. scroll. pack(fill = "both", expand = True, padx = 10, pady = 10)

        # 一覧側で削除している可能性があるので、件数と次の番号を最新の状態に合わせ直す
        # (編集読込の場合はこの直後にload_preset_for_editがNo.表示に上書きする)
        self. registered_count = self. get_current_count()
        self. count_label. configure(text = f"登録済み: {self. registered_count}件")
        self. name_display. configure(text = str(self. registered_count + 1))


    # ======================================
    # データ一覧：枠組み(戻るボタン・見出し行・一覧本体・ページ切り替え)を作る
    # ======================================
    def build_list_frame(self):

        self. list_frame = ctk. CTkFrame(self, fg_color = "white")

        # ------------------------------------
        # 上段：戻るボタンとタイトル
        # ------------------------------------
        top_row = ctk. CTkFrame(self. list_frame, fg_color = "transparent")
        top_row. pack(fill = "x", padx = 10, pady = (10, 4))

        back_btn = ctk. CTkButton(
            top_row,
            text = "← 戻る",
            width = 90,
            height = 30,
            corner_radius = 50,
            fg_color = "#dddddd",
            hover_color = "#cccccc",
            text_color = "black",
            font = ("ふてほど丸ゴシック", 13),
            command = self. close_data_list
        )
        back_btn. pack(side = "left")

        ctk. CTkLabel(
            top_row,
            text = "データ一覧",
            font = ("ふてほど丸ゴシック", 20, "bold")
        ). pack(side = "left", padx = 20)

        # ------------------------------------
        # 並び順切り替え(新しい順／古い順)
        # ------------------------------------
        sort_row = ctk. CTkFrame(top_row, fg_color = "transparent")
        sort_row. pack(side = "left", padx = (20, 0))

        ctk. CTkLabel(
            sort_row,
            text = "並び順:",
            font = ("ふてほど丸ゴシック", 12),
            text_color = "#555555"
        ). pack(side = "left", padx = (0, 6))

        self. sort_new_btn = ctk. CTkButton(
            sort_row,
            text = "新しい順",
            width = 80,
            height = 28,
            corner_radius = 50,
            font = ("ふてほど丸ゴシック", 12),
            command = lambda: self. set_list_sort("new")
        )
        self. sort_new_btn. pack(side = "left", padx = 2)

        self. sort_old_btn = ctk. CTkButton(
            sort_row,
            text = "古い順",
            width = 80,
            height = 28,
            corner_radius = 50,
            font = ("ふてほど丸ゴシック", 12),
            command = lambda: self. set_list_sort("old")
        )
        self. sort_old_btn. pack(side = "left", padx = 2)

        self. update_sort_buttons()

        # ------------------------------------
        # 表の列定義(見出し行と各データ行で共通して使う)
        # ------------------------------------
        self. list_columns = [
            ("no", "No.", 50),
            ("base", "ベース", 110),
            ("base_pct", "ベース%", 65),
            ("accent", "アクセント", 110),
            ("accent_pct", "アクセント%", 80),
            ("sub", "サブ", 110),
            ("sub_pct", "サブ%", 65),
            ("tone_tags", "イメージ", 130),
            ("season_tags", "季節", 100),
            ("era_tags", "年代", 100),
            ("region_tags", "地域", 130),
        ]

        # ------------------------------------
        # 見出し行(クリックしても何も起きない、ただのラベル)
        # ------------------------------------
        header_row = ctk. CTkFrame(self. list_frame, fg_color = "#eeeeee")
        header_row. pack(fill = "x", padx = 10, pady = (6, 0))

        for _, label_text, width in self. list_columns:
            ctk. CTkLabel(
                header_row,
                text = label_text,
                width = width,
                font = ("ふてほど丸ゴシック", 12, "bold"),
                text_color = "#555555"
            ). pack(side = "left", padx = 2, pady = 6)

        # 削除ボタン分のスペース(見出しは空欄でよい)
        ctk. CTkLabel(header_row, text = "", width = 60). pack(side = "left")

        # ------------------------------------
        # データ行を並べるスクロールエリア
        # ------------------------------------
        self. list_rows_scroll = ctk. CTkScrollableFrame(self. list_frame, fg_color = "white")
        self. list_rows_scroll. pack(fill = "both", expand = True, padx = 10, pady = (0, 4))

        # ------------------------------------
        # ページ切り替えボタンの行
        # ------------------------------------
        self. list_page_row = ctk. CTkFrame(self. list_frame, fg_color = "transparent")
        self. list_page_row. pack(fill = "x", padx = 10, pady = (0, 10))


    # ======================================
    # データ一覧：SQLiteから最新の内容を読み直す
    # 登録された順(id昇順)にNo.を1から振り直す。こうすると途中の1件を削除しても
    # 残りは自動的に詰まった連番になり、編集(id不変)ではNo.が変わらない
    # ======================================
    def refresh_list_data(self):

        self. cursor. execute("""
            SELECT id, name, base_hex, base_pct, accent_hex, accent_pct, sub_hex, sub_pct,
                   tone_tags, era_tags, season_tags, region_tags
            FROM presets
            ORDER BY id ASC
        """)

        rows = self. cursor. fetchall()

        self. list_all_rows = [
            {
                "no": i + 1,
                "id": r[0],
                "name": r[1],
                "base_hex": r[2],
                "base_pct": r[3],
                "accent_hex": r[4],
                "accent_pct": r[5],
                "sub_hex": r[6],
                "sub_pct": r[7],
                "tone_tags": r[8],
                "era_tags": r[9],
                "season_tags": r[10],
                "region_tags": r[11],
            }
            for i, r in enumerate(rows)
        ]


    # ======================================
    # データ一覧：並び順ボタンの見た目を、現在の選択状態に合わせて更新
    # ======================================
    def update_sort_buttons(self):

        if self. list_sort_order == "new":
            self. sort_new_btn. configure(fg_color = "#ff9fd0", hover_color = "#ff9fd0", text_color = "white")
            self. sort_old_btn. configure(fg_color = "#e6a5f8", hover_color = "#866091", text_color = "white")
        else:
            self. sort_old_btn. configure(fg_color = "#ff9fd0", hover_color = "#ff9fd0", text_color = "white")
            self. sort_new_btn. configure(fg_color = "#e6a5f8", hover_color = "#866091", text_color = "white")


    # ======================================
    # データ一覧：並び順(新しい順／古い順)を切り替える
    # ======================================
    def set_list_sort(self, order):

        if self. list_sort_order == order:
            return

        self. list_sort_order = order
        self. update_sort_buttons()
        self. build_list_pagination()


    # ======================================
    # データ一覧：現在の並び順設定に沿った表示用の行リストを返す
    # ======================================
    def get_display_rows(self):

        if self. list_sort_order == "new":
            return list(reversed(self. list_all_rows))

        return self. list_all_rows


    # ======================================
    # データ一覧：件数に応じてページボタンを作り直す
    # ======================================
    def build_list_pagination(self, keep_page = 0):

        for widget in self. list_page_row. winfo_children():
            widget. destroy()

        total = len(self. list_all_rows)
        total_pages = max(1, (total + self. list_page_size - 1) // self. list_page_size)

        self. list_page_buttons = []

        for i in range(total_pages):
            btn = ctk. CTkButton(
                self. list_page_row,
                text = str(i + 1),
                width = 36,
                height = 28,
                corner_radius = 0,
                fg_color = "white",
                hover_color = "#f0d9f5",
                text_color = "#555555",
                border_width = 1,
                border_color = "#d0d0d0",
                command = lambda i = i: self. switch_list_page(i)
            )
            btn. pack(side = "left")

            self. list_page_buttons. append(btn)

        target_page = keep_page if keep_page < total_pages else 0
        self. switch_list_page(target_page)


    # ======================================
    # データ一覧：表示するページを切り替える
    # ======================================
    def switch_list_page(self, index):

        self. list_page_index = index

        for i, btn in enumerate(self. list_page_buttons):
            if i == index:
                btn. configure(fg_color = "#ff9fd0", text_color = "white")
            else:
                btn. configure(fg_color = "white", text_color = "#555555")

        self. render_list_page(index)


    # ======================================
    # データ一覧：現在のページぶんの行を描画する
    # ======================================
    def render_list_page(self, index):

        for widget in self. list_rows_scroll. winfo_children():
            widget. destroy()

        start = index * self. list_page_size
        page_rows = self. get_display_rows()[start : start + self. list_page_size]

        if not page_rows:
            ctk. CTkLabel(
                self. list_rows_scroll,
                text = "まだ登録されたデータがありません",
                font = ("ふてほど丸ゴシック", 13),
                text_color = "#888888"
            ). pack(pady = 20)
            return

        for row in page_rows:
            self. build_list_row(row)


    # ======================================
    # データ一覧：行を1つ作る(クリックで編集読込、右端に削除ボタン)
    # ======================================
    def build_list_row(self, row):

        row_frame = ctk. CTkFrame(self. list_rows_scroll, fg_color = "white")
        row_frame. pack(fill = "x", pady = 1)

        # クリックで編集読込する部分(削除ボタンは含めない)
        content_frame = ctk. CTkFrame(row_frame, fg_color = "white", cursor = "hand2")
        content_frame. pack(side = "left", fill = "x", expand = True)

        ctk. CTkLabel(
            content_frame,
            text = str(row["no"]),
            width = 50,
            anchor = "w",
            font = ("ふてほど丸ゴシック", 12),
            text_color = "#555555"
        ). pack(side = "left", padx = 2, pady = 4)

        self. build_color_cell(content_frame, row["base_hex"], 110)
        self. build_pct_cell(content_frame, row["base_pct"], 65)

        self. build_color_cell(content_frame, row["accent_hex"], 110)
        self. build_pct_cell(content_frame, row["accent_pct"], 80)

        self. build_color_cell(content_frame, row["sub_hex"], 110)
        self. build_pct_cell(content_frame, row["sub_pct"], 65)

        for column, width in (("tone_tags", 130), ("season_tags", 100), ("era_tags", 100), ("region_tags", 130)):
            ctk. CTkLabel(
                content_frame,
                text = row[column] or "",
                width = width,
                anchor = "w",
                font = ("ふてほど丸ゴシック", 11),
                text_color = "#555555"
            ). pack(side = "left", padx = 2, pady = 4)

        delete_btn = ctk. CTkButton(
            row_frame,
            text = "🗑",
            width = 40,
            height = 28,
            corner_radius = 50,
            fg_color = "#dddddd",
            hover_color = "#cccccc",
            text_color = "black",
            command = lambda r = row: self. delete_preset(r["id"])
        )
        delete_btn. pack(side = "left", padx = (2, 10))

        ToolTip(delete_btn, "削除")

        self. bind_row_click(content_frame, row)


    # ======================================
    # データ一覧：色スウォッチ＋HEXコードのセルを作る
    # ======================================
    def build_color_cell(self, parent, hex_color, width):

        cell = ctk. CTkFrame(parent, fg_color = "transparent", width = width, height = 28)
        cell. pack_propagate(False)
        cell. pack(side = "left", padx = 2, pady = 4)

        ctk. CTkLabel(
            cell,
            text = "",
            width = 20,
            height = 20,
            corner_radius = 4,
            fg_color = hex_color
        ). pack(side = "left")

        ctk. CTkLabel(
            cell,
            text = hex_color. upper(),
            font = ("ふてほど丸ゴシック", 11),
            text_color = "#555555"
        ). pack(side = "left", padx = (4, 0))

        return cell


    # ======================================
    # データ一覧：比率(%)だけのセルを作る
    # ======================================
    def build_pct_cell(self, parent, pct, width):

        ctk. CTkLabel(
            parent,
            text = f"{pct}%",
            width = width,
            anchor = "w",
            font = ("ふてほど丸ゴシック", 12),
            text_color = "#555555"
        ). pack(side = "left", padx = 2, pady = 4)


    # ======================================
    # データ一覧：行のどこをクリックしても編集読込されるように、子要素にも再帰でbindする
    # ======================================
    def bind_row_click(self, widget, row):

        widget. bind("<Button-1>", lambda e, r = row: self. load_preset_for_edit(r))

        for child in widget. winfo_children():
            self. bind_row_click(child, row)


app = DataEntryApp()
app. mainloop()