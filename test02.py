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
        header = ctk.CTkFrame(self, height=40)
        header.pack(fill="x")

        home_btn = ctk.CTkButton(
            header,
            text="🏠 COLpama",
            width=80,
            fg_color="#e8aedd",
            hover_color="#e358c7", 
            text_color="white",
            command=self.go_home
        )
        home_btn.pack(side="left", padx=5, pady=5)

        # ======================================
        # スクロールエリア
        # ======================================
        self.scroll = ctk.CTkScrollableFrame(
            self, 
             # 背景の色
            fg_color="white" )
        
        self.scroll.pack(fill="both", expand=True)

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
        # 現在余白
        # ======================================
        for i in range(60):

            # ------------------------------
            # 空欄（後で好きなものを追加）
            # ------------------------------
            blank = ctk.CTkLabel(
                self.scroll,
                text="",      # ← 空欄
                height=30
            )
            blank.pack(pady=3)

        # ======================================
        # ↑ここまでコンテンツ
        # ======================================

    # ======================================
    # ホームボタン
    # 一番上へ戻る
    # ======================================
    def go_home(self):
        self.scroll._parent_canvas.yview_moveto(0)


# ======================================
# アプリ起動
# ======================================
app = App()
app.mainloop()