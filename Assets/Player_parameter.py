import pygame


class Player_Parameter:

    def __init__(self):
        super().__init__()
        """
        プレイヤーのパラメーターを初期化
        """
        self.base_hp = 100
        self.base_atk = 5
        self.base_def = 5
        self.base_mp = 5

        self.Player_lv = 1
        self.Player_exp = 0

        # -----計算後のステータス-----
        self.max_hp = 0
        self.current_hp = 0
        self.atk = 0
        self.def_ = 0
        self.mp = 0

        self.Calc_Status()
        self.current_hp = self.max_hp



    def Calc_Status(self):
        """
        レベルを参照しステータスの更新を行う
        """
        # レベルアップで最大HPなどが増える計算
        self.max_hp = self.base_hp + self.Player_lv
        self.atk = self.base_atk + self.Player_lv
        self.def_ = self.base_def + self.Player_lv
        self.mp = self.base_mp + self.Player_lv

    
    def Levelup(self):
        """
        経験値Player_expが一定の数値になった際レベルアップする関数
        """
        if self.Player_exp >= 100:
            self.Player_exp = self.Player_exp - 100         # レベルアップ分の数値を引く
            self.Player_lv = self.Player_lv + 1         # レベルを示す数値を1加算させる
            
            # レベルアップしたので最大ステータスの再計算を行う
            old_max_hp = self.max.hp
            self.Calc_Status()

            # 最大HPが増えた分、現HPも回復させる
            self.current_hp += (self.max_hp - old_max_hp)

            print(f"Level Up! Lv.{self.Player_lv}")         # デバッグ用

    
    def Trap_dmg(self, x: int):
        """
        トラップが発動した際hpからダメージ分減算する関数

        Args:
            x: ダメージ量X
        """
        self.current_hp = self.current_hp - x

        # 死亡判定の為HPが0未満にならないようにする
        if self.current_hp < 0:
            self.current_hp = 0

        print(f"ダメージを受けました。残りHP:{self.current_hp}/{self.max_hp}")          #デバッグ用

        return self.current_hp


