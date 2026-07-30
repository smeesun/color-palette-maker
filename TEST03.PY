import customtkinter as ctk
from PIL import Image


# ======================================
# テーマ設定
# ======================================
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


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

        self.select_frame = ctk.CTkFrame(
            self.scroll,
            fg_color="white"
        )

        self.select_frame.pack(
            fill="x",
            pady=10
        )


        ctk.CTkLabel(
            self.select_frame,
            text="セレクト",
            font=("あめふりドロップス無料版", 22, "bold")
        ).pack(anchor="w", padx=15)


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


        ctk.CTkLabel(
            self.category_frame,
            text="カテゴリ",
            font=("あめふりドロップス無料版", 22, "bold")
        ).pack(anchor="w", padx=15)


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


        ctk.CTkLabel(
            self.preset_frame,
            text="プリセット",
            font=("あめふりドロップス無料版", 22, "bold")
        ).pack(anchor="w", padx=15)


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


        ctk.CTkLabel(
            self.recommend_frame,
            text="ラッキーカラー",
            font=("あめふりドロップス無料版", 22, "bold")
        ).pack()


        self.space()


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