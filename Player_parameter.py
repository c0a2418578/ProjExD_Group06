import pygame

class Player_Parameter:

    def __init__(self):
        super().__init__()
        """
        プレイヤーのパラメーターを取得
        """
        self.Prayer_hp =  10
        self.Player_atk = 5
        self.Player_def = 5
        self.Player_mp = 5
        self.Player_lv = 1
        self.Player_exp = 0


    def Calc_Status(self):
        """
        レベルを参照しステータスを決定
        """
        self.calc_hp = self.Prayer_hp + self.Player_lv
        self.calc_atk = self.Player_atk + self.Player_lv
        self.calc_def = self.Player_def + self.Player_lv
        self.calc_mp = self.Player_mp + self.Player_lv

    
    def Levelup(self):
        """
        経験値Player_expが一定の数値になった際レベルアップする関数
        """
        if self.Player_exp >= 100:
            self.Player_exp = self.Player_exp - 100         #レベルアップ分の数値を引く
            self.Player_lv = self.Player_lv + 1         #レベルを示す数値を1加算させる

