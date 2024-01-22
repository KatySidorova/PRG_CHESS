import pygame
import sys
from data.classes.Board import Board
from data.classes.Particle import Particle, all_sprites
import datetime
import sqlite3
import random

pygame.init()

WINDOW_SIZE = (600, 600)
screen = pygame.display.set_mode(WINDOW_SIZE)

board = Board(WINDOW_SIZE[0], WINDOW_SIZE[1])


def draw(display):
    display.fill('white')
    board.draw(display)
    pygame.display.update()


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["Шахматы", "Выполнили:", "- Сидорова Екатерина", "- Анисимова Кристина"]
    img_path = 'data/imgs/fon.jpg'
    fon = pygame.transform.scale(pygame.image.load(img_path), WINDOW_SIZE)
    screen.blit((fon), (0, 0))
    font = pygame.font.Font(None, 27)
    text_coord = 10
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()


def win_screen(res_game, name_tab, dlit):
    def create_particles(position):
        # количество создаваемых частиц
        particle_count = 1
        # возможные скорости
        numbers = range(-5, 6)
        for _ in range(particle_count):
            Particle(position, random.choice(numbers), random.choice(numbers))

    fon = pygame.transform.scale(pygame.image.load('data/imgs/fon.jpg'), WINDOW_SIZE)

    pygame.font.init()
    my_color = (255, 255, 255)
    my_font = pygame.font.Font(None, 25)
    text0 = my_font.render("Игра закончена", False, my_color)
    text1 = my_font.render(res_game, False, my_color)
    text2 = my_font.render("Ходы записаны в таблице " + name_tab, False, my_color)
    text3 = my_font.render(dlit, False, my_color)

    clock = pygame.time.Clock()

    while True:
        x = random.randint(10, 590)
        y = random.randint(10, 590)
        create_particles((x, y))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

        all_sprites.update()
        screen.blit((fon), (0, 0))
        screen.blit(text0, (20, 20))
        screen.blit(text1, (20, 50))
        screen.blit(text2, (20, 80))
        screen.blit(text3, (20, 110))
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(50)


def add_to_bd(name_tab, txt):
    try:
        sql_text = "insert into " + name_tab + " (id, move) values(?,?)"
        cur.execute(sql_text, (-1, txt,))
        con.commit()
    except Exception as error:
        print(error)


def stat_game(d1, d2):
    dlit = (d2 - d1).total_seconds()
    m = round(dlit // 60, 0)
    game_dlit = f'Игра длилась {m} минут, {round(dlit - m * 60, 2)} секунд'
    print(game_dlit)
    return game_dlit


if __name__ == '__main__':
    name_tab = 'tab_' + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    print(name_tab)

    # Подключение к БД
    file_name = 'chess.sqlite'
    con = sqlite3.connect(file_name)

    # Создание курсора
    cur = con.cursor()

    # Создание таблицы
    sql_text = "CREATE TABLE IF NOT EXISTS " + name_tab + "(id integer, move text)"
    cur.execute(sql_text)
    con.commit()

    pygame.display.set_caption('Шахматы (IT Cube)')
    running = True

    start_screen()
    dt1 = datetime.datetime.now()
    print(f'Начало игры: {dt1}')

    while running:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                itog = 'Игра прервана!'
                print(itog)
                add_to_bd(name_tab, itog)
                con.close()
                running = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    board.handle_click(mx, my, cur, con, name_tab)
        if board.is_in_checkmate('black'):
            itog = 'Белые поставили МАТ!'
            print(itog)

            dt2 = datetime.datetime.now()
            print(f'Конец игры: {dt2}')
            game_dlit = stat_game(dt1, dt2)

            add_to_bd(name_tab, itog)
            con.close()

            win_screen(itog, name_tab, game_dlit)
            running = False

        elif board.is_in_checkmate('white'):
            itog = 'Черные поставили МАТ!'
            print(itog)

            dt2 = datetime.datetime.now()
            print(f'Конец игры: {dt2}')
            game_dlit = stat_game(dt1, dt2)

            add_to_bd(name_tab, itog)
            con.close()

            win_screen(itog, name_tab, game_dlit)
            running = False

        draw(screen)
