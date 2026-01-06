# map_engine/tile_selector.py
import pygame
import os
from typing import List

DEFAULT_TILE_SIZE = 48

class TileSelector:
    def __init__(self, tileset_images: List[str], tile_size=DEFAULT_TILE_SIZE): 
        """
        タイルセット画像からタイルを読み込み、1次元リストに格納する。
        """
        self.tile_size = tile_size
        self.tileset_images = []  
        self.tileset_names = []   
        
        for img_idx, img_path in enumerate(tileset_images):
            try:
                # パスが存在しない場合に備えて、ロード時にエラーをチェック
                if not os.path.exists(img_path):
                     print(f"警告: ファイルが見つかりません - {img_path}")
                     continue

                tileset = pygame.image.load(img_path).convert_alpha()
                img_width = tileset.get_width()
                img_height = tileset.get_height()
                
                width = img_width // tile_size
                height = img_height // tile_size
                
                tiles = []
                for y in range(height):
                    for x in range(width):
                        tile_surface = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
                        tile_surface.blit(tileset, (0, 0), 
                                         (x * tile_size, y * tile_size, tile_size, tile_size))
                        tiles.append(tile_surface)
                        
                self.tileset_images.append(tiles)
                self.tileset_names.append(os.path.basename(img_path))
                print(f"タイルセット読み込み成功 (TS Index {img_idx}): {img_path} ({len(tiles)} tiles)")
            except pygame.error as e:
                # Pygameによる画像ロードエラーが発生した場合
                raise RuntimeError(f"タイルセット {img_path} のロード中にエラーが発生しました: {e}")
    
    def get_tile(self, tileset_idx: int, tile_idx: int):
        """指定されたタイルセット（ファイル）とインデックスのタイルを取得"""
        if 0 <= tileset_idx < len(self.tileset_images):
            tiles = self.tileset_images[tileset_idx]
            if 0 <= tile_idx < len(tiles):
                return tiles[tile_idx]
        return None
    
    def get_tileset_count(self):
        """読み込んだタイルセット（ファイル）の数を取得"""
        return len(self.tileset_images)