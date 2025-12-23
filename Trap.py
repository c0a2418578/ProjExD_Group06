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
        self.tile_x = x
        self.tile_y = y
        self.tile_size = tile_size
        self.trap_type = trap_type
        self.active = True
        self.triggered = False
        self.damage = {"spike": 10, "fire": 15, "poison": 5}.get(trap_type, 10)
    
    def get_rect(self) -> pygame.Rect:
        """トラップの矩形を取得"""
        return pygame.Rect(
            self.tile_x * self.tile_size,
            self.tile_y * self.tile_size,
            self.tile_size,
            self.tile_size
        )
    
    def check_collision(self, player_rect: pygame.Rect):
        """
        プレイヤーとの衝突判定
        
        Args:
            player_rect: プレイヤーの矩形
            
        Returns:
            tuple: (衝突したか, ダメージ量, 削除すべきか)
        """
        if not self.active:
            return False, 0, False
        
        # 衝突チェック
        if self.get_rect().colliderect(player_rect):
            # 衝突した場合、ダメージを計算して返す
            damage = self.activate()
            # ダメージが発生した場合は削除フラグをTrue
            should_remove = damage > 0
            return True, damage, should_remove
        
        return False, 0, False
    
    def activate(self) -> int:
        """トラップを発動してダメージを返す"""
        if self.active and not self.triggered:
            self.triggered = True
            return self.damage
        return 0
    
    def reset(self):
        """トラップをリセット（再利用可能にする）"""
        self.triggered = False
    
    def deactivate(self):
        """トラップを無効化"""
        self.active = False
    
    def update(self, dt: float = 1.0):
        """更新（透明なので特に処理なし）"""
        pass
    
    def draw(self, surface: pygame.Surface, camera_x: int = 0, camera_y: int = 0, show_debug: bool = False):
        """トラップを描画（デバッグモードでのみ表示）"""
        if not show_debug or not self.active:
            return
        
        screen_x = self.tile_x * self.tile_size - camera_x
        screen_y = self.tile_y * self.tile_size - camera_y
        
        if (screen_x < -self.tile_size or screen_x > surface.get_width() or
            screen_y < -self.tile_size or screen_y > surface.get_height()):
            return
        
        color = {
            "spike": (255, 0, 0, 128),
            "fire": (255, 165, 0, 128),
            "poison": (0, 255, 0, 128)
        }.get(self.trap_type, (255, 0, 0, 128))
        
        s = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
        s.fill(color)
        surface.blit(s, (screen_x, screen_y))
        
        if self.trap_type == "spike":
            pygame.draw.line(
                surface,
                (255, 255, 255),
                (screen_x + self.tile_size // 2, screen_y + 4),
                (screen_x + self.tile_size // 2, screen_y + self.tile_size - 4),
                2
            )
        elif self.trap_type == "fire":
            pygame.draw.circle(
                surface,
                (255, 255, 255),
                (screen_x + self.tile_size // 2, screen_y + self.tile_size // 2),
                3
            )
        elif self.trap_type == "poison":
            pygame.draw.circle(
                surface,
                (255, 255, 255),
                (screen_x + self.tile_size // 2, screen_y + self.tile_size // 2),
                2
            )