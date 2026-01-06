import pygame
import os
import sys
import random
from typing import List, Tuple

# パッケージ内のクラスをインポート
from map_engine.map_generator import MapGenerator
from Trap import Trap
from Trapmanager import TrapManager
from Title import TitleScreen
from Player_parameter import Player_Parameter

from enemy import Enemy

# MapGenerator内で定義されているデフォルトサイズを取得
DEFAULT_TILE_SIZE = 48 
# 部屋ごとの敵数（ここを変更して1部屋あたりの敵数を制御）
ENEMIES_PER_ROOM = 2

def play_random_bgm(folder="bgm"):
    """bgmフォルダからランダムにMP3を選んで再生する"""
    try:
        if not os.path.exists(folder):
            print(f"警告: {folder} フォルダが見つかりません。")
            return

        files = [f for f in os.listdir(folder) if f.lower().endswith(".mp3")]
        if files:
            chosen_bgm = random.choice(files)
            full_path = os.path.join(folder, chosen_bgm)
            
            pygame.mixer.music.load(full_path)

            pygame.mixer.music.set_volume(0.1)  # 音量調整（0.0〜1.0）

            pygame.mixer.music.play(-1)  # -1 はループ再生
            print(f"BGM再生中: {chosen_bgm}")
        else:
            print("警告: bgmフォルダにMP3ファイルがありません。")
    except Exception as e:
        print(f"BGM再生エラー: {e}")

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    pygame.init()
    screen = pygame.display.set_mode((1000, 700)) 
    pygame.display.set_caption(".pngへの道")
    clock = pygame.time.Clock()
    Cat = Player_Parameter()
    
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

    enemies = Enemy.spawn(map_gen, ENEMIES_PER_ROOM)
    
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

    # 初期マップ生成のあたり
    play_random_bgm("bgm") # ここで最初のBGMを再生
    
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
                    enemies = Enemy.spawn(map_gen, ENEMIES_PER_ROOM)
                    
                    if hasattr(map_gen, 'stairs_pos') and map_gen.stairs_pos:
                        stairs = Stairs(map_gen.stairs_pos[0], map_gen.stairs_pos[1], DEFAULT_TILE_SIZE)
                    else:
                        last_room = map_gen.rooms[-1]
                        stairs = Stairs(last_room.centerx, last_room.centery, DEFAULT_TILE_SIZE)
                    
                    current_floor = 1
                    camera_x = camera_y = 0
                    player.tile_x = map_gen.rooms[0].centerx
                    player.tile_y = map_gen.rooms[0].centery
                elif event.key == pygame.K_t:
                    show_traps = not show_traps
        
        # --- 1. プレイヤーの移動処理 ---
        keys = pygame.key.get_pressed()
        prev_px, prev_py = player.tile_x, player.tile_y
        player.handle_input(keys, map_gen)

        # --- 2. プレイヤーが移動した瞬間の判定 ---
        if (player.tile_x, player.tile_y) != (prev_px, prev_py):
            # プレイヤーが動いたので、移動先の敵をチェック
            for e in enemies:
                if hasattr(e, 'hp') and e.hp > 0:
                    etx, ety = int(e.x) // e.tile_size, int(e.y) // e.tile_size
                    if player.tile_x == etx and player.tile_y == ety:
                        Cat.Trap_dmg(5)
                        print(f"移動先に敵がいた！ 残りHP: {Cat.current_hp}")

            # プレイヤーが1タイル移動したので、敵も1マス進める
            occupied = set()
            for ee in enemies:
                occupied.add((int(ee.x) // ee.tile_size, int(ee.y) // ee.tile_size))
            occupied.add((player.tile_x, player.tile_y))

            for e in enemies:
                cur = (int(e.x) // e.tile_size, int(e.y) // e.tile_size)
                if cur in occupied: occupied.remove(cur)
                
                try:
                    e.move_towards_player(player.tile_x, player.tile_y, map_gen, occupied=occupied)
                except:
                    pass

                new_pos = (int(e.x) // e.tile_size, int(e.y) // e.tile_size)
                occupied.add(new_pos)

                # --- 3. 敵が移動してプレイヤーに重なった時の判定 ---
                if hasattr(e, 'hp') and e.hp > 0:
                    if new_pos == (player.tile_x, player.tile_y):
                        Cat.Trap_dmg(5)
                        print(f"敵が突っ込んできた！ 残りHP: {Cat.current_hp}")

        # --- 4. 階段・トラップ判定 ---
        player_rect = player.get_rect()
        
        # トラップ判定
        trap_dmg = trap_manager.check_collisions(player_rect)
        if trap_dmg > 0:
            Cat.Trap_dmg(trap_dmg)
            print(f"トラップ! 残りHP: {Cat.current_hp}")

        # ゲームオーバー確認
        if Cat.current_hp <= 0:
            print("GAME OVER")
            running = False

        # --- 4. 階段・トラップ判定 ---
        if stairs.check_collision(player_rect):
            current_floor += 1
            print(f"階段を下りた！ 次は Floor {current_floor}")

            # --- 階層が4になったらクリア画面へ ---
            if current_floor >= 4:
                # 【ここが重要：この2行を追加して変数を定義する】
                folder = "cat_model"
                extensions = (".png", ".jpg", ".jpeg")
                files = [f for f in os.listdir(folder) if f.lower().endswith(extensions)]
                
                # --- 【ランダム要素の決定】 ---
                # 1. 画像をランダムに選ぶ
                if files:  # これで NameError が消えます
                    chosen_file = random.choice(files)
                    clear_image = pygame.image.load(os.path.join(folder, chosen_file)).convert_alpha()
                    img_size = random.randint(200, 450)
                    clear_image = pygame.transform.scale(clear_image, (img_size, img_size))
                else:
                    chosen_file = "No Image"
                    clear_image = None

                # 2. 背景色をランダムに選ぶ
                bg_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                
                # 3. メッセージをランダムに選ぶ
                msgs = ["GAME CLEAR!", "YOU WIN!", "CONGRATULATIONS!", "NYA-N!", "HAPPY END"]
                chosen_msg = random.choice(msgs)
                
                # 4. 文字の色を背景に合わせてランダムに（または白固定で見やすく）
                text_color = (255, 255, 255) if sum(bg_color) < 400 else (0, 0, 0)
                
                # 5. 表示位置を少しランダムにずらす
                offset_y = random.randint(-50, 50)

                show_clear_screen = True
                while show_clear_screen:
                    screen.fill(bg_color) # ランダム背景
                    
                    font = pygame.font.Font(None, 80)
                    sub_font = pygame.font.Font(None, 40)
                    
                    msg_surf = font.render(chosen_msg, True, text_color)
                    img_info = sub_font.render(f"Result: {chosen_file}", True, text_color)
                    exit_txt = sub_font.render("Press SPACE to Exit", True, text_color)
                    
                    # ランダムな位置要素を反映して描画
                    screen.blit(msg_surf, (500 - msg_surf.get_width()//2, 450 + offset_y))
                    screen.blit(img_info, (500 - img_info.get_width()//2, 530 + offset_y))
                    screen.blit(exit_txt, (500 - exit_txt.get_width()//2, 620))
                    
                    if clear_image:
                        # 画像の位置も少しだけランダムに
                        screen.blit(clear_image, (500 - clear_image.get_width()//2, 100 + offset_y))
                    
                    pygame.display.flip()
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit(); sys.exit()
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_SPACE:
                                show_clear_screen = False
                                running = False
                continue


            # --- 【重要】次の階層へ進むためのリセット処理 ---
            # これを行うことで、プレイヤーが階段から離れるため、数字の連打を防げます
            play_random_bgm("bgm")  # BGM切り替え
            
            map_gen.generate() # 新しいマップを作る
            trap_manager.generate_traps(map_gen, trap_count=30)
            enemies = Enemy.spawn(map_gen, ENEMIES_PER_ROOM)
            
            # 階段を新しいマップのどこかへ再配置
            if hasattr(map_gen, 'stairs_pos') and map_gen.stairs_pos:
                stairs = Stairs(map_gen.stairs_pos[0], map_gen.stairs_pos[1], DEFAULT_TILE_SIZE)
            else:
                stairs = Stairs(map_gen.rooms[-1].centerx, map_gen.rooms[-1].centery, DEFAULT_TILE_SIZE)
            
            # 【ここが重要】プレイヤーを新しい部屋の初期位置へワープさせる
            player.tile_x = map_gen.rooms[0].centerx
            player.tile_y = map_gen.rooms[0].centery
            
            # 念のためカメラ位置も更新
            camera_x, camera_y = player.get_camera_pos(800, 600, map_gen.width * map_gen.tile_size, map_gen.height * map_gen.tile_size)

        # --- 5. 描画処理 ---
        camera_x, camera_y = player.get_camera_pos(800, 600, map_gen.width * map_gen.tile_size, map_gen.height * map_gen.tile_size)
        screen.fill((0, 0, 0))
        map_gen.draw(screen, camera_x, camera_y)
        for e in enemies: e.draw(screen, camera_x, camera_y)
        trap_manager.draw(screen, camera_x, camera_y, show_traps)
        stairs.draw(screen, camera_x, camera_y)
        player.draw(screen, camera_x, camera_y)
        
        # UI描画
        font = pygame.font.Font(None, 24)
        screen.blit(font.render(f"Floor: {current_floor}  HP: {Cat.current_hp}/{Cat.max_hp}", True, (255, 255, 255)), (10, 10))
        
        pygame.display.flip()
        trap_manager.update(dt)

    pygame.quit()

if __name__ == "__main__":
    main()