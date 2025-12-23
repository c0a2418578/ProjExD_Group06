import pygame
import random
from typing import List, Tuple
from map_engine.map_generator import MapGenerator
from Trap import Trap

class TrapManager:
    """トラップ管理クラス"""
    def __init__(self, tile_size: int):
        # トラップオブジェクトのリストを初期化（空のリスト）
        self.traps: List[Trap] = []
        
        # タイルサイズを保存（トラップ生成時に使用）
        self.tile_size = tile_size
    
    def generate_traps(self, map_gen: MapGenerator, trap_count: int = 20):
        """マップ上にランダムにトラップを生成"""
        # 既存のトラップをすべて削除（再生成時に古いトラップが残らないようにする）
        self.traps.clear()
        
        # 生成可能なトラップの種類リスト
        trap_types = ["spike", "fire", "poison"]
        
        # 試行回数のカウンター（無限ループを防ぐため）
        attempts = 0
        
        # 最大試行回数（指定数の10倍まで試行）
        max_attempts = trap_count * 10
        
        # 指定数のトラップを生成するまでループ（ただし最大試行回数まで）
        while len(self.traps) < trap_count and attempts < max_attempts:
            # 試行回数をカウント
            attempts += 1
            
            # ランダムなタイル座標を生成
            x = random.randint(0, map_gen.width - 1)   # X座標（0からマップ幅-1）
            y = random.randint(0, map_gen.height - 1)  # Y座標（0からマップ高さ-1）
            
            # 床の上にのみトラップを配置（tilemap[x][y]==1が床を示す）
            if map_gen.tilemap[x][y] == 1:
                # 既に同じ位置にトラップがないか確認
                # any()関数：リスト内に条件を満たす要素が1つでもあればTrue
                if not any(t.tile_x == x and t.tile_y == y for t in self.traps):
                    # トラップの種類をランダムに選択
                    trap_type = random.choice(trap_types)
                    
                    # 新しいトラップを生成してリストに追加
                    self.traps.append(Trap(x, y, self.tile_size, trap_type))
    
    def update(self, dt: float = 1.0):
        """全てのトラップを更新"""
        # 管理下の全トラップのupdateメソッドを呼び出す
        # dtはデルタタイム（フレーム間の経過時間）
        for trap in self.traps:
            trap.update(dt)
    
    def draw(self, surface: pygame.Surface, camera_x: int = 0, camera_y: int = 0, show_debug: bool = False):
        """全てのトラップを描画（デバッグモードでのみ表示）"""
        # 管理下の全トラップのdrawメソッドを呼び出す
        for trap in self.traps:
            # surface: 描画先のSurface
            # camera_x, camera_y: カメラのオフセット
            # show_debug: デバッグ表示フラグ（Trueで可視化）
            trap.draw(surface, camera_x, camera_y, show_debug)
    
    def check_collisions(self, player_rect: pygame.Rect) -> int:
        """プレイヤーとの衝突チェックして合計ダメージを返す"""
        # 合計ダメージを初期化
        total_damage = 0
        
        # 全てのトラップに対して衝突判定を行う
        for trap in self.traps:
            # プレイヤーの矩形とトラップが衝突しているかチェック
            if trap.check_collision(player_rect):
                # 衝突している場合、トラップを発動してダメージを取得
                damage = trap.activate()
                
                # ダメージが0より大きい場合（実際に発動した場合）
                if damage > 0:
                    # 合計ダメージに加算
                    total_damage += damage
        
        # 合計ダメージを返す（複数のトラップに同時に触れた場合は合計される）
        return total_damage