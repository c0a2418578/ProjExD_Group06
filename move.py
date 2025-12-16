import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from map_generator import MapGenerator


class Player:
    def __init__(self, x: int, y: int, tile_size: int = 48):
        super().__init__()
        """
        プレイヤークラス
        
        Args:
            x: 初期X座標（タイル単位）
            y: 初期Y座標（タイル単位）
            tile_size: タイルサイズ（ピクセル）
        """
        self.tile_x = x
        self.tile_y = y
        self.tile_size = tile_size
        self.speed = tile_size  # 1タイル分の移動速度
        
        # 向き（0: 右, 1: 左）
        self.direction = 0
        
        # 画像の読み込み
        try:
            self.image_right = pygame.image.load("cat_model/right.png").convert_alpha()
            self.image_left = pygame.image.load("cat_model/0.jpg").convert_alpha()
            
            # タイルサイズにリサイズ
            self.image_right = pygame.transform.scale(self.image_right, (tile_size, tile_size))
            self.image_left = pygame.transform.scale(self.image_left, (tile_size, tile_size))
            
            self.current_image = self.image_right
        except pygame.error as e:
            print(f"プレイヤー画像の読み込みエラー: {e}")
            print("Assets/player_right.png と Assets/player_left.png を用意してください")
            # フォールバック: 円で描画
            self.image_right = None
            self.image_left = None
            self.current_image = None
    
    def get_pixel_pos(self):
        """ピクセル座標を取得"""
        return self.tile_x * self.tile_size, self.tile_y * self.tile_size
    
    def can_move_to(self, x: int, y: int, map_gen: 'MapGenerator') -> bool:
        """
        指定された座標に移動可能かチェック
        
        Args:
            x: 移動先X座標（タイル単位）
            y: 移動先Y座標（タイル単位）
            map_gen: マップジェネレーター
            
        Returns:
            移動可能ならTrue
        """
        # マップ範囲外チェック
        if x < 0 or x >= map_gen.width or y < 0 or y >= map_gen.height:
            return False
        
        # 壁チェック（0=壁, 1=床）
        if map_gen.tilemap[x][y] == 0:
            return False
        
        return True
    
    def move(self, dx: int, dy: int, map_gen: 'MapGenerator'):
        """
        プレイヤーを移動
        
        Args:
            dx: X方向の移動量（タイル単位）
            dy: Y方向の移動量（タイル単位）
            map_gen: マップジェネレーター
        """
        new_x = self.tile_x + dx
        new_y = self.tile_y + dy
        
        # 移動可能かチェック
        if self.can_move_to(new_x, new_y, map_gen):
            self.tile_x = new_x
            self.tile_y = new_y
            
            # 向きの更新
            if dx > 0:
                self.direction = 0  # 右
                if self.image_right:
                    self.current_image = self.image_right
            elif dx < 0:
                self.direction = 1  # 左
                if self.image_left:
                    self.current_image = self.image_left
    
    def handle_input(self, keys, map_gen: 'MapGenerator'):
        """
        キー入力を処理
        
        Args:
            keys: pygame.key.get_pressed()の結果
            map_gen: マップジェネレーター
        """
        moved = False
        
        if keys[pygame.K_w] and not moved:
            self.move(0, -1, map_gen)
            moved = True
        if keys[pygame.K_s] and not moved:
            self.move(0, 1, map_gen)
            moved = True
        if keys[pygame.K_a] and not moved:
            self.move(-1, 0, map_gen)
            moved = True
        if keys[pygame.K_d] and not moved:
            self.move(1, 0, map_gen)
            moved = True
    
    def get_camera_pos(self, screen_width: int, screen_height: int, map_width: int, map_height: int):
        """
        プレイヤーを中心にしたカメラ位置を計算
        
        Args:
            screen_width: 画面幅
            screen_height: 画面高さ
            map_width: マップ幅（ピクセル）
            map_height: マップ高さ（ピクセル）
            
        Returns:
            (camera_x, camera_y): カメラ座標
        """
        pixel_x, pixel_y = self.get_pixel_pos()
        
        # プレイヤーを画面中央に配置
        camera_x = pixel_x - screen_width // 2 + self.tile_size // 2
        camera_y = pixel_y - screen_height // 2 + self.tile_size // 2
        
        # カメラ位置を制限
        camera_x = max(0, min(camera_x, map_width - screen_width))
        camera_y = max(0, min(camera_y, map_height - screen_height))
        
        return camera_x, camera_y
    
    def draw(self, surface: pygame.Surface, camera_x: int = 0, camera_y: int = 0):
        """
        プレイヤーを描画
        
        Args:
            surface: 描画先サーフェス
            camera_x: カメラのX座標（ピクセル）
            camera_y: カメラのY座標（ピクセル）
        """
        pixel_x, pixel_y = self.get_pixel_pos()
        screen_x = pixel_x - camera_x
        screen_y = pixel_y - camera_y
        
        if self.current_image:
            surface.blit(self.current_image, (screen_x, screen_y))
        else:
            # フォールバック: 青い円で描画
            center_x = screen_x + self.tile_size // 2
            center_y = screen_y + self.tile_size // 2
            pygame.draw.circle(surface, (0, 100, 255), (center_x, center_y), self.tile_size // 2)