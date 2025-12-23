import pygame
import random
import math
import sys


class ChaosParticle:
    """カオスな背景パーティクル"""
    def __init__(self, screen_width, screen_height):
        self.x = random.randint(0, screen_width)
        self.y = random.randint(0, screen_height)
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.size = random.randint(2, 8)
        self.color = [random.randint(0, 255) for _ in range(3)]
        self.life = random.randint(60, 180)
        self.max_life = self.life
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-5, 5)
        
    def update(self, screen_width, screen_height):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.rotation += self.rotation_speed
        
        # 画面外に出たら反対側から出現
        if self.x < 0: self.x = screen_width
        if self.x > screen_width: self.x = 0
        if self.y < 0: self.y = screen_height
        if self.y > screen_height: self.y = 0
        
        # 色を変化させる
        for i in range(3):
            self.color[i] = (self.color[i] + random.randint(-5, 5)) % 256
            
    def draw(self, surface):
        alpha = int(255 * (self.life / self.max_life))
        color = self.color + [alpha]
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, color, (self.size, self.size), self.size)
        surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))


class TitleScreen:
    """カオスなタイトル画面クラス"""
    def __init__(self, screen_width=1000, screen_height=700):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # パーティクル生成
        self.particles = [ChaosParticle(screen_width, screen_height) for _ in range(100)]
        
        # 日本語フォント設定
        try:
            # Windowsの場合
            self.title_font = pygame.font.SysFont('msgothic', 100)  # MSゴシック
            self.subtitle_font = pygame.font.SysFont('msgothic', 30)
            self.small_font = pygame.font.SysFont('msgothic', 25)
        except:
            try:
                # カスタムフォントファイルを使用する場合
                self.title_font = pygame.font.Font('fonts/NotoSansJP-Bold.ttf', 100)
                self.subtitle_font = pygame.font.Font('fonts/NotoSansJP-Regular.ttf', 35)
                self.small_font = pygame.font.Font('fonts/NotoSansJP-Regular.ttf', 25)
            except:
                # フォールバック: デフォルトフォント
                print("日本語フォントが見つかりません。デフォルトフォントを使用します。")
                self.title_font = pygame.font.Font(None, 120)
                self.subtitle_font = pygame.font.Font(None, 40)
                self.small_font = pygame.font.Font(None, 30)
        
        # テキスト
        self.title_text = ".pngへの道"
        self.subtitle_text = "jpegから憧れの.pngに…"
        self.start_text = "SPACEキーでスタート"
        self.warning_texts = [
            "警告: Warning!",
            "危険: Dangerous!",
            "注意: Attention!"
        ]
        
        # アニメーション用変数
        self.time = 0
        self.flash_timer = 0
        
    def update(self, dt):
        """タイトル画面を更新"""
        self.time += dt / 1000.0
        self.flash_timer += dt
        
        # パーティクル更新
        for particle in self.particles:
            particle.update(self.screen_width, self.screen_height)
            if particle.life <= 0:
                self.particles.remove(particle)
                self.particles.append(ChaosParticle(self.screen_width, self.screen_height))
    
    def draw(self, surface):
        """タイトル画面を描画"""
        # 背景を暗くする
        surface.fill((10, 5, 15))
        
        # パーティクル描画
        for particle in self.particles:
            particle.draw(surface)
        
        # タイトル描画（グリッチエフェクト付き）
        for i in range(3):
            offset_x = random.randint(-5, 5) if random.random() < 0.1 else 0
            offset_y = random.randint(-5, 5) if random.random() < 0.1 else 0
            
            # RGB分離エフェクト
            colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
            color = colors[i]
            
            title_surface = self.title_font.render(self.title_text, True, color)
            title_rect = title_surface.get_rect(center=(self.screen_width // 2 + offset_x + (i-1)*3, 200 + offset_y))
            surface.blit(title_surface, title_rect)
        
        # 波打つサブタイトル
        subtitle_y = 320 + math.sin(self.time * 3) * 10
        for i, char in enumerate(self.subtitle_text):
            char_offset = math.sin(self.time * 2 + i * 0.3) * 15
            char_color = (
                int(128 + 127 * math.sin(self.time * 2 + i * 0.5)),
                int(128 + 127 * math.sin(self.time * 2 + i * 0.5 + 2)),
                int(128 + 127 * math.sin(self.time * 2 + i * 0.5 + 4))
            )
            char_surface = self.subtitle_font.render(char, True, char_color)
            char_rect = char_surface.get_rect(center=(350 + i * 20, subtitle_y + char_offset))
            surface.blit(char_surface, char_rect)
        
        # 点滅するスタートテキスト
        if (self.flash_timer // 500) % 2 == 0:
            start_surface = self.small_font.render(self.start_text, True, (255, 255, 100))
            start_rect = start_surface.get_rect(center=(self.screen_width // 2, 500))
            surface.blit(start_surface, start_rect)
        
        # ランダムなノイズライン
        if random.random() < 0.3:
            y = random.randint(0, self.screen_height)
            pygame.draw.line(surface, (255, 255, 255, 100), (0, y), (self.screen_width, y), 2)
        
        # 警告テキスト
        warning_index = int(self.time * 2) % len(self.warning_texts)
        warning_surface = self.small_font.render(self.warning_texts[warning_index], True, (255, 50, 50))
        warning_rect = warning_surface.get_rect(center=(self.screen_width // 2, 600))
        surface.blit(warning_surface, warning_rect)
    
    def run(self, screen):
        """タイトル画面を実行（Spaceが押されるまでループ）"""
        clock = pygame.time.Clock()
        
        waiting = True
        while waiting:
            dt = clock.tick(60)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        waiting = False
            
            self.update(dt)
            self.draw(screen)
            pygame.display.flip()