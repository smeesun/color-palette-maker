# import customtkinter as ctk
# import pyautogui
# from pynput import mouse
# from PIL import Image

# print("OK!")





# import customtkinter as ctk

# app = ctk.CTk()
# app.geometry("400x200")

# # ボタンの色を徐々に変えるアニメーション関数
# def animate_color(current_step=0):
#     if current_step <= 10:
#         # 緑から青へ色を変化させる例（簡易的な段階処理）
#         r = int(53 - (53 - 33) * (current_step / 10))
#         g = int(162 - (162 - 150) * (current_step / 10))
#         b = int(159 - (159 - 243) * (current_step / 10))
#         hex_color = f"#{r:02x}{g:02x}{b:02x}"
        
#         button.configure(fg_color=hex_color)
#         # 20ミリ秒後に次のステップを実行
#         app.after(20, lambda: animate_color(current_step + 1))

# def on_click():
#     animate_color(0)

# button = ctk.CTkButton(app, text="モーションボタン", command=on_click)
# button.pack(pady=50)

# app.mainloop()






import customtkinter as ctk

app = ctk.CTk()
app.geometry("300x200")

button = ctk.CTkButton(app, text="色が変わるよ", fg_color="#1f538d")
button.pack(pady=50)

# RGBを補間して徐々に色を変更する関数
def animate_color(r1, g1, b1, r2, g2, b2, steps=20, current=0):
    if current <= steps:
        # 現在のステップのRGB値を計算
        r = int(r1 + (r2 - r1) * (current / steps))
        g = int(g1 + (g2 - g1) * (current / steps))
        b = int(b1 + (b2 - b1) * (current / steps))
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        
        # ボタンの色を更新
        button.configure(fg_color=hex_color)
        
        # 50ミリ秒後に次のステップを実行
        app.after(50, animate_color, r1, g1, b1, r2, g2, b2, steps, current + 1)

# ボタンをクリックしたときに青(#1f538d)から赤(#d32f2f)へ滑らかに変化させる
def start_animation():
    animate_color(31, 83, 141, 211, 47, 47, steps=30, current=0)

button.configure(command=start_animation)

app.mainloop()



#test
#自宅でもgithubとVScodekaが連携されてるか確認