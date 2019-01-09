"""
Dodger
"""

import sys
import random
import pygame
from pygame.locals import *


IMAGE_PATH = 'static/images/'
SOUND_PATH = 'static/sounds/'

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
TEXT_COLOR = (0, 0, 0)
BACKGROUND_COLOR = (255, 255, 255)
FPS = 60
BADDIE_MIN_SIZE = 10
BADDIE_MAX_SIZE = 40
BADDIE_MIN_SPEED = 1
BADDIE_MAX_SPEED = 8
ADD_NEW_BADDIE_RATE = 6
PLAYER_MOVE_RATE = 5


def terminate():
    pygame.quit()
    sys.exit()


def wait_for_player_to_press_key():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                return


def player_has_hit_baddie(player_rect, baddies):
    for b in baddies:
        if player_rect.colliderect(b['rect']):
            return True
    return False


def draw_text(text, font, surface, x, y):
    text_obj = font.render(text, 1, TEXT_COLOR)
    text_rect = text_obj.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_obj, text_rect)


pygame.init()
main_clock = pygame.time.Clock()
window_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Dodger Game')
pygame.mouse.set_visible(False)

font = pygame.font.SysFont(None, 35)

# sounds
game_over_sound = pygame.mixer.Sound(SOUND_PATH + 'game_over.wav')
pygame.mixer.music.load(SOUND_PATH + 'house_lo.mp3')

# images
p_image = pygame.image.load(IMAGE_PATH + 'player.png')
player_image = pygame.transform.scale(p_image, (40, 40))
player_rect = player_image.get_rect()
baddie_image = pygame.image.load(IMAGE_PATH + 'baddie.png')

# display the start screen
window_surface.fill(BACKGROUND_COLOR)
draw_text('Dodger', font, window_surface, (WINDOW_WIDTH/3), (WINDOW_HEIGHT/3))
draw_text('Press any key to start the game', font, window_surface, (WINDOW_WIDTH/5) - 30, (WINDOW_HEIGHT/3) + 50)
pygame.display.update()
wait_for_player_to_press_key()

top_score = 0
while True:
    # Setting up the start of the game
    baddies = []
    score = 0
    player_rect.topleft = (WINDOW_WIDTH / 2, WINDOW_HEIGHT - 50)
    move_left = move_right = move_up = move_down = False
    reverse_cheat = slow_cheat = False
    baddie_add_counter = 0
    pygame.mixer.music.play(-1, 0.0)

    # the game loop runs while the game is running
    while True:
        score += 1

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()

            if event.type == KEYDOWN:
                if event.key == K_z:
                    reverse_cheat = True
                if event.key == K_x:
                    slow_cheat = True
                if event.key == K_LEFT or event.key == K_a:
                    move_right = False
                    move_left = True
                if event.key == K_RIGHT or event.key == K_d:
                    move_right = True
                    move_left = False
                if event.key == K_UP or event.key == K_w:
                    move_down = False
                    move_up = True
                if event.key == K_DOWN or event.key == K_s:
                    move_down = True
                    move_up = False
            if event.type == KEYUP:
                if event.key == K_z:
                    reverse_cheat = False
                    score = 0
                if event.key == K_x:
                    slow_cheat = False
                    score = 0
                if event.key == K_ESCAPE:
                    terminate()

                if event.key == K_LEFT or event.key == K_a:
                    move_left = False
                if event.key == K_RIGHT or event.key == K_d:
                    move_right = False
                if event.key == K_UP or event.key == K_w:
                    move_up = False
                if event.key == K_DOWN or event.key == K_s:
                    move_down = False

            if event.type == MOUSEBUTTONUP:
                # if the mouse moves, move the player to the mouse pointer
                player_rect.centerx = event.pos[0]
                player_rect.centery = event.pos[1]

        # if necessary, add new humans to the top of the screen
        if not reverse_cheat and not slow_cheat:
            baddie_add_counter += 1
        if baddie_add_counter == ADD_NEW_BADDIE_RATE:
            baddie_add_counter = 0
            baddie_size = random.randint(BADDIE_MIN_SIZE, BADDIE_MAX_SIZE)
            new_baddie = {
                'rect': pygame.Rect(random.randint(0, WINDOW_WIDTH - baddie_size),
                                    0 - baddie_size, baddie_size, baddie_size),
                'speed': random.randint(BADDIE_MIN_SPEED, BADDIE_MAX_SPEED),
                'surface': pygame.transform.scale(baddie_image, (baddie_size, baddie_size))
            }
            baddies.append(new_baddie)

        # player movement
        if move_left and player_rect.left > 0:
            player_rect.move_ip(-1 * PLAYER_MOVE_RATE, 0)
        if move_right and player_rect.right < WINDOW_WIDTH:
            player_rect.move_ip(PLAYER_MOVE_RATE, 0)
        if move_up and player_rect.top > 0:
            player_rect.move_ip(0, -1 * PLAYER_MOVE_RATE)
        if move_down and player_rect.bottom < WINDOW_HEIGHT:
            player_rect.move_ip(0, PLAYER_MOVE_RATE)

        # move the humans down
        for b in baddies:
            if not reverse_cheat and not slow_cheat:
                b['rect'].move_ip(0, b['speed'])
            elif reverse_cheat:
                b['rect'].move_ip(0, -5)
            elif slow_cheat:
                b['rect'].move_ip(0, 1)

        # remove the humans who fell behind the bottom of the screen
        for b in baddies[:]:
            if b['rect'].top > WINDOW_HEIGHT:
                baddies.remove(b)

        # display the game world in the window
        window_surface.fill(BACKGROUND_COLOR)

        # display the number of points and the best result
        draw_text(f'Score: {score}', font, window_surface, 10, 0)
        draw_text(f'Best score: {top_score}', font, window_surface, 10, 40)

        # display player
        window_surface.blit(player_image, player_rect)

        # display every human
        for b in baddies:
            window_surface.blit(b['surface'], b['rect'])

        pygame.display.update()

        # check if any of the humans hit the player
        if player_has_hit_baddie(player_rect, baddies):
            if score > top_score:
                # new high score
                top_score = score
            break

        main_clock.tick(FPS)

    # displaying the game and displaying the caption 'Game over'
    pygame.mixer.music.stop()
    game_over_sound.play()

    draw_text('GAME OVER!', font, window_surface, (WINDOW_WIDTH/3), (WINDOW_HEIGHT/3))
    draw_text('Press any key to start new game', font, window_surface,
              (WINDOW_WIDTH/3) - 120, (WINDOW_HEIGHT / 3) + 50)

    pygame.display.update()
    wait_for_player_to_press_key()

    game_over_sound.stop()
