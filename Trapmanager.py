import pygame
import random
import math
from typing import List, Tuple
from map_engine.map_generator import MapGenerator
from Trap import Trap


class TrapEffectParticle:
    """罠エフェクト用のパーティクル"""
    def __init__(self, x, y, trap_type):
        self.x = x
        self.y = y
        
        # 罠の種類によって色とエフェクトを変更
        if trap_type == "spike":
            self.color = (255, 0, 0)  # 赤
            self.vx = random.uniform(-5, 5)
            self.vy = random.uniform(-8, -2)
            self.gravity = 0.3
        elif trap_type == "fire":
            self.color = (255, random.randint(100, 200), 0)  # オレンジ
            self.vx = random.uniform(-3, 3)
            self.vy = random.uniform(-6, -2)
            self.gravity = -0.1  # 上に昇る
        elif trap_type == "poison":
            self.color = (0, 255, 0)  # 緑
            self.vx = random.uniform(-4, 4)
            self.vy = random.uniform(-5, -1)
            self.gravity = 0.05
        else:
            self.color = (255, 255, 255)
            self.vx = random.uniform(-4, 4)
            self.vy = random.uniform(-6, -2)
            self.gravity = 0.2
            
        self.size = random.randint(3, 8)
        self.life = random.randint(30, 60)
        self.max_life = self.life
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.life -= 1
        self.vx *= 0.98  # 空気抵抗
        
    def draw(self, surface, camera_x, camera_y):
        if self.life <= 0:
            return
            
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        alpha = int(255 * (self.life / self.max_life))
        color = self.color + (alpha,)
        
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, color, (self.size, self.size), self.size)
        surface.blit(s, (screen_x - self.size, screen_y - self.size))


class TrapEffect:
    """罠を踏んだ時のエフェクト"""
    def __init__(self, x, y, trap_type, tile_size):
        self.x = x * tile_size + tile_size // 2  # タイル中心
        self.y = y * tile_size + tile_size // 2
        self.trap_type = trap_type
        self.tile_size = tile_size
        self.particles = []
        self.life = 60  # エフェクトの持続時間
        self.time = 0
        
        # パーティクル生成
        particle_count = 30 if trap_type == "fire" else 20
        for _ in range(particle_count):
            self.particles.append(TrapEffectParticle(self.x, self.y, trap_type))
        
        # 爆発リング用
        self.ring_radius = 0
        self.ring_max_radius = tile_size * 2
        self.ring_speed = tile_size / 10
        
    def update(self):
        self.life -= 1
        self.time += 1
        
        # パーティクル更新
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)
        
        # リング拡大
        if self.ring_radius < self.ring_max_radius:
            self.ring_radius += self.ring_speed
            
    def draw(self, surface, camera_x, camera_y):
        if self.life <= 0:
            return
        
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # 爆発リング描画
        if self.ring_radius < self.ring_max_radius:
            alpha = int(255 * (1 - self.ring_radius / self.ring_max_radius))
            
            if self.trap_type == "spike":
                color = (255, 0, 0, alpha)
            elif self.trap_type == "fire":
                color = (255, 165, 0, alpha)
            elif self.trap_type == "poison":
                color = (0, 255, 0, alpha)
            else:
                color = (255, 255, 255, alpha)
            
            s = pygame.Surface((int(self.ring_radius * 2), int(self.ring_radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(s, color, (int(self.ring_radius), int(self.ring_radius)), int(self.ring_radius), 3)
            surface.blit(s, (screen_x - int(self.ring_radius), screen_y - int(self.ring_radius)))
        
        # 画面振動用の線（オプション）
        if self.time < 10:
            flash_alpha = int(200 * (1 - self.time / 10))
            if self.trap_type == "spike":
                flash_color = (255, 0, 0, flash_alpha)
            elif self.trap_type == "fire":
                flash_color = (255, 165, 0, flash_alpha)
            elif self.trap_type == "poison":
                flash_color = (0, 255, 0, flash_alpha)
            else:
                flash_color = (255, 255, 255, flash_alpha)
            
            flash_s = pygame.Surface((self.tile_size * 3, self.tile_size * 3), pygame.SRCALPHA)
            pygame.draw.circle(flash_s, flash_color, (self.tile_size * 3 // 2, self.tile_size * 3 // 2), self.tile_size * 3 // 2)
            surface.blit(flash_s, (screen_x - self.tile_size * 3 // 2, screen_y - self.tile_size * 3 // 2))
        
        # パーティクル描画
        for particle in self.particles:
            particle.draw(surface, camera_x, camera_y)


class TrapManager:
    """トラップ管理クラス"""
    def __init__(self, tile_size: int):
        self.traps: List[Trap] = []
        self.tile_size = tile_size
        self.effects: List[TrapEffect] = []  # エフェクトリスト
    
    def generate_traps(self, map_gen: MapGenerator, trap_count: int = 20):
        """マップ上にランダムにトラップを生成"""
        self.traps.clear()
        self.effects.clear()  # エフェクトもクリア
        trap_types = ["spike", "fire", "poison"]
        attempts = 0
        max_attempts = trap_count * 10
        
        while len(self.traps) < trap_count and attempts < max_attempts:
            attempts += 1
            x = random.randint(0, map_gen.width - 1)
            y = random.randint(0, map_gen.height - 1)
            
            if map_gen.tilemap[x][y] == 1:
                if not any(t.tile_x == x and t.tile_y == y for t in self.traps):
                    trap_type = random.choice(trap_types)
                    self.traps.append(Trap(x, y, self.tile_size, trap_type))
    
    def update(self, dt: float = 1.0):
        """全てのトラップとエフェクトを更新"""
        for trap in self.traps:
            trap.update(dt)
        
        # エフェクト更新
        for effect in self.effects[:]:
            effect.update()
            if effect.life <= 0:
                self.effects.remove(effect)
    
    def draw(self, surface: pygame.Surface, camera_x: int = 0, camera_y: int = 0, show_debug: bool = False):
        """全てのトラップとエフェクトを描画"""
        for trap in self.traps:
            trap.draw(surface, camera_x, camera_y, show_debug)
        
        # エフェクト描画
        for effect in self.effects:
            effect.draw(surface, camera_x, camera_y)
    
    def check_collisions(self, player_rect: pygame.Rect) -> int:
        """
        プレイヤーとの衝突チェックして合計ダメージを返す
        発動したトラップはリストから削除され、エフェクトが生成される
        """
        total_damage = 0
        traps_to_remove = []
        
        for trap in self.traps:
            collision, damage, should_remove = trap.check_collision(player_rect)
            
            if collision and damage > 0:
                total_damage += damage
                if should_remove:
                    # エフェクトを生成
                    effect = TrapEffect(trap.tile_x, trap.tile_y, trap.trap_type, self.tile_size)
                    self.effects.append(effect)
                    traps_to_remove.append(trap)
        
        # 発動したトラップをリストから削除
        for trap in traps_to_remove:
            self.traps.remove(trap)
        
        return total_damage