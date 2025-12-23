import os
import random
from typing import Optional, Tuple
from collections import deque

import pygame

__all__ = ["Enemy"]


class Enemy:
	"""敵キャラの基本クラス。

	Base.py からインスタンス化して使えるように、座標・体力・速度・描画処理を提供します。
	プレイヤー位置が渡されれば追跡し、渡されなければランダム歩行します。
	"""

	def __init__(
		self,
		x: int,
		y: int,
		hp: int = 10,
		speed: float = 1.0,
		image_path: Optional[str] = None,
		tile_size: int = 16,
	) -> None:
		
		self.x = x
		self.y = y
		self.hp = hp
		self.max_hp = hp
		self.speed = speed
		self.tile_size = tile_size

		self._vx = 0.0
		self._vy = 0.0

		self._image = None
		self._rect = pygame.Rect(int(x), int(y), tile_size, tile_size)

		# 画像の読み込み（省略可）
		if image_path:
			try:
				base_dir = os.path.dirname(os.path.abspath(__file__))
				full_path = (
					image_path
					if os.path.isabs(image_path)
					else os.path.join(base_dir, image_path)
				)
				img = pygame.image.load(full_path).convert_alpha()
				self._image = pygame.transform.scale(img, (tile_size, tile_size))
			except Exception:
				# 読み込み失敗時は None のままにしてフォールバック描画を行う
				self._image = None

		# ランダム移動のためのタイマー
		self._change_dir_timer = 0.0

	@classmethod
	def spawn(cls, map_gen, count_per_room: int) -> list["Enemy"]:
		"""マップ情報に基づいて敵をランダムに配置・生成する。"""
		enemies = []
		for room in map_gen.rooms:
			for _ in range(count_per_room):
				tx = random.randint(max(room.left + 1, 0), max(room.right - 2, room.left))
				ty = random.randint(max(room.top + 1, 0), max(room.bottom - 2, room.top))
				ex = tx * map_gen.tile_size
				ey = ty * map_gen.tile_size
				
				enemies.append(
					cls(
						ex,
						ey,
						hp=20,
						speed=40.0,
						image_path="Assets/enemy_kyuri.png",
						tile_size=map_gen.tile_size,
					)
				)
		return enemies

	def draw(self, surface: pygame.Surface, camera_x: int = 0, camera_y: int = 0) -> None:
		"""敵を描画する。カメラオフセットに対応。"""
		screen_x = int(self.x) - camera_x
		screen_y = int(self.y) - camera_y

		if self._image:
			surface.blit(self._image, (screen_x, screen_y))
		else:
			# フォールバック: シンプルな矩形
			pygame.draw.rect(
				surface,
				(200, 50, 50),
				(screen_x, screen_y, self.tile_size, self.tile_size),
			)
		
	@property
	def rect(self) -> pygame.Rect:
		return self._rect

	def move_towards_player(
		self,
		player_tile_x: int,
		player_tile_y: int,
		map_gen,
		occupied: Optional[set] = None,
	) -> bool:
		"""
		プレイヤーへの直線距離（ユークリッド距離）を最小化する隣接タイルへ1マスだけ移動する。

		四方向（上下左右）のうち、通行可能（map_gen.tilemap == 1）で
		プレイヤーへの距離が現在より小さくなるタイルを選ぶ。
		"""
		# 敵の現在タイル座標（ピクセル座標 -> タイル座標）
		start_tx = int(self.x) // self.tile_size
		start_ty = int(self.y) // self.tile_size

		ptx = int(player_tile_x)
		pty = int(player_tile_y)

		# 既に同じタイルなら何もしない
		if (start_tx, start_ty) == (ptx, pty):
			return

		width = map_gen.width
		height = map_gen.height

		# 現在の二乗距離（sqrtは不要）
		curr_ds = (start_tx - ptx) * (start_tx - ptx) + (start_ty - pty) * (start_ty - pty)

		# 四方向を候補として距離でソートし、occupied に入っていない最良候補を選ぶ
		dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
		candidates = []
		for dx, dy in dirs:
			nx = start_tx + dx
			ny = start_ty + dy
			if 0 <= nx < width and 0 <= ny < height:
				if map_gen.tilemap[nx][ny] == 1:
					ds = (nx - ptx) * (nx - ptx) + (ny - pty) * (ny - pty)
					candidates.append((ds, (nx, ny)))

		if not candidates:
			return False

		candidates.sort(key=lambda x: x[0])

		occ = occupied or set()

		for _, (nx, ny) in candidates:
			# プレイヤーや他の敵と重ならないようにチェック
			if (nx, ny) in occ:
				continue
			# 移動実行
			self.x = nx * self.tile_size
			self.y = ny * self.tile_size
			self._rect.topleft = (int(self.x), int(self.y))
			return True

		# 有効な候補が見つからなかった
		return False

