import pygame
import os
import sys

# パッケージ内のクラスをインポート
from map_engine.map_generator import MapGenerator
from Trap import Trap
from Trapmanager import TrapManager
from Title import TitleScreen

DEFAULT_TILE_SIZE = 48 


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    pygame.init()
    screen = pygame.display.set_mode((1000, 700)) 
    pygame.display.set_caption(".pngへの道")
    clock = pygame.time.Clock()
    
    # タイトル画面を表示
    title_screen = TitleScreen(screen_width=1000, screen_height=700)
    title_screen.run(screen)
    
    try:
        map_gen = MapGenerator(width=50, height=50, tile_size=DEFAULT_TILE_SIZE) 
    except (FileNotFoundError, RuntimeError) as e:
        print(f"エラー: {e}")
        pygame.quit()
        sys.exit()

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
    
    trap_manager = TrapManager(tile_size=DEFAULT_TILE_SIZE)
    trap_manager.generate_traps(map_gen, trap_count=30)

    camera_x = 0
    camera_y = 0

    from Stairs import Stairs  # Stairsクラスのインポート
    if hasattr(map_gen, 'stairs_pos') and map_gen.stairs_pos:
        stairs = Stairs(map_gen.stairs_pos[0], map_gen.stairs_pos[1], DEFAULT_TILE_SIZE)
    else:
        last_room = map_gen.rooms[-1]
        stairs = Stairs(last_room.centerx, last_room.centery, DEFAULT_TILE_SIZE)
    
    from move import Player
    player = Player(
        map_gen.rooms[0].centerx,
        map_gen.rooms[0].centery,
        tile_size=48
    )
    
    camera_speed = 10 
    show_traps = False
    current_floor = 1
    
    running = True
    while running:
        dt = clock.tick(60) / 16.0

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
                    show_traps = not show_traps
        
        keys = pygame.key.get_pressed()
        player.handle_input(keys, map_gen)
        
        camera_x, camera_y = player.get_camera_pos(
            800, 600,
            map_gen.width * map_gen.tile_size,
            map_gen.height * map_gen.tile_size
        )

        # トラップとの衝突判定
        damage = trap_manager.check_collisions(player.get_rect())
        if damage > 0:
            print(f"トラップ発動! ダメージ: {damage}")

        trap_manager.update(dt)
        if player.tile_x == stairs.tile_x and player.tile_y == stairs.tile_y:
            print(f"階段に到達! 次の階層へ（Floor {current_floor + 1}）")
            current_floor += 1
            
            # 新しいマップを生成
            map_gen.generate()
            trap_manager.generate_traps(map_gen, trap_count=30)
            
            # 新しい階段を配置
            if hasattr(map_gen, 'stairs_pos') and map_gen.stairs_pos:
                stairs = Stairs(map_gen.stairs_pos[0], map_gen.stairs_pos[1], DEFAULT_TILE_SIZE)
            else:
                last_room = map_gen.rooms[-1]
                stairs = Stairs(last_room.centerx, last_room.centery, DEFAULT_TILE_SIZE)
            
            # プレイヤーを最初の部屋に配置
            player.tile_x = map_gen.rooms[0].centerx
            player.tile_y = map_gen.rooms[0].centery
        
        screen.fill((0, 0, 0))
        map_gen.draw(screen, camera_x, camera_y)
        trap_manager.draw(screen, camera_x, camera_y, show_traps)
        stairs.draw(screen, camera_x, camera_y)
        
        player.draw(screen, camera_x, camera_y)
        
        font = pygame.font.Font(None, 24)
        small_font = pygame.font.Font(None, 20)
        text1 = font.render("SPACE: Regenerate | T: Toggle Traps", True, (255, 255, 255))
        
        tile_info = (f"Floor: TS{map_gen.floor_tileset}[{map_gen.floor_tile}] | "
                f"Wall: TS{map_gen.wall_tileset}[{map_gen.wall_tile}]")
        text2 = small_font.render(tile_info, True, (150, 200, 255))
        
        trap_status = "Visible" if show_traps else "Invisible"
        trap_text = small_font.render(f"Traps: {len(trap_manager.traps)} ({trap_status})", True, (255, 255, 100))

        floor_text = font.render(f"Floor: {current_floor}", True, (255, 255, 255))

        screen.blit(text1, (10, 50))
        screen.blit(text2, (10, 75))
        screen.blit(trap_text, (10, 100))
        screen.blit(floor_text, (10, 10))  
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()


if __name__ == "__main__":
    main()