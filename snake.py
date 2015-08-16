__author__ = 'Risto Pärnapuu'
__version__ = "1.01"

# !/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame.display
import eztext
import os
import urllib.request
import urllib.parse
from random import randint
from math import *
from operator import itemgetter

# Colors
gray = (104, 104, 104)
light_gray = (248, 248, 248, 210)
green = (32, 178, 170, 250)
white = (255, 255, 255)
black = (000, 000, 000)
blue = (0, 191, 255)
red = (255, 000, 56, 50)
orange = (255, 127, 80)

# Window size
playable_squares_x = 16 * 3
playable_squares_y = 9 * 3
width = playable_squares_x * 22 + 46
length = playable_squares_y * 22 + 46

pygame.init()
gameDisplay = pygame.display.set_mode((width, length))
pygame.display.set_caption("Snake ")
icon = pygame.image.load("snakeicon.png").convert_alpha()
pygame.display.set_icon(icon)

# Sound effects
laugh = pygame.mixer.Sound('sound/laugh1.wav')
eatfood = pygame.mixer.Sound('sound/food.wav')

clock = pygame.time.Clock()

# FUNCTIONS=============================================================================================================
def check_connectivity(reference):
    try:
        urllib.request.urlopen(reference, timeout=2)
        return True
    except urllib.request.URLError:
        return False


def generate_food(not_allowed):
    while True:
        food_loc_x = 24 + 22 * randint(0, playable_squares_x - 1)
        food_loc_y = 24 + 22 * randint(0, playable_squares_y - 1)
        if [food_loc_x, food_loc_y, 20, 20] not in not_allowed:
            return [food_loc_x, food_loc_y, 20, 20]


def generate_level(wall_loc_x, wall_loc_y):
    generated_walls = []
    for x in range(2, wall_loc_x, 22):
        for y in range(2, wall_loc_y, 22):
            if x == 2 or y == 2 or y == wall_loc_y - 22 or x == wall_loc_x - 22:
                generated_walls.append([x, y, 20, 20])
    return generated_walls


def generate_background(bg_loc_x, bg_loc_y):
    generated_background = []
    for x in range(2, bg_loc_x, 22):
        for y in range(2, bg_loc_y, 22):
            generated_background.append([x, y, 20, 20])
    return generated_background


def save_score(score, old_scoreboard, current_speed, user_name):
    if len(old_scoreboard) < 10:
        old_scoreboard.append([score, user_name])
    elif old_scoreboard[0][0] < score:
        old_scoreboard[0] = [score, user_name]
    else:
        return old_scoreboard

    new_scoreboard = sorted(old_scoreboard, key=itemgetter(0))
    scoreboards[speeds.index(current_speed)] = new_scoreboard

    if network_status and check_connectivity('http://www.google.com/'):
        upload = ""

        for k in range(len(new_scoreboard)):
            upload += str(new_scoreboard[k][0]) + "-" + str(new_scoreboard[k][1]) + "\n"

        url = ('http://kodu.ut.ee/~a50871/Snake/upload.php?table=save/scoreboard' + str(
            current_speed) + '.txt' + '&data=' + upload)
        url = url.replace("\n", '%0A').replace(" ", '+')
        urllib.request.urlopen(url)
    else:
        f = open("save/scoreboard" + str(current_speed) + ".txt", "w")

        for k in range(len(new_scoreboard)):
            f.write(str(new_scoreboard[k][0]) + "-" + str(new_scoreboard[k][1]) + "\n")

        f.close()

    return new_scoreboard


def save_worm(head_loc_x, head_loc_y, locations):
    if (head_loc_x - 2) % 22 == 0 and (head_loc_y - 2) % 22 == 0 and [head_loc_x, head_loc_y, 20, 20] not in locations:
        locations.append([head_loc_x, head_loc_y, 20, 20])
        if len(locations) > 1:
            if locations[-2][0] > head_loc_x:
                new_last_key = "L"
                return locations, new_last_key
            elif locations[-2][0] < head_loc_x:
                new_last_key = "R"
                return locations, new_last_key
            elif locations[-2][1] > head_loc_y:
                new_last_key = "U"
                return locations, new_last_key
            elif locations[-2][1] < head_loc_y:
                new_last_key = "D"
                return locations, new_last_key
        else:
            new_last_key = "R"
            return locations, new_last_key


def load_scores_online(files):
    new_scoreboards = []
    url_start = 'http://kodu.ut.ee/~a50871/Snake/'
    for board in files:
        data = urllib.request.urlopen(url_start + board).read()
        raw_data = data.decode("utf-8")
        raw_data = raw_data.strip()
        if raw_data != "":
            new_scoreboard = raw_data.split('\n')
            for k in range(len(new_scoreboard)):
                score = int(new_scoreboard[k].strip().split("-")[0])
                name = new_scoreboard[k].strip().split("-")[1]
                new_scoreboard[k] = [[], []]
                new_scoreboard[k][0] = score
                new_scoreboard[k][1] = name
            new_scoreboard = sorted(new_scoreboard, key=itemgetter(0))
            new_scoreboards.append(new_scoreboard)
        else:
            new_scoreboard = []
            new_scoreboards.append(new_scoreboard)
    return new_scoreboards


def load_scores_local(files):
    new_scoreboards = []
    for board in files:

        if os.path.exists(board):
            f = open(board)
            new_scoreboard = f.readlines()
            for k in range(len(new_scoreboard)):
                score = int(new_scoreboard[k].strip().split("-")[0])
                name = new_scoreboard[k].strip().split("-")[1]
                new_scoreboard[k] = [[], []]
                new_scoreboard[k][0] = score
                new_scoreboard[k][1] = name
            new_scoreboard = sorted(new_scoreboard, key=itemgetter(0))
            new_scoreboards.append(new_scoreboard)
            f.close()
        else:
            new_scoreboard = []
            new_scoreboards.append(new_scoreboard)
    return new_scoreboards


def change_speed(current_speed, arrow_dir):
    speed_texts = ["<- [Sonic]   Fast   Normal   Slow   Captain Slow ->",
                   "<- Sonic   [Fast]   Normal   Slow   Captain Slow ->",
                   "<- Sonic   Fast   [Normal]   Slow   Captain Slow ->",
                   "<- Sonic   Fast   Normal   [Slow]   Captain Slow ->",
                   "<- Sonic   Fast   Normal   Slow   [Captain Slow] ->"]
    if arrow_dir == 1:
        if current_speed != speeds[4]:
            current_speed_id = speeds.index(current_speed)
            return speed_texts[current_speed_id + 1], speeds[current_speed_id + 1], scoreboards[current_speed_id + 1]
        else:
            return speed_texts[0], speeds[0], scoreboards[0]
    elif arrow_dir == -1:
        if current_speed != speeds[0]:
            current_speed_id = speeds.index(current_speed)
            return speed_texts[current_speed_id - 1], speeds[current_speed_id - 1], scoreboards[current_speed_id - 1]
        else:
            return speed_texts[4], speeds[4], scoreboards[4]


def rainbow_colors(l):
    red_tail_color = sin(0.05 * l + 0) * 127 + 128
    green_tail_color = sin(0.05 * l + 2) * 127 + 128
    blue_tail_color = sin(0.05 * l + 4) * 127 + 128
    return red_tail_color, green_tail_color, blue_tail_color


def draw_worm(locations):
    for k in range(len(locations)):
        if k == len(locations) - 1:
            if rainbow_mode:
                pygame.draw.rect(gameDisplay, rainbow_colors(k), locations[k])
            else:
                pygame.draw.rect(gameDisplay, blue, locations[k])
        else:
            if rainbow_mode:
                pygame.draw.rect(gameDisplay, rainbow_colors(k), locations[k])
            else:
                tail_color = + (len(locations) - k)
                pygame.draw.rect(gameDisplay, (tail_color, tail_color, tail_color), locations[k])


# PRE_SET_VARIABLES=====================================================================================================
game_exit = False
food_set = False
game_pause = False
game_over = True
game_started = False
extra_food = False
rainbow_mode = False
sound_on = True
name_change = False
network_status = False

# Speed
speeds = [10, 5, 2.5, 2, 1]
speed = speeds[2]
speed_text = pygame.font.SysFont("Verdana", 15).render("<- Sonic   Fast   [Normal]   Slow   Captain Slow ->", True,
                                                       black)

if not os.path.exists('save'):
    os.makedirs('save')
scoreboards = load_scores_local(
    ["save/scoreboard10.txt", "save/scoreboard5.txt", "save/scoreboard2.5.txt", "save/scoreboard2.txt",
     "save/scoreboard1.txt"])
scoreboard = scoreboards[speeds.index(speed)]

walls = generate_level(width, length)
background = generate_background(width, length)

# Text input
txtbx = eztext.Input(maxlength=45, color=gray, prompt='Change name (F1): ')

# MAIN_LOOP=============================================================================================================

while not game_exit:  # Game loop
    for event in pygame.event.get():
        # print(o, event)

        if event.type == pygame.QUIT:
            game_exit = True

        if event.type == pygame.KEYUP:
            if (not game_started or game_over) and name_change:
                txtbx.update(event)

        if event.type == pygame.KEYDOWN:
            # Sound on/off buttons
            if event.key == pygame.K_v:
                if sound_on:
                    sound_on = False
                else:
                    sound_on = True

            # Pause game
            if event.key == pygame.K_SPACE and not game_over and game_started:
                if not game_pause:
                    game_pause = True
                else:
                    game_pause = False
            if game_pause:
                break

            # Ask for a player name if no name has been entered, don't start the game
            if event.key == pygame.K_RETURN and game_over and txtbx.get_value() == "":
                name_change = True
                txtbx.set_color(red)

            # Start new game, if player name is entered
            if event.key == pygame.K_RETURN and game_over and txtbx.get_value() != "":
                worm_locations = []  # Empty the worm
                last_key = "R"
                laugh.fadeout(500)  # Fade out sound
                # Worm starting point and length
                box_x = 46
                box_y = 46
                increase_x = speed
                increase_y = 0
                worm_length = 2
                forward_x = 0
                forward_y = 0
                worm_locations.append([box_x, box_y, 20, 20])
                game_started = True  # Game is started, home screen is not shown
                game_exit = False  # Game is started, game over screen is not shown
                food_set = False  # Delete the last food
                game_pause = False  # Game started and not on pause
                game_over = False  # Game is not lost
                name_change = False
                txtbx.set_color(gray)

            # Username
            if (not game_started or game_over) and name_change:
                txtbx.update(event)

            # Rainbow mode
            if not game_over and game_started and event.key == pygame.K_TAB:
                if rainbow_mode:
                    rainbow_mode = False
                else:
                    rainbow_mode = True

            # Keys to change the speed
            if (not game_started or game_over) and event.key == pygame.K_F1:
                if name_change:
                    txtbx.set_color(gray)
                    name_change = False
                else:
                    txtbx.set_color(black)
                    name_change = True

            # Keys to change between online and offline mode
            if (not game_started or game_over) and event.key == pygame.K_F2:
                if network_status:
                    scoreboards = load_scores_local(["save/scoreboard10.txt",
                                                     "save/scoreboard5.txt",
                                                     "save/scoreboard2.5.txt",
                                                     "save/scoreboard2.txt",
                                                     "save/scoreboard1.txt"])
                    scoreboard = load_scores_local(["save/scoreboard" + str(speed) + ".txt"])[0]
                    network_status = False
                elif not network_status and check_connectivity('http://www.google.com/'):
                    scoreboards = load_scores_online(["save/scoreboard10.txt",
                                                      "save/scoreboard5.txt",
                                                      "save/scoreboard2.5.txt",
                                                      "save/scoreboard2.txt",
                                                      "save/scoreboard1.txt"])
                    scoreboard = load_scores_online(["save/scoreboard" + str(speed) + ".txt"])[0]
                    network_status = True

            if (not game_started or game_over) and event.key == pygame.K_RIGHT:
                kiri, speed, scoreboard = change_speed(speed, 1)
                speed_text = pygame.font.SysFont("Verdana", 15).render(kiri, True, black)

            if (not game_started or game_over) and event.key == pygame.K_LEFT:
                kiri, speed, scoreboard = change_speed(speed, -1)
                speed_text = pygame.font.SysFont("Verdana", 15).render(kiri, True, black)

            # Keys to change the direction of worm
            if (event.key == pygame.K_RIGHT or event.key == pygame.K_d) \
                    and game_started and last_key != "L" and last_key != "R":
                box_y = worm_locations[-1][1]
                increase_x = speed
                forward_x = + (abs(forward_y) + abs(forward_x))
                increase_y = 0
                break
            if (event.key == pygame.K_LEFT or event.key == pygame.K_a) and \
                    game_started and last_key != "R" and last_key != "L":
                box_y = worm_locations[-1][1]
                increase_x = -speed
                forward_x = - (abs(forward_y) + abs(forward_x))
                increase_y = 0
                break
            if (event.key == pygame.K_UP or event.key == pygame.K_w) and \
                    game_started and last_key != "D" and last_key != "U":
                box_x = worm_locations[-1][0]
                increase_y = -speed
                forward_y = - (abs(forward_y) + abs(forward_x))
                increase_x = 0
                break
            if (event.key == pygame.K_DOWN or event.key == pygame.K_s) and \
                    game_started and last_key != "U" and last_key != "D":
                box_x = worm_locations[-1][0]
                increase_y = speed
                forward_y = + (abs(forward_y) + abs(forward_x))
                increase_x = 0
                break

    # Home screen setup
    if not game_started:
        # Joonistan sinad
        for j in range(len(walls)):
            pygame.draw.rect(gameDisplay, gray, walls[j])
        # Joonistan läbipaistva kasti üle terve akna
        rect = pygame.Surface((width, length), pygame.SRCALPHA, 32)
        rect.fill(light_gray)
        gameDisplay.blit(rect, [0, 0])
        # Kuvan vajaliku teksti ekraanile
        txtbx.draw(gameDisplay)  # Player name

        status_text = "Online (F2)" if network_status else "Offline (F2)"
        status_text_color = green if network_status else red
        game_mode_text = pygame.font.SysFont("Verdana", 10).render(status_text, True, status_text_color)
        game_start_text = pygame.font.SysFont("Verdana", 100).render("Snake", True, blue)
        author_text = pygame.font.SysFont("Verdana", 13).render("By Risto Parnapuu", True, blue)
        replay_text = pygame.font.SysFont("Verdana", 10).render(
            "Press ENTER to play, SPACE to pause and TAB to add some magic ;)", True, gray)
        player_text = pygame.font.SysFont("Verdana", 10).render("Change name (F1): " + str(txtbx.get_value()), True,
                                                                gray)

        worm_length = game_start_text.get_height() + \
                      author_text.get_height() + \
                      replay_text.get_height() + \
                      speed_text.get_height()
        gameDisplay.blit(game_mode_text, (width // 2 - game_mode_text.get_width() // 2 + 95,
                                          length // 2 - worm_length // 2 + 25))
        gameDisplay.blit(game_start_text, (width // 2 - game_start_text.get_width() // 2,
                                           length // 2 - worm_length // 2))
        gameDisplay.blit(author_text, (width // 2 - author_text.get_width() // 2,
                                       length // 2 - worm_length // 2 + game_start_text.get_height() - 20))
        a = gameDisplay.blit(speed_text, (width // 2 - speed_text.get_width() // 2,
                                          length // 2 - speed_text.get_height() // 2 + 43))
        gameDisplay.blit(replay_text, (width // 2 - replay_text.get_width() // 2,
                                       length // 2 - replay_text.get_height() // 2 + 60))
        txtbx.set_pos(width // 2 - player_text.get_width() // 2,
                      length // 2 - player_text.get_height() // 2 + 77)

        pygame.display.update()
        continue

    # Game over screen setup
    if game_over:
        # Draw walls
        for j in range(len(walls)):
            pygame.draw.rect(gameDisplay, gray, walls[j])

        # Show worm that hit the wall
        draw_worm(worm_locations)

        # Transparent box to cover everything
        rect = pygame.Surface((width, length), pygame.SRCALPHA, 32)
        rect.fill(light_gray)
        gameDisplay.blit(rect, [0, 0])

        # All necessary texts
        game_over_text = pygame.font.SysFont("Verdana", 55).render("Game Over", True, red)
        gameDisplay.blit(game_over_text, (
            width // 2 - game_over_text.get_width() // 2, length // 2 - game_over_text.get_height() // 2 - 150))

        score_text = pygame.font.SysFont("Verdana", 30).render("Score: " + str(worm_length - 2), True, black)
        gameDisplay.blit(score_text,
                         (width // 2 - score_text.get_width() // 2, length // 2 - score_text.get_height() // 2 - 110))

        replay_text = pygame.font.SysFont("Verdana", 15).render("(Press ENTER to play again)", True, gray)
        gameDisplay.blit(replay_text,
                         (width // 2 - replay_text.get_width() // 2, length // 2 - replay_text.get_height() // 2 - 85))

        player_text = pygame.font.SysFont("Verdana", 10).render("Change name (F1): " + str(txtbx.get_value()), True,
                                                                gray)
        txtbx.set_pos(width // 2 - player_text.get_width() // 2, length // 2 - player_text.get_height() // 2 - 67)

        a = gameDisplay.blit(speed_text, (
            width // 2 - speed_text.get_width() // 2, length // 2 - speed_text.get_height() // 2 - 50))
        status_text = "online" if network_status else "offline"
        high_scores_text = pygame.font.SysFont("Verdana", 15).render("High Scores [" + status_text + " (F2)]", True,
                                                                     black)
        gameDisplay.blit(high_scores_text, (
            width // 2 - high_scores_text.get_width() // 2, length // 2 - high_scores_text.get_height() // 2 - 15))

        # Show leaderboard
        a = 20
        for i in range(len(scoreboard)):
            if i == 0 or i == 1 or i == 2:
                color = (i * a, i * a, i * a)
            else:
                color = (i * a, i * a, i * a)
            high_scores_text = pygame.font.SysFont("Verdana", 15).render(
                str(i + 1) + ". " + str(scoreboard[len(scoreboard) - i - 1][0]) + " - " + str(
                    scoreboard[len(scoreboard) - i - 1][1]), True, color)
            gameDisplay.blit(high_scores_text, (width // 2 - high_scores_text.get_width() // 2,
                                                length // 2 - high_scores_text.get_height() // 2 + 5 + (i * 15)))

        # Player name
        txtbx.draw(gameDisplay)

        pygame.display.update()
        continue

    # Draw white background and fill it with white squares
    gameDisplay.fill(white)
    for square in background:
        pygame.draw.rect(gameDisplay, light_gray, square)

    # Pause screen
    if game_pause:
        # Draw walls
        for j in range(len(walls)):
            pygame.draw.rect(gameDisplay, gray, walls[j])
        # Draw worm
        draw_worm(worm_locations)
        # Transparent box to cover everything
        rect = pygame.Surface((width, length), pygame.SRCALPHA, 32)
        rect.fill(light_gray)
        gameDisplay.blit(rect, [0, 0])
        # Pause text
        game_start_text = pygame.font.SysFont("Verdana", 55).render("Paused", True, red)
        gameDisplay.blit(game_start_text, (
            width // 2 - game_start_text.get_width() // 2, length // 2 - game_start_text.get_height() // 2))
        pygame.display.update()
        continue

    # Check if worm is on a legal spot
    forward_x += increase_x
    forward_y += increase_y
    if abs(forward_x) >= 10:
        box_x += 22 * abs(forward_x) / forward_x
        forward_x, forward_y = 0, 0
        if not (increase_x == 0 and increase_y == 0) and (
                        [box_x, box_y, 20, 20] in worm_locations or [box_x, box_y, 20, 20] in walls):
            game_over = True
            if network_status and check_connectivity('http://www.google.com/'):
                scoreboard = load_scores_online(["save/scoreboard" + str(speed) + ".txt"])[0]
            else:
                network_status = False
                scoreboard = load_scores_local(["save/scoreboard" + str(speed) + ".txt"])[0]
            scoreboard = save_score(worm_length - 2, scoreboard, speed, txtbx.get_value())
            # If didn't get on a scoreboard or length is less than 4
            if worm_length - 2 < scoreboard[0][0] or worm_length - 2 < 4:
                if sound_on:
                    laugh.play()
            continue
        worm_locations, last_key = save_worm(box_x, box_y, worm_locations)
    elif abs(forward_y) >= 10:
        box_y += 22 * abs(forward_y) / forward_y
        forward_x, forward_y = 0, 0
        if not (increase_x == 0 and increase_y == 0) and (
                        [box_x, box_y, 20, 20] in worm_locations or [box_x, box_y, 20, 20] in walls):
            game_over = True
            if network_status and check_connectivity('http://www.google.com/'):
                scoreboard = load_scores_online(["save/scoreboard" + str(speed) + ".txt"])[0]
            else:
                network_status = False
                scoreboard = load_scores_local(["save/scoreboard" + str(speed) + ".txt"])[0]
            scoreboard = save_score(worm_length - 2, scoreboard, speed, txtbx.get_value())
            # If didn't get on a scoreboard or length is less than 4
            if worm_length - 2 < scoreboard[0][0] or worm_length - 2 < 4:
                if sound_on:
                    laugh.play()
            continue
        worm_locations, last_key = save_worm(box_x, box_y, worm_locations)

    # Generate new food if necessary
    if not food_set:
        if not (len(worm_locations) == playable_squares_y * playable_squares_x):
            food_square = generate_food(worm_locations)
            extra_food = randint(0, 9) == 5  # Food that gives +3 length
            food_set = True

    # Draw food on a screen
    if extra_food:
        pygame.draw.rect(gameDisplay, orange, food_square)
    else:
        pygame.draw.rect(gameDisplay, green, food_square)

    # If snake ate the food
    if food_square == [box_x, box_y, 20, 20] and not (len(worm_locations) == playable_squares_y * playable_squares_x):
        eatfood.play()
        if extra_food:
            worm_length += 3
        else:
            worm_length += 1
        food_set = False

    # If worm moved, remove the tail
    if len(worm_locations) > worm_length:
        worm_locations = worm_locations[1:]

    # Draw walls
    for j in range(len(walls)):
        pygame.draw.rect(gameDisplay, gray, walls[j])

    # Draw worm
    draw_worm(worm_locations)

    # current_score_text = pygame.font.SysFont("Verdana", 30).render(str(worm_length-2), True, black).convert_alpha()
    # gameDisplay.blit(current_score_text, (34, 24))

    pygame.display.update()
    clock.tick(40)

# MAIN_LOOP_END=========================================================================================================

pygame.quit()
