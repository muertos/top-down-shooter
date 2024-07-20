#!/usr/bin/env python

from objects import *
import copy

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BG_COLOR = (0,0,0)
GAME_TITLE = "Shoot 'em up"

# define testing level
level = [
  [0,0,0,0,1,0,0,0,1,0,0,0],
  [1,0,0,0,0,0,1,0,0,0,0,1],
  [1,0,0,0,0,0,0,0,0,0,0,1],
  [0,1,0,0,0,0,0,0,0,0,1,0]]
  
def make_level(level, sprites):
  # initialize width / height
  img = pygame.image.load('data/enemy_ship.png')
  """ given a matrix, make a level, starting at (0,0) """  
  for i in range(len(level)):
    for j in range(len(level[i])):
      if level[i][j] == 1:
        enemy = Enemy(((img.get_width() + 12) * j), ((img.get_height() + 12)* i), sprites)
        sprites.add(enemy)

def draw_text(text, color=(0,200,0)):
  font = pygame.font.SysFont(None, 30)
  return font.render(text, False, color)

def create_game_window():
  screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
  background = pygame.Surface(screen.get_size())
  background = background.convert()
  background.fill(BG_COLOR)
  screen.blit(background, (0,0))
  pygame.display.flip()
  screen.fill(BG_COLOR)
  pygame.display.set_caption(GAME_TITLE)
  return screen, background

def create_player(group):
  player_img = pygame.image.load('data/ship.png')
  return Player((SCREEN_WIDTH / 2) - (player_img.get_width() / 2), SCREEN_HEIGHT - player_img.get_height(), group)

def create_bullet(player, bullet_group):
  bullet_img = pygame.image.load('data/bullet.png')
  return Bullet(player.rect.x + (player.image.get_width() / 2) - (bullet_img.get_width() / 2), player.rect.y, bullet_group)

def create_enemy_bullet(enemy, enemy_bullet_group):
  enemy_bullet_img = pygame.image.load('data/enemy_bullet.png')
  return EnemyBullet(enemy.rect.x + enemy.image.get_width() / 2 - enemy_bullet_img.get_width() / 2, enemy.rect.y + enemy_bullet_img.get_height(), enemy_bullet_group)

def main():
  # initialize pygame and game screen
  pygame.init()
  screen, background = create_game_window()

  # sprite groups
  bullet_group = pygame.sprite.Group()
  enemy_group = pygame.sprite.Group()
  enemy_bullet_group = pygame.sprite.Group()
  player_group = pygame.sprite.Group()
  
  # game state and game objects
  lose = win = False
  player = create_player(player_group)
  make_level(level, enemy_group)

  clock = pygame.time.Clock()
  while True:
    clock.tick(120)
    screen.blit(background, (0,0))

    keys = pygame.key.get_pressed()
    time_now = pygame.time.get_ticks()
    prev_x = player.rect.x
    if not lose:
      if keys[pygame.K_LEFT]:
        player.move(-player.speed)
        if player.rect.x < 0:
          player.rect.x = prev_x
      if keys[pygame.K_RIGHT]:
        player.move(player.speed)
        if player.rect.x + player.image.get_width() > screen.get_width():
          player.rect.x = prev_x
      if keys[pygame.K_SPACE] and time_now > player.next_bullet_time:
        bullet = create_bullet(player, bullet_group)
        # introduce delay between bullets
        player.next_bullet_time = bullet.delay + time_now
    if keys[pygame.K_END] or keys[pygame.K_ESCAPE]:
      sys.exit(0)
    
    # event handler
    for e in pygame.event.get():
      if e.type == QUIT:
        return

    # move bullets / bullet collision detection
    for bullet in bullet_group.sprites():
      bullet.move(bullet.speed)
      collisions = pygame.sprite.spritecollide(bullet, enemy_group, True, collided=pygame.sprite.collide_mask)
      for enemy in collisions:
        bullet_group.remove(bullet)
        if not enemy_group:
          win = True
        if bullet.rect.y < 0:
          bullet_group.remove(bullet)
          
    # enemy movement / collision detection  
    for enemy in enemy_group.sprites():
      prev_x = enemy.rect.x
      prev_y = enemy.rect.y
      enemy.move_random()
      collisions = pygame.sprite.spritecollide(enemy, enemy_group, False, collided=pygame.sprite.collide_mask)
      collisions.remove(enemy)
      if collisions:
        enemy.rect.x = prev_x
        enemy.rect.y = prev_y
      # check if enemies are out of bounds  
      if enemy.rect.x + enemy.image.get_width() > screen.get_width():
        enemy.rect.x = prev_x
      if enemy.rect.x < 0:
        enemy.rect.x = prev_x
      if enemy.rect.y + enemy.image.get_height() > screen.get_height():
        enemy.rect.y = prev_y
      if enemy.rect.y < 0:
        enemy.rect.y = prev_y

    # create enemy bullets
    for enemy in enemy_group.sprites():
      if enemy.shooting and time_now > enemy.next_bullet_time:
        enemy_bullet = create_enemy_bullet(enemy, enemy_bullet_group)
        enemy_bullet_group.add(enemy_bullet)
        enemy.next_bullet_time = time_now + enemy_bullet.delay

    # move enemy bullets
    for bullet in enemy_bullet_group.sprites():
      bullet.move(bullet.speed)
      collisions = pygame.sprite.spritecollide(bullet, player_group, False, collided=pygame.sprite.collide_mask)
      if collisions:
        lose = True

    # we draw things after screen.fill, otherwise they don't display!
    screen.fill((0,0,0))
    
    if win:
      screen.blit(draw_text("you're a winner! :)"), (SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2 - 30))
    if lose:
      screen.blit(draw_text("you lose :(", (200,0,0)), (SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2 - 30))
    bullet_group.draw(screen)
    enemy_group.draw(screen)
    enemy_bullet_group.draw(screen)
    player_group.draw(screen)

    pygame.display.flip()

if __name__ == "__main__":
  main()