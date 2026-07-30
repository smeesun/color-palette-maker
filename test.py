import customtkinter as ctk
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import platform
import json
from datetime import datetime

# 日本語フォント設定
import matplotlib.font_manager as fm
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')

def setup_japanese_font():
    """OS別に日本語フォントを設定"""
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    system = platform.system()
    
    if system == 'Windows':
        fonts = ['Yu Gothic', 'MS Gothic', 'Meiryo']
    elif system == 'Darwin':  # macOS
        fonts = ['Hiragino Sans', 'Osaka', 'AppleGothic']
    else:  # Linux
        fonts = ['Noto Sans CJK JP', 'TakaoGothic', 'IPAGothic']
    
    for font in fonts:
        if font in available_fonts:
            plt.rcParams['font.family'] = font
            return True
    
    # フォールバック
    plt.rcParams['font.family'] = 'DejaVu Sans'
    return False

setup_japanese_font()

# スパイスデータベース
SPICE_DATABASE = {
    "クミン": {
        "color": "#8B4513",
        "properties": {"辛さ": 2, "香り": 8, "苦み": 3, "甘み": 1, "酸味": 0},
        "description": "カレーの基本スパイス。土っぽい香りが特徴",
        "emoji": "🌰"
    },
    "ターメリック": {
        "color": "#FFD700",
        "properties": {"辛さ": 0, "香り": 3, "苦み": 4, "甘み": 0, "酸味": 0},
        "description": "黄色い色付けと独特の土臭さ",
        "emoji": "🟡"
    },
    "コリアンダー": {
        "color": "#DEB887",
        "properties": {"辛さ": 1, "香り": 6, "苦み": 2, "甘み": 3, "酸味": 1},
        "description": "柑橘系の爽やかな香り",
        "emoji": "🌿"
    },
    "カルダモン": {
        "color": "#90EE90",
        "properties": {"辛さ": 3, "香り": 9, "苦み": 1, "甘み": 4, "酸味": 0},
        "description": "スパイスの女王。上品で清涼感のある香り",
        "emoji": "💚"
    },
    "シナモン": {
        "color": "#D2691E",
        "properties": {"辛さ": 2, "香り": 7, "苦み": 1, "甘み": 8, "酸味": 0},
        "description": "甘くてスパイシーな香り",
        "emoji": "🟫"
    },
    "チリパウダー": {
        "color": "#DC143C",
        "properties": {"辛さ": 9, "香り": 4, "苦み": 2, "甘み": 0, "酸味": 1},
        "description": "強烈な辛さ。使いすぎ注意！",
        "emoji": "🌶️"
    },
    "ガラムマサラ": {
        "color": "#8B4513",
        "properties": {"辛さ": 4, "香り": 8, "苦み": 2, "甘み": 3, "酸味": 0},
        "description": "ミックススパイス。複雑で深い味わい",
        "emoji": "✨"
    },
    "フェヌグリーク": {
        "color": "#DAA520",
        "properties": {"辛さ": 1, "香り": 5, "苦み": 6, "甘み": 2, "酸味": 0},
        "description": "ほろ苦さとメープルのような甘い香り",
        "emoji": "🍂"
    }
}

# プリセットレシピ
PRESET_RECIPES = {
    "基本の家庭カレー": {
        "blend": {"クミン": 2, "ターメリック": 1, "コリアンダー": 2},
        "description": "バランスの取れた定番の味わい"
    },
    "スパイシーカレー": {
        "blend": {"チリパウダー": 3, "ガラムマサラ": 2, "カルダモン": 1},
        "description": "刺激的で本格的な辛口カレー"
    },
    "マイルドカレー": {
        "blend": {"シナモン": 2, "カルダモン": 2, "コリアンダー": 1},
        "description": "子供も食べやすい甘口カレー"
    },
    "本格インドカレー": {
        "blend": {"クミン": 2, "コリアンダー": 2, "ガラムマサラ": 1, "フェヌグリーク": 1},
        "description": "複雑で深みのある本格派"
    }
}

class SpiceBlendMaker:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("カレースパイスブレンドメーカー")
        self.root.geometry("1300x750")
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # ブレンド状態を管理
        self.current_blend = {}
        self.saved_recipes = []
        
        self.setup_ui()
        
    def setup_ui(self):
        # メインフレーム
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 左側：スパイス棚
        self.create_spice_shelf(main_frame)
        
        # 中央：ブレンドボウル
        self.create_blend_bowl(main_frame)
        
        # 右側：結果表示
        self.create_result_panel(main_frame)
    
    def create_spice_shelf(self, parent):
        shelf_frame = ctk.CTkFrame(parent, width=350)
        shelf_frame.pack(side="left", fill="y", padx=5, pady=5)
        
        title = ctk.CTkLabel(shelf_frame, text="🌶️ スパイス棚", 
                           font=ctk.CTkFont(size=22, weight="bold"))
        title.pack(pady=10)
        
        # タブビュー
        tab_view = ctk.CTkTabview(shelf_frame)
        tab_view.pack(fill="both", expand=True, padx=10, pady=10)
        
        # スパイス一覧タブ
        spice_tab = tab_view.add("スパイス")
        self.create_spice_list(spice_tab)
        
        # プリセットタブ
        preset_tab = tab_view.add("プリセット")
        self.create_preset_list(preset_tab)
    
    def create_spice_list(self, parent):
        # スクロール可能なフレーム
        scroll_frame = ctk.CTkScrollableFrame(parent)
        scroll_frame.pack(fill="both", expand=True)
        
        for spice_name, spice_data in SPICE_DATABASE.items():
            self.create_spice_card(scroll_frame, spice_name, spice_data)
    
    def create_preset_list(self, parent):
        scroll_frame = ctk.CTkScrollableFrame(parent)
        scroll_frame.pack(fill="both", expand=True)
        
        for recipe_name, recipe_data in PRESET_RECIPES.items():
            self.create_preset_card(scroll_frame, recipe_name, recipe_data)
    
    def create_spice_card(self, parent, name, data):
        card = ctk.CTkFrame(parent, fg_color=("#f0f0f0", "#2b2b2b"))
        card.pack(fill="x", pady=5, padx=5)
        
        # ヘッダー（絵文字とスパイス名）
        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.pack(fill="x", pady=5, padx=10)
        
        emoji_label = ctk.CTkLabel(header_frame, text=data["emoji"], 
                                 font=ctk.CTkFont(size=20))
        emoji_label.pack(side="left", padx=5)
        
        name_label = ctk.CTkLabel(header_frame, text=name, 
                                font=ctk.CTkFont(size=16, weight="bold"))
        name_label.pack(side="left", padx=5)
        
        # 説明文
        desc_label = ctk.CTkLabel(card, text=data["description"], 
                                wraplength=280, justify="left",
                                font=ctk.CTkFont(size=12))
        desc_label.pack(pady=5, padx=10)
        
        # 追加ボタン
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(fill="x", pady=5, padx=10)
        
        add_btn = ctk.CTkButton(btn_frame, text="+ 追加", width=80,
                              command=lambda: self.add_spice_to_blend(name))
        add_btn.pack(side="left", padx=2)
        
        add_multi_btn = ctk.CTkButton(btn_frame, text="+3 追加", width=80,
                                    command=lambda: self.add_spice_to_blend(name, 3))
        add_multi_btn.pack(side="left", padx=2)
    
    def create_preset_card(self, parent, name, data):
        card = ctk.CTkFrame(parent, fg_color=("#e8f4f8", "#1e3a4c"))
        card.pack(fill="x", pady=5, padx=5)
        
        name_label = ctk.CTkLabel(card, text=f"🍛 {name}", 
                                font=ctk.CTkFont(size=14, weight="bold"))
        name_label.pack(pady=5)
        
        desc_label = ctk.CTkLabel(card, text=data["description"],
                                wraplength=280, justify="left",
                                font=ctk.CTkFont(size=12))
        desc_label.pack(pady=5, padx=10)
        
        # ブレンド内容表示
        blend_text = " + ".join([f"{s}×{a}" for s, a in data["blend"].items()])
        blend_label = ctk.CTkLabel(card, text=blend_text,
                                 font=ctk.CTkFont(size=11),
                                 fg_color=("#d0d0d0", "#404040"))
        blend_label.pack(pady=5, padx=10)
        
        apply_btn = ctk.CTkButton(card, text="このレシピを使用",
                                command=lambda: self.apply_preset(data["blend"]))
        apply_btn.pack(pady=5)
    
    def create_blend_bowl(self, parent):
        bowl_frame = ctk.CTkFrame(parent, width=400)
        bowl_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        title = ctk.CTkLabel(bowl_frame, text="🥣 ブレンドボウル", 
                           font=ctk.CTkFont(size=22, weight="bold"))
        title.pack(pady=10)
        
        # 現在のブレンド表示
        list_frame = ctk.CTkFrame(bowl_frame)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.blend_listbox = tk.Listbox(list_frame, height=15, 
                                      bg='#2b2b2b', fg='white',
                                      selectbackground='#1f538d',
                                      font=('Arial', 11))
        self.blend_listbox.pack(fill="both", expand=True)
        
        # ボタンフレーム
        btn_frame = ctk.CTkFrame(bowl_frame)
        btn_frame.pack(fill="x", padx=10, pady=5)
        
        # ボタン配置
        clear_btn = ctk.CTkButton(btn_frame, text="🗑️ クリア", 
                                command=self.clear_blend, width=100)
        clear_btn.pack(side="left", padx=5)
        
        remove_btn = ctk.CTkButton(btn_frame, text="➖ 削除", 
                                 command=self.remove_selected_spice, width=100)
        remove_btn.pack(side="left", padx=5)
            
    def create_result_panel(self, parent):
        result_frame = ctk.CTkFrame(parent, width=450)
        result_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        title = ctk.CTkLabel(result_frame, text="📊 ブレンド分析", 
                           font=ctk.CTkFont(size=22, weight="bold"))
        title.pack(pady=10)
        
        # レーダーチャート用のフレーム
        self.chart_frame = ctk.CTkFrame(result_frame, height=350)
        self.chart_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 情報パネル
        info_frame = ctk.CTkFrame(result_frame)
        info_frame.pack(fill="x", padx=10, pady=5)
        
        # カレータイプ表示
        self.curry_type_label = ctk.CTkLabel(info_frame, 
                                           text="カレータイプ: ---", 
                                           font=ctk.CTkFont(size=16, weight="bold"))
        self.curry_type_label.pack(pady=5)
        
        # 詳細情報
        self.detail_label = ctk.CTkLabel(info_frame, 
                                       text="ブレンドを作成してください", 
                                       font=ctk.CTkFont(size=12),
                                       wraplength=400)
        self.detail_label.pack(pady=5)
        
        # 合計表示
        self.total_label = ctk.CTkLabel(info_frame, 
                                      text="合計: 0種類 (0個)", 
                                      font=ctk.CTkFont(size=14))
        self.total_label.pack(pady=5)
        
        self.update_result_chart()
    
    def add_spice_to_blend(self, spice_name, amount=1):
        """スパイスをブレンドに追加（エラーハンドリング付き）"""
        try:
            if spice_name not in SPICE_DATABASE:
                raise ValueError(f"未知のスパイス: {spice_name}")
            
            if spice_name in self.current_blend:
                self.current_blend[spice_name] = min(self.current_blend[spice_name] + amount, 10)
            else:
                self.current_blend[spice_name] = amount
            
            self.update_blend_display()
            self.update_result_chart()
            
        except Exception as e:
            print(f"エラー: {e}")
    
    def apply_preset(self, preset_blend):
        """プリセットレシピを適用"""
        self.current_blend = preset_blend.copy()
        self.update_blend_display()
        self.update_result_chart()
    
    def remove_selected_spice(self):
        """選択したスパイスを削除"""
        selection = self.blend_listbox.curselection()
        if selection:
            idx = selection[0]
            spice_list = list(self.current_blend.keys())
            if idx < len(spice_list):
                spice_name = spice_list[idx]
                if self.current_blend[spice_name] > 1:
                    self.current_blend[spice_name] -= 1
                else:
                    del self.current_blend[spice_name]
                
                self.update_blend_display()
                self.update_result_chart()
    
    def update_blend_display(self):
        """ブレンド表示を更新"""
        self.blend_listbox.delete(0, tk.END)
        for spice, amount in self.current_blend.items():
            emoji = SPICE_DATABASE[spice]["emoji"]
            self.blend_listbox.insert(tk.END, f"{emoji} {spice} × {amount}")
        
        # 合計表示更新
        total_count = len(self.current_blend)
        total_amount = sum(self.current_blend.values())
        self.total_label.configure(text=f"合計: {total_count}種類 ({total_amount}個)")
    
    def clear_blend(self):
        """ブレンドをクリア"""
        self.current_blend = {}
        self.update_blend_display()
        self.update_result_chart()
        
    def calculate_blend_properties(self):
        """ブレンドの特性を計算"""
        if not self.current_blend:
            return {"辛さ": 0, "香り": 0, "苦み": 0, "甘み": 0, "酸味": 0}
        
        total_properties = {"辛さ": 0, "香り": 0, "苦み": 0, "甘み": 0, "酸味": 0}
        total_amount = sum(self.current_blend.values())
        
        for spice, amount in self.current_blend.items():
            spice_props = SPICE_DATABASE[spice]["properties"]
            weight = amount / total_amount
            
            for prop, value in spice_props.items():
                total_properties[prop] += value * weight
        
        # 0-10の範囲に正規化
        for prop in total_properties:
            total_properties[prop] = min(10, total_properties[prop])
        
        return total_properties
    
    def determine_curry_type(self, properties):
        """カレータイプを判定し、詳細な説明を返す"""
        spiciness = properties["辛さ"]
        aroma = properties["香り"]
        sweetness = properties["甘み"]
        bitterness = properties["苦み"]
        sourness = properties["酸味"]
        
        curry_type = ""
        detail = ""
        
        if spiciness > 7:
            curry_type = "🔥 激辛カレー系"
            detail = "非常に辛いカレー。水とヨーグルトを準備して挑戦しましょう！"
        elif sweetness > 5 and spiciness < 3:
            curry_type = "🍯 甘口カレー系"
            detail = "子供も食べやすい優しい味わい。りんごやはちみつとの相性抜群。"
        elif aroma > 6 and spiciness < 4:
            curry_type = "🌿 アロマティックカレー系"
            detail = "香り豊かで上品な味わい。食欲をそそる芳醇な香りが特徴。"
        elif spiciness > 4 and aroma > 5:
            curry_type = "🇮🇳 本格インドカレー系"
            detail = "バランスの取れた本格派。ナンやバスマティライスと相性抜群。"
        elif bitterness > 4:
            curry_type = "🍂 大人のビターカレー系"
            detail = "苦みが効いた深い味わい。ビールとの相性が良い。"
        else:
            curry_type = "🏠 家庭的カレー系"
            detail = "日本の家庭でよく作られる定番の味。どんな具材とも相性が良い。"
        
        return curry_type, detail
    
    def update_result_chart(self):
        """結果チャートを更新（メモリリーク対策済み）"""
        # 既存のチャートをクリア
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        properties = self.calculate_blend_properties()
        
        try:
            # レーダーチャート作成
            fig, ax = plt.subplots(figsize=(5, 4), subplot_kw=dict(projection='polar'))
            fig.patch.set_facecolor('#212121')
            
            categories = list(properties.keys())
            values = list(properties.values())
            
            # 角度を計算
            N = len(categories)
            angles = [n / float(N) * 2 * np.pi for n in range(N)]
            angles += angles[:1]
            values += values[:1]
            
            # プロット
            ax.plot(angles, values, 'o-', linewidth=2, color='#00a8ff', markersize=8)
            ax.fill(angles, values, alpha=0.25, color='#00a8ff')
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories, color='white', size=11)
            ax.set_ylim(0, 10)
            ax.set_facecolor('#212121')
            ax.tick_params(colors='white')
            ax.grid(True, color='#404040', linewidth=0.5)
            
            # Y軸のラベル
            ax.set_yticks([2, 4, 6, 8, 10])
            ax.set_yticklabels(['2', '4', '6', '8', '10'], color='#808080', size=9)
            
            # tkinterに埋め込み
            canvas = FigureCanvasTkAgg(fig, self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
            # カレータイプ更新
            curry_type, detail = self.determine_curry_type(properties)
            self.curry_type_label.configure(text=f"カレータイプ: {curry_type}")
            self.detail_label.configure(text=detail)
            
        finally:
            plt.close('all') 
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SpiceBlendMaker()
    app.run()
