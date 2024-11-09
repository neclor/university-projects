import sys
from typing import Tuple
import math
import pygame


WHITE: Tuple[int, int, int] = (255, 255, 255)
BLACK: Tuple[int, int, int] = (0, 0, 0)
RED: Tuple[int, int, int] = (255, 0, 0)

WINDOW_SIZE: Tuple[int, int] = (800, 600)

FOV_H: float = math.pi / 2
FOV_V: float = math.atan(math.tan(FOV_H / 2) / (WINDOW_SIZE[0] / WINDOW_SIZE[1])) * 2
RAYS_NUMBER: int = 100
RAY_LENGTH: int = 1000

RAY_WIDTH: int = WINDOW_SIZE[0] // RAYS_NUMBER

WALL_SIZE: int = 100
HALF_WALL_HEIGHT: int = 50

fps: int = 60
clock: pygame.time.Clock
window: pygame.Surface


level_text_map: list[str] = [
	"##########",
	"#..#...#.#",
	"#......#.#",
	"#........#",
	"#..####..#",
	"##########"]
level_map: list = []


player: dict = {
	"position": [150, 200],
	"rotation": 0.0,
	"speed": 100,
	"rotation_speed": math.pi / 2,
}


def main() -> None:
	init()
	run()


def init() -> None:
	pygame.init()

	global clock, window
	clock = pygame.time.Clock()
	window = pygame.display.set_mode(WINDOW_SIZE)


def run() -> None:
	create_level_map()
	while True:
		move_player()
		draw()
		ray_cast()
		draw_map()
		update()
		check_exit()


def create_level_map() -> None:
	for y, string in enumerate(level_text_map):
		for x, char in enumerate(string):
			if char == '#':
				level_map.append((x, y))


def move_player() -> None:
	delta: float = clock.get_time() / 1000

	direction: list[float] = [0.0, 0.0]

	keys = pygame.key.get_pressed()
	if keys[pygame.K_w]:
		direction[1] -= 1
	if keys[pygame.K_s]:
		direction[1] += 1
	if keys[pygame.K_a]:
		direction[0] -= 1
	if keys[pygame.K_d]:
		direction[0] += 1

	if keys[pygame.K_LEFT]:
		player["rotation"] -= player["rotation_speed"] * delta
	if keys[pygame.K_RIGHT]:
		player["rotation"] += player["rotation_speed"] * delta

	direction_rotated: list[float] = [0.0, 0.0]
	direction_rotated[0] = direction[0] * math.cos(player["rotation"] + math.pi / 2) - direction[1] * math.sin(player["rotation"] + math.pi / 2)
	direction_rotated[1] = direction[0] * math.sin(player["rotation"] + math.pi / 2) + direction[1] * math.cos(player["rotation"] + math.pi / 2)

	velocity: list[float] = [0.0 ,0.0]
	velocity[0] = direction_rotated[0] * player["speed"]
	velocity[1] = direction_rotated[1] * player["speed"]

	player["position"][0] += velocity[0] * delta
	player["position"][1] += velocity[1] * delta


def draw() -> None:
	window.fill(BLACK)


def draw_map() -> None:
	for wall in level_map:
		pygame.draw.rect(window, RED, (int(wall[0] * WALL_SIZE / 4), int(wall[1] * WALL_SIZE / 4), WALL_SIZE / 4, WALL_SIZE / 4))
	pygame.draw.circle(window, RED, (player["position"][0] / 4, player["position"][1] / 4), 10)


def ray_cast() -> None:
	delta_angle: float = FOV_H / RAYS_NUMBER
	ray_rotation: float = player["rotation"] - FOV_H / 2
	for ray in range(RAYS_NUMBER):
		x: float = 0
		y: float = 0
		for length in range(RAY_LENGTH):
			x = player["position"][0] + length * math.cos(ray_rotation)
			y = player["position"][1] + length * math.sin(ray_rotation)
			if (x // WALL_SIZE, y // WALL_SIZE) in level_map:
				relative_angle: float = ray_rotation - player["rotation"]
				distance: float = length * math.cos(relative_angle)
				half_screen_projection_height: float = 1
				if distance != 0:
					half_screen_projection_height = HALF_WALL_HEIGHT / distance / math.tan(FOV_V / 2)
				screen_rect = (ray * RAY_WIDTH, WINDOW_SIZE[1] / 2 * (1 - half_screen_projection_height), RAY_WIDTH, WINDOW_SIZE[1] * half_screen_projection_height)
				pygame.draw.rect(window, WHITE, screen_rect)
				break

		pygame.draw.line(window, RED, (player["position"][0] / 4, player["position"][1] / 4), (x / 4, y / 4))
		ray_rotation += delta_angle


def update() -> None:
	pygame.display.set_caption(str(clock.get_fps()))
	pygame.display.flip()
	clock.tick(fps)


def check_exit():
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()


if __name__ == "__main__":
	main()
