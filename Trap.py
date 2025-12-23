import pygame

class Trap:
    """トラップクラス（透明化）"""
    def __init__(self, x: int, y: int, tile_size: int, trap_type: str = "spike"):
        """
        トラップを初期化
        
        Args:
            x: タイル座標X
            y: タイル座標Y
            tile_size: タイルサイズ（ピクセル単位）
            trap_type: トラップの種類 ("spike", "fire", "poison")
        """
        # トラップのタイル座標（マップ上の位置）
        self.tile_x = x
        self.tile_y = y
        
        # タイルのサイズ（ピクセル単位、例: 16, 32, 48など）
        self.tile_size = tile_size
        
        # トラップの種類（"spike": トゲ, "fire": 炎, "poison": 毒）
        self.trap_type = trap_type
        
        # トラップが有効かどうか（Falseになると機能しなくなる）
        self.active = True
        
        # トラップが一度でも発動したかどうか（同じトラップで複数回ダメージを受けないため）
        self.triggered = False
        
        # トラップの種類ごとのダメージ量を辞書で定義し、該当する値を取得
        # spike=10, fire=15, poison=5。該当しない場合はデフォルトで10
        self.damage = {"spike": 10, "fire": 15, "poison": 5}.get(trap_type, 10)
    
    def get_rect(self) -> pygame.Rect:
        """トラップの矩形を取得"""
        # タイル座標をピクセル座標に変換してpygame.Rectオブジェクトを返す
        # これは衝突判定に使用される
        return pygame.Rect(
            self.tile_x * self.tile_size,    # X座標（ピクセル）
            self.tile_y * self.tile_size,    # Y座標（ピクセル）
            self.tile_size,                  # 幅（ピクセル）
            self.tile_size                   # 高さ（ピクセル）
        )
    
    def check_collision(self, player_rect: pygame.Rect) -> bool:
        """プレイヤーとの衝突判定"""
        # トラップが無効化されている場合は衝突しない
        if not self.active:
            return False
        
        # トラップの矩形とプレイヤーの矩形が重なっているかチェック
        return self.get_rect().colliderect(player_rect)
    
    def activate(self) -> int:
        """トラップを発動してダメージを返す"""
        # トラップが有効で、かつまだ発動していない場合のみダメージを与える
        if self.active and not self.triggered:
            # 発動フラグを立てる（これ以降はダメージを与えない）
            self.triggered = True
            # ダメージ量を返す
            return self.damage
        
        # 既に発動済み、または無効化されている場合は0ダメージ
        return 0
    
    def deactivate(self):
        """トラップを無効化"""
        # トラップを完全に無効化する（衝突判定もされなくなる）
        self.active = False
    
    def update(self, dt: float = 1.0):
        """更新（透明なので特に処理なし）"""
        # 透明トラップはアニメーションなどが不要なため、何もしない
        # dtはデルタタイム（フレーム間の時間）だが、ここでは未使用
        pass
    
    def draw(self, surface: pygame.Surface, camera_x: int = 0, camera_y: int = 0, show_debug: bool = False):
        """トラップを描画（デバッグモードでのみ表示）"""
        # デバッグモードがオフ、またはトラップが無効化されている場合は描画しない
        if not show_debug or not self.active:
            return
        
        # ワールド座標からスクリーン座標に変換（カメラオフセットを引く）
        screen_x = self.tile_x * self.tile_size - camera_x
        screen_y = self.tile_y * self.tile_size - camera_y
        
        # 画面外にあるトラップは描画をスキップ（パフォーマンス向上）
        if (screen_x < -self.tile_size or screen_x > surface.get_width() or
            screen_y < -self.tile_size or screen_y > surface.get_height()):
            return
        
        # デバッグ表示用：トラップの種類ごとに色を設定
        # 各色の最後の値(128)はアルファ値（透明度、0=完全透明、255=不透明）
        color = {
            "spike": (255, 0, 0, 128),      # 赤（半透明）
            "fire": (255, 165, 0, 128),     # オレンジ（半透明）
            "poison": (0, 255, 0, 128)      # 緑（半透明）
        }.get(self.trap_type, (255, 0, 0, 128))  # デフォルトは赤
        
        # 半透明の矩形を描画するため、SRCALPHA付きのSurfaceを作成
        s = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
        # 作成したSurfaceを指定色で塗りつぶす
        s.fill(color)
        # 半透明の矩形をメイン画面に描画
        surface.blit(s, (screen_x, screen_y))
        
        # 罠の種類を示すマークを白色で描画
        if self.trap_type == "spike":
            # トゲトラップ：縦線を描画
            pygame.draw.line(
                surface,                                        # 描画先Surface
                (255, 255, 255),                               # 白色
                (screen_x + self.tile_size // 2, screen_y + 4),  # 始点（上）
                (screen_x + self.tile_size // 2, screen_y + self.tile_size - 4),  # 終点（下）
                2                                              # 線の太さ
            )
        elif self.trap_type == "fire":
            # 炎トラップ：小さい円を描画
            pygame.draw.circle(
                surface,                                        # 描画先Surface
                (255, 255, 255),                               # 白色
                (screen_x + self.tile_size // 2, screen_y + self.tile_size // 2),  # 中心座標
                3                                              # 半径
            )
        elif self.trap_type == "poison":
            # 毒トラップ：さらに小さい円を描画
            pygame.draw.circle(
                surface,                                        # 描画先Surface
                (255, 255, 255),                               # 白色
                (screen_x + self.tile_size // 2, screen_y + self.tile_size // 2),  # 中心座標
                2                                              # 半径
            )