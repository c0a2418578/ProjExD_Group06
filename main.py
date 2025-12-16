# main.py
import pygame
import os
import sys

# パッケージ内のクラスをインポート
# main.pyと同じディレクトリにmap_engineがあることを想定
from map_engine.map_generator import MapGenerator

# MapGenerator内で定義されているデフォルトサイズを取得
DEFAULT_TILE_SIZE = 48 


def main():
    # 実行ファイルからの相対パスを基準にする
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Pygameの初期化
    pygame.init()
    screen = pygame.display.set_mode((1000, 700)) 
    pygame.display.set_caption("Modular Map Generator")
    clock = pygame.time.Clock()
    
    try:
        # MapGeneratorの初期化
        # タイルセット画像が見つからない場合はここでエラーが発生します
        map_gen = MapGenerator(width=50, height=50, tile_size=DEFAULT_TILE_SIZE) 
    except (FileNotFoundError, RuntimeError) as e:
        print(f"エラー: {e}")
        pygame.quit()
        sys.exit()

    
    # --- タイル選択の固定設定 (48x48タイル用) ---
    # TS0 = tileset1.png, TS1 = tileset2.png (あれば)
    # インデックス計算: tile_idx = y * (横のタイル数) + x 
    
    FLOOR_TILESET_IDX = 0 
    FLOOR_TILE_IDX = 0    
    
    WALL_TILESET_IDX = 1  
    WALL_TILE_IDX = 1     
    
    if map_gen.tile_selector.get_tileset_count() <= 1:
        WALL_TILESET_IDX = 0
        WALL_TILE_IDX = 1 
        
    map_gen.set_tiles(
        FLOOR_TILESET_IDX, FLOOR_TILE_IDX,
        WALL_TILESET_IDX, WALL_TILE_IDX
    )
    # --- 固定設定ここまで ---
    
    map_gen.generate()
    
    camera_x = 0
    camera_y = 0
    camera_speed = 10 
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    map_gen.generate()
                    camera_x = 0
                    camera_y = 0
        
        # カメラ移動 (矢印キー)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            camera_x -= camera_speed
        if keys[pygame.K_RIGHT]:
            camera_x += camera_speed
        if keys[pygame.K_UP]:
            camera_y -= camera_speed
        if keys[pygame.K_DOWN]:
            camera_y += camera_speed
        
        # カメラ位置の制限
        max_camera_x = max(0, map_gen.width * map_gen.tile_size - screen.get_width())
        max_camera_y = max(0, map_gen.height * map_gen.tile_size - screen.get_height())
        
        camera_x = max(0, min(camera_x, max_camera_x))
        camera_y = max(0, min(camera_y, max_camera_y))
        
        # 描画
        screen.fill((0, 0, 0))
        map_gen.draw(screen, camera_x, camera_y)
        
        # UI表示
        font = pygame.font.Font(None, 24)
        text1 = font.render("SPACE: Regenerate | Arrows: Move", True, (255, 255, 255))
        
        tile_info = (f"Floor: TS{map_gen.floor_tileset}[{map_gen.floor_tile}] | "
                     f"Wall: TS{map_gen.wall_tileset}[{map_gen.wall_tile}] (48x48 Tiles)")
        text2 = font.render(tile_info, True, (150, 200, 255))
        
        screen.blit(text1, (10, 10))
        screen.blit(text2, (10, 35))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()


if __name__ == "__main__":
    main()