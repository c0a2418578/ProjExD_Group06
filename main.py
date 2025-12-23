import pygame
import os
import random
import sys
import random
from typing import List, Tuple

from map_engine.map_generator import MapGenerator
from Trap import Trap
from Trapmanager import TrapManager
from Stairs import Stairs

from enemy import Enemy

# MapGenerator内で定義されているデフォルトサイズを取得
DEFAULT_TILE_SIZE = 48 
# 部屋ごとの敵数（ここを変更して1部屋あたりの敵数を制御）
ENEMIES_PER_ROOM = 2


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    pygame.init()
    screen = pygame.display.set_mode((1000, 700)) 
    pygame.display.set_caption("Dungeon Crawler with Stairs")
    clock = pygame.time.Clock()
    
    try:
        map_gen = MapGenerator(width=50, height=50, tile_size=DEFAULT_TILE_SIZE) 
    except (FileNotFoundError, RuntimeError) as e:
        print(f"エラー: {e}")
        pygame.quit()
        sys.exit()

    # タイル設定
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
    
    # 初期マップ生成
    map_gen.generate()

    enemies: List[Enemy] = []
    for room in map_gen.rooms:
        # 各部屋に対して ENEMIES_PER_ROOM 体の敵を配置
        for _ in range(ENEMIES_PER_ROOM):
            # 部屋内のタイル座標をランダムに選び、ピクセル座標に変換
            tx = random.randint(max(room.left + 1, 0), max(room.right - 2, room.left))
            ty = random.randint(max(room.top + 1, 0), max(room.bottom - 2, room.top))
            ex = tx * map_gen.tile_size
            ey = ty * map_gen.tile_size
            # 敵画像は未指定（フォールバック描画）。速度は適度に設定
            enemies.append(
                Enemy(
                    ex,
                    ey,
                    hp=20,
                    speed=40.0,
                    image_path="Assets/enemy_kyuri.png",
                    tile_size=map_gen.tile_size,
                )
            )
    
    # トラップマネージャーの初期化
    trap_manager = TrapManager(tile_size=DEFAULT_TILE_SIZE)
    trap_manager.generate_traps(map_gen, trap_count=30)

    # 階段の生成（map_generatorに階段位置がない場合は最後の部屋の中央に配置）
    if hasattr(map_gen, 'stairs_pos') and map_gen.stairs_pos:
        stairs = Stairs(map_gen.stairs_pos[0], map_gen.stairs_pos[1], DEFAULT_TILE_SIZE)
    else:
        # 階段位置がない場合は最後の部屋に配置
        last_room = map_gen.rooms[-1]
        stairs = Stairs(last_room.centerx, last_room.centery, DEFAULT_TILE_SIZE)
    
    # 現在の階層
    current_floor = 1

    # プレイヤー生成
    from move import Player
    player = Player(
        map_gen.rooms[0].centerx,
        map_gen.rooms[0].centery,
        tile_size=48
    )
    
    camera_x = 0
    camera_y = 0
    
    # デバッグモード（罠の可視化）
    show_traps = False

    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # 秒単位のデルタタイム

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # マップ再生成
                    map_gen.generate()
                    trap_manager.generate_traps(map_gen, trap_count=30)
                    
                    # 階段を再生成
                    if hasattr(map_gen, 'stairs_pos') and map_gen.stairs_pos:
                        stairs = Stairs(map_gen.stairs_pos[0], map_gen.stairs_pos[1], DEFAULT_TILE_SIZE)
                    else:
                        last_room = map_gen.rooms[-1]
                        stairs = Stairs(last_room.centerx, last_room.centery, DEFAULT_TILE_SIZE)
                    
                    current_floor = 1
                    camera_x = 0
                    camera_y = 0
                    player.tile_x = map_gen.rooms[0].centerx
                    player.tile_y = map_gen.rooms[0].centery
                elif event.key == pygame.K_t:
                    # Tキーで罠の可視化切り替え
                    show_traps = not show_traps
                    
        
        # プレイヤー移動（WASDキー）
        keys = pygame.key.get_pressed()
        prev_px, prev_py = player.tile_x, player.tile_y
        player.handle_input(keys, map_gen)

        # プレイヤーが1タイル移動したら敵を1マス進める
        if (player.tile_x, player.tile_y) != (prev_px, prev_py):
            # 敵同士およびプレイヤーと重ならないように順次移動させる
            # 初期 occupied は全ての敵のタイル座標とプレイヤーのタイル
            occupied = set()
            for ee in enemies:
                etx = int(ee.x) // ee.tile_size
                ety = int(ee.y) // ee.tile_size
                occupied.add((etx, ety))
            occupied.add((player.tile_x, player.tile_y))

            for e in enemies:
                # 自分の現在位置を一旦開放して移動を試みる
                cur = (int(e.x) // e.tile_size, int(e.y) // e.tile_size)
                if cur in occupied:
                    occupied.remove(cur)

                try:
                    moved = e.move_towards_player(player.tile_x, player.tile_y, map_gen, occupied=occupied)
                except Exception:
                    moved = False

                # 移動後の位置を占有セットに追加
                new_pos = (int(e.x) // e.tile_size, int(e.y) // e.tile_size)
                occupied.add(new_pos)
        
        # 階段との衝突判定
        player_rect = pygame.Rect(
            player.tile_x * player.tile_size,
            player.tile_y * player.tile_size,
            player.tile_size,
            player.tile_size
        )
        
        if stairs.check_collision(player_rect):
            # 次の階層へ移動
            current_floor += 1
            map_gen.generate()
            trap_manager.generate_traps(map_gen, trap_count=30)
            
            # 階段を再生成
            if hasattr(map_gen, 'stairs_pos') and map_gen.stairs_pos:
                stairs = Stairs(map_gen.stairs_pos[0], map_gen.stairs_pos[1], DEFAULT_TILE_SIZE)
            else:
                last_room = map_gen.rooms[-1]
                stairs = Stairs(last_room.centerx, last_room.centery, DEFAULT_TILE_SIZE)
            
            # プレイヤーを新しいマップの最初の部屋に配置
            player.tile_x = map_gen.rooms[0].centerx
            player.tile_y = map_gen.rooms[0].centery
        
        # カメラをプレイヤーに追従
        camera_x, camera_y = player.get_camera_pos(
            800, 600,
            map_gen.width * map_gen.tile_size,
            map_gen.height * map_gen.tile_size
        )

        # トラップの更新
        trap_manager.update(dt)
        
        # 描画
        screen.fill((0, 0, 0))
        map_gen.draw(screen, camera_x, camera_y)

        for e in enemies:
            e.draw(screen, camera_x, camera_y)

        trap_manager.draw(screen, camera_x, camera_y, show_traps)
        stairs.draw(screen, camera_x, camera_y)
        
        player.draw(screen, camera_x, camera_y)
        
        # UI表示
        font = pygame.font.Font(None, 36)
        floor_text = font.render(f"Floor: {current_floor}", True, (255, 255, 255))
        screen.blit(floor_text, (10, 10))
        
        # その他の情報
        small_font = pygame.font.Font(None, 24)
        text1 = small_font.render("SPACE: Regenerate | WASD: Move", True, (255, 255, 255))
        
        tile_info = (f"Floor: TS{map_gen.floor_tileset}[{map_gen.floor_tile}] | "
                f"Wall: TS{map_gen.wall_tileset}[{map_gen.wall_tile}]")
        text2 = small_font.render(tile_info, True, (150, 200, 255))
        
        trap_status = "Visible" if show_traps else "Invisible"
        trap_text = small_font.render(f"Traps: {len(trap_manager.traps)} ({trap_status})", True, (255, 255, 100))

        screen.blit(text1, (10, 50))
        screen.blit(text2, (10, 75))
        screen.blit(trap_text, (10, 100))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()


if __name__ == "__main__":
    main()