import pygame

class Stairs:
    """階段クラス"""
    def __init__(self, x: int, y: int, tile_size: int):
        """
        階段を初期化
        
        Args:
            x: タイル座標X
            y: タイル座標Y
            tile_size: タイルサイズ（ピクセル単位）
        """
        self.tile_x = x
        self.tile_y = y
        self.tile_size = tile_size
        
        # 階段の色（黄色系）
        self.color = (255, 215, 0)
        
    def get_rect(self) -> pygame.Rect:
        """階段の矩形を取得"""
        return pygame.Rect(
            self.tile_x * self.tile_size,
            self.tile_y * self.tile_size,
            self.tile_size,
            self.tile_size
        )
    
    def check_collision(self, player_rect: pygame.Rect) -> bool:
        """プレイヤーとの衝突判定"""
        return self.get_rect().colliderect(player_rect)
    
    def draw(self, surface: pygame.Surface, camera_x: int = 0, camera_y: int = 0):
        """階段を描画"""
        screen_x = self.tile_x * self.tile_size - camera_x
        screen_y = self.tile_y * self.tile_size - camera_y
        
        # 画面外チェック
        if (screen_x < -self.tile_size or screen_x > surface.get_width() or
            screen_y < -self.tile_size or screen_y > surface.get_height()):
            return
        
        # 階段の背景（黄色）
        pygame.draw.rect(
            surface,
            self.color,
            (screen_x, screen_y, self.tile_size, self.tile_size)
        )
        
        # 階段の段差を表現（3段の横線）
        step_count = 3
        step_height = self.tile_size // (step_count + 1)
        
        for i in range(1, step_count + 1):
            y_pos = screen_y + step_height * i
            pygame.draw.line(
                surface,
                (200, 180, 0),  # 少し暗い黄色
                (screen_x, y_pos),
                (screen_x + self.tile_size, y_pos),
                2
            )
        
        # 下向き矢印を描画
        arrow_color = (100, 80, 0)
        center_x = screen_x + self.tile_size // 2
        center_y = screen_y + self.tile_size // 2
        
        # 矢印の縦線
        pygame.draw.line(
            surface,
            arrow_color,
            (center_x, center_y - 8),
            (center_x, center_y + 8),
            3
        )
        
        # 矢印の先端（下向き三角形）
        pygame.draw.polygon(
            surface,
            arrow_color,
            [
                (center_x, center_y + 10),
                (center_x - 6, center_y + 2),
                (center_x + 6, center_y + 2)
            ]
        )