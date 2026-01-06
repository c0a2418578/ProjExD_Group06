# map_engine/map_generator.py
import pygame
import random
import os
from typing import List, Tuple
from .tile_selector import TileSelector, DEFAULT_TILE_SIZE

class MapGenerator:
    def __init__(self, width=50, height=50, tile_size=DEFAULT_TILE_SIZE, 
                 floor_tileset=0, floor_tile=0, wall_tileset=0, wall_tile=1):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.room_count = 5
        self.room_min_size = 6
        self.room_max_size = 15
        
        self.tilemap = [[0 for _ in range(height)] for _ in range(width)]
        self.rooms: List[pygame.Rect] = []
        
        # タイルセレクター初期化のためのパス確認
        possible_paths = [
            ["assets/tileset1.png", "assets/tileset2.png"],
            ["Assets/tileset1.png", "Assets/tileset2.png"],
            ["tileset1.png", "tileset2.png"],
        ]
        
        tileset_paths = None
        for paths in possible_paths:
            # main.pyからの相対パスを想定してチェック
            if os.path.exists(paths[0]): 
                tileset_paths = [p for p in paths if os.path.exists(p)]
                break
        
        if not tileset_paths:
            # 実行ディレクトリが見つからない場合はエラー
            raise FileNotFoundError(
                "タイルセット画像が見つかりません。assets/tileset1.png を配置してください。"
            )
        
        self.tile_selector = TileSelector(tileset_paths, tile_size=tile_size) 
        
        self.floor_tileset = floor_tileset
        self.floor_tile = floor_tile
        self.wall_tileset = wall_tileset
        self.wall_tile = wall_tile
    
    def set_tiles(self, floor_tileset, floor_tile, wall_tileset, wall_tile):
        """使用するタイルを設定する"""
        self.floor_tileset = floor_tileset
        self.floor_tile = floor_tile
        self.wall_tileset = wall_tileset
        self.wall_tile = wall_tile
    
    def generate(self):
        """マップを生成"""
        self.rooms.clear()
        
        for x in range(self.width):
            for y in range(self.height):
                self.tilemap[x][y] = 0
        
        for i in range(self.room_count):
            w = random.randint(self.room_min_size, self.room_max_size)
            h = random.randint(self.room_min_size, self.room_max_size)
            x = random.randint(1, self.width - w - 1)
            y = random.randint(1, self.height - h - 1)
            
            room = pygame.Rect(x, y, w, h)
            self.rooms.append(room)
            self.create_room(room)
            
            if i > 0:
                prev_center = self.rooms[i - 1].center
                new_center = room.center
                self.create_corridor(prev_center, new_center)
    
    def create_room(self, room: pygame.Rect):
        """部屋の床を作成"""
        for x in range(room.left, room.right):
            for y in range(room.top, room.bottom):
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.tilemap[x][y] = 1
    
    def create_corridor(self, start: Tuple[int, int], end: Tuple[int, int]):
        """L字型の通路を作成"""
        x1, y1 = start
        x2, y2 = end
        
        step_x = 1 if x1 < x2 else -1
        x = x1
        while x != x2:
            if 0 <= x < self.width and 0 <= y1 < self.height:
                self.tilemap[x][y1] = 1
            x += step_x
        
        step_y = 1 if y1 < y2 else -1
        y = y1
        while y != y2:
            if 0 <= x2 < self.width and 0 <= y < self.height:
                self.tilemap[x2][y] = 1
            y += step_y
    
    def draw(self, surface: pygame.Surface, camera_x=0, camera_y=0):
        """マップを描画 (カメラオフセット対応) - 垂直通路が壁に隠れるバグを修正"""
        screen_w, screen_h = surface.get_size()
        
        # 描画範囲を計算
        start_x = max(0, camera_x // self.tile_size)
        end_x = min(self.width, (camera_x + screen_w) // self.tile_size + 1)
        start_y = max(0, camera_y // self.tile_size)
        end_y = min(self.height, (camera_y + screen_h) // self.tile_size + 1)
        
        floor_tile = self.tile_selector.get_tile(self.floor_tileset, self.floor_tile)
        wall_tile = self.tile_selector.get_tile(self.wall_tileset, self.wall_tile)
        
        # まず床を描画
        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                if self.tilemap[x][y] == 1:
                    screen_x = x * self.tile_size - camera_x
                    screen_y = y * self.tile_size - camera_y
                    
                    # 床の描画
                    if floor_tile:
                        surface.blit(floor_tile, (screen_x, screen_y))
                    else:
                        pygame.draw.rect(surface, (200, 200, 200), 
                                         (screen_x, screen_y, self.tile_size, self.tile_size))
        
        # 次に壁を描画 (床の上に立つ壁のみ)
        # 床の上(y-1)の壁(0)は、Isometricな表現でない限り、
        # 床(1)の上に描画されるべきです。
        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                
                # セル(x, y) が壁(0)で、その下(y+1)が床(1)の場合、
                # セル(x, y) を床の上に立つ壁として描画します。
                # y-1 (奥側) の床の有無はここでは無視します。
                
                # **重要**: y座標のループの順序は、壁が手前の床に描画されるため、
                # この単純な描画では問題になりません。
                
                if self.tilemap[x][y] == 0:
                    # その下のセルが床であるかどうかをチェック
                    if y < self.height - 1 and self.tilemap[x][y+1] == 1:
                        screen_x = x * self.tile_size - camera_x
                        screen_y = y * self.tile_size - camera_y

                        # 壁の描画
                        if wall_tile:
                            surface.blit(wall_tile, (screen_x, screen_y))
                        else:
                            # デフォルト矩形
                            pygame.draw.rect(surface, (80, 60, 40), 
                                             (screen_x, screen_y, self.tile_size, self.tile_size))