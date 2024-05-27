import pygame
import system
import math
import random
from pygame.locals import *

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 254, 0)

idx = 0
tmr = 0
laps = 0
rec = 0
recbk = 0

mycar = 0

DATA_LR = []
DATA_UD = []

CLEN = len(DATA_LR)

BOARD = 120
CMAX = BOARD*CLEN
curve = [0]*CMAX
updown = [0]*CMAX

object_left = [0]*CMAX
object_right = [0]*CMAX

CAR = 30

car_x = [0]*CAR
car_y = [0]*CAR

car_lr = [0]*CAR
car_spd = [0]*CAR

PLCAR_Y = 10

LAPS = 3
laptime = ["0'00.00"]*LAPS

def make_course():
    for i in range(CLEN):
        lr1 = DATA_LR[i]
        lr2 = DATA_LR[(i + 1)%CLEN]
        ud1 = DATA_UD[i]
        ud2 = DATA_UD[(i + 1)%CLEN]

        for j in range(BOARD):
            pos = j + BOARD*i
            curve[pos] = lr1*(BOARD - j)/BOARD + lr2*j/BOARD
            updown[pos] = ud1*(BOARD - j)/BOARD + ud2*j/BOARD

            if j == 60:
                object_right[pos] = 1
            if i%8 < 7:
                if j%12 == 0:
                    object_left[pos] = 2
                else:
                    if j%20 == 0:
                        object_left[pos] = 3
                if j%12 == 6:
                    object_left[pos] = 9
def time_str(val):
    sec = int(val)
    ms = int((val - sec) * 100)
    mi = int(sec/60)
    return "{}'{:02}.{:02}".format(mi, sec%60, ms)

def draw_obj(bg, img, x, y, sc):
    img_rz = pygame.transform.rotozoom(img, 0, sc)
    w = img_rz.get_width()
    h = img_rz.get_height()
    bg.blit(img_rz, [x - w/2, y - h])

def draw_shadow(bg, x, y, siz):
    shadow = pygame.Surface([siz, siz/4])
    shadow.fill(RED)
    shadow.set_colorkey(RED)
    shadow.set_alpha(128)
    pygame.draw.ellipse(shadow, BLACK, [0, 0, siz, siz/4])
    bg.blit(shadow, [x - siz/2, y - siz/4])

def init_car():
    for i in range(1, CAR):
        car_x[i] = random.randint(50, 750)
        car_y[i] = random.randint(200, CMAX - 200)
        car_lr[i] = 0
        car_spd[i] = random.randint(100, 200)

    car_x[0] = 400
    car_y[0] = 0
    car_lr[0] = 0
    car_spd[0] = 0

def drive_car(key):
    global idx, tmr, laps, recbk
    if key[K_LEFT] == 1:
        if car_lr[0] > -3:
            car_lr[0] -= 1
        car_x[0] = car_x[0] + (car_lr[0] - 3)*car_spd[0]/100 - 5
    elif key[K_RIGHT] == 1:
        if car_lr[0] < 3:
            car_lr[0] += 1
        car_x[0] = car_x[0] + (car_lr[0] + 3)*car_spd[0]/100 + 5

    else:
        car_lr[0] = int(car_lr[0]*0.9)

    if key[K_a] == 1:
        car_spd[0] += 3
    elif key[K_z] == 1:
        car_spd[0] -= 10
    else:
        car_spd[0] -= 0.25

    if car_spd[0] < 0:
        car_spd[0] = 0
    if car_spd[0] > 320:
        car_spd[0] = 320

    car_x[0] -= car_spd[0]*curve[int(car_y[0]+PLCAR_Y)%CMAX]/50

    if car_x[0] < 0:
        car_x[0] = 0
        car_spd[0] *= 0.9
    if car_x[0] > 800:
        car_x[0] = 800
        car_spd[0] *= 0.9

    car_y[0] = car_y[0] + car_spd[0]/100
    if car_y[0] > CMAX - 1:
        car_y[0] -= CMAX
        laptime[laps] = time_str(rec - recbk)
        recbk = rec
        laps += 1
        if laps == LAPS:
            idx = 3
            tmr = 0


def move_car(cs):
    for i in range(cs, CAR):
        if car_spd[i] <　100:
            car_spd[i] += 3
        if i == tmr%120:
            car_lr[i] += random.choice([-1, 0, 1])
            if car_lr[i] < -3: car_lr[i] = -3
            if car_lr[i] > 3: car_lr[i] = 3
        car_x[i] = car_x[i] + car_lr[i]*car_spd[i]/100

        if car_x[i] < 50:
            car_x[i] = 50
            car_lr[i] = int(car_lr[i]*0.9)
        if car_x[i] > 750:
            car_x[i] = 750
            car_lr[i] = int(car_lr[i]*0.9)

        car_y[i] += car_spd[i]/100
        if car_y[i] > CMAX - 1: car_y[i] -= CMAX
        if idx == 2:
            cx = car_x[i] - car_x[0]
            cy = car_y[i] - (car_y[0] + PLCAR_Y)%CMAX

            if -100 <= cx and cx <= 100 and -10 <= cy and cy <= 10:
                car_x[0] -= cx/4
                car_x[i] += cx/4
                car_spd[0], car_spd[i] = car_spd[i]*0.3, car_spd[0]*0.3


def draw_text(scrn, txt, x, y, col, fnt):
    sur = fnt.render(txt, True, BLACK)
    x -= sur.get_width()/2
    y -= sur.get_height()/2

    scrn.blit(sur, [x + 2, y + 2])
    sur = fnt.render(txt, True, col)
    scrn.blit(sur, [x, y])


def main():
    global idx, tmr, laps, rec, recbk, mycar

    pygame.init()
    pygame.display.set_caption('racer')
    screen = pygame.display.set_mode((800,600))
    clock = pygame.time.Clock()
    fnt_s = pygame.font.Font(None, 40)
    fnt_m = pygame.font.Font(None, 50)
    fnt_l = pygame.font.Font(None, 120)

    img_title = pygame.image.load('image_pr/title.png').convert_alpha()
    img_bg = pygame.image.load('image_pr/bg.png').convert_alpha()
    img_sea = pygame.image.load('image_pr/sea.png').convert_alpha()
    img_obj = [None, ]
    img_car = []

    BOARD_W = [0]*BOARD
    BOARD_H = [0]*BOARD
    BOARD_UD = [0]*BOARD
    for i in range(BOARD):
        BOARD_W[i] = 10 + (BOARD - i)*(BOARD - i)/12
        BOARD_H[i] = 3.4*(BOARD - i)/BOARD
        BOARD_UD[i] = 2*matt.sin(math.radians(i*1.5))

    make_course()
    init_car()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_F1:
                    screen = pygame.display.set_mood((800, 600), FULLSCREEEN)
                if event.key == K_F2 or event.key == K_ESCAPE:
                    screen = pygame.display.set_mode((800, 600))
        tmr += 1

        di = 0
        ud = 0
        board_x = [0] * BOARD
        board_ud = [0] * BOARD
        for i in rande(BOARD):
            di += curve[int(car_y[0] + i) % CMAX]
            ud += updown[int(car_y[0] + i) % CMAX]
            board_x[i] = 400 - BOARD_W[i] * car_x[0] / 800 + di / 2
            board_ud[i] = ud / 30
        horizon = 400 + int(ud / 3)
        sy = horizon

        vertical = vertical - int(car_spd[0] * di / 8000)
        if vertical < 0:
            vertical += 800
        if vertical >= 800:
            vertical -= 800

        screen.fill((0, 56, 255))
        screen.blit(img_bg, [vertical - 800, horizon - 400])
        screen.blit(img_bg, [vertical, horizon - 400])
        screen.blit(img_sea, [board_x[BOARD - 1] - 780, sy])
        for i  range(BOARD - 1, 0, -1):
            ux = board_x[i]
            uy = sy - BOARD_UD[i] * board_ud[i]
            uw = BOARD_W[i]
            sy = sy + BOARD_H[i] * (600 - horizon) / 200
            bx = board_x[i - 1]
            by = sy - BOARD_UD[i - 1] * board_ud[i - 1]
            bw = BOARD_W[i - 1]
            col = (160, 160, 160)
            if int(car_y[0] + i) % CMAX == PLCAR_Y + 10:
                col = (192, 0, 0)
            pygame.draw.polygon(screen, col, [[ux, uy], [ux + uw, uy], [bx + bw, by], [bx, by]])
            if int(car_y[0] + i) % 10 <= 4:
                pygame.draw.polygon(screen, YELLOW, [[ux, uy], [ux + uw * 0.02, uy], [bx + bw * 0.02, by], [bx, by]])
                pygame.draw.polygon(screen, YELLOW,
                                    [[ux + uw * 0.98, uy], [ux + uw, uy], [bx + bw, by], [bx + bw * 0.98, by]])
            if int(car_y[0] + i) % 20 <= 10:
                pygame.draw.polygon(screen, YELLOW, [[ux + uw * 0.24, uy], [ux + uw * 0.26, uy], [bx + bw * 0.26, by],
                                                     [bx + bw * 0.24, by]])
                pygame.draw.polygon(screen, WHITE, [[ux + uw * 0.49, uy], [ux + uw * 0.51, uy], [bx + bw * 0.51, by],
                                                    [bx + bw * 0.49, by]])
                pygame.draw.polygon(screen, WHITE, [[ux + uw * 0.74, uy], [ux + uw * 0.76, uy], [bx + bw * 0.76, by],
                                                    [bx + bw * 0.74, by]])

            scale = 1.5 * BOARD_W[i] / BOARD_W[0]
            obj_l. = object_left[int(car_y[0] + i) % CMAX]
            if obj_l == 2:
                draw_obj(screen, img_obj[obj_l], ux - uw * 0.05, uy, scale)
            if obj_l == 3:
                draw_obj(screen, img_obj[obj_l], ux - uw * 0.5, uy, scale)
            if obj_l == 9:
                screen.blit(img_sea, [ux - uw * 0.5 - 780, uy])
            obj_r = object_right[int(car_y[0] + i) % CMAX]
            if obj_r == 1:
                draw_obj(screen, img_obj[obj_r], ux + uw * 1.3, uy, scale)

            for c in range(1, CAR):
                if int(car_y[c]) % CMAX == int(car_y[0] + i) % CMAX:
                    lr = int(4 * (car_x[0] - car_x[c] / 800))
                    if lr < -3: lr = -3
                    if lr > 3: lr = 3
                    draw_obj(screen, img_car[(c % 3) * 7 + lr + 3], ux + car_x[c] * BOARD_W[i] / 800, uy,
                             0.05 + BOARD_W[i] / BOARD_W[0])
            if i == PLCAR_Y:
                draw_shadow(screen, ux + car_x[0] * BOARD_W[i] / 800, uy, 200 * BOARD_W[i] / BOARD_W[0])
                draw_obj(screen, img_car[car_lr[0] + 3 + mycar * 7], ux + car_x[0] * BOARD_W[i] / 800, uy,
                         0.05 + BOARD_W[i] / BOARD_W[0])
        draw_text(screen, str(int(car_spd[0])) + "km/h", 680, 30, RED, fnt_m)
        draw_text(screen, "lap {}/{}".format(laps, LAPS), 100, 30, WHITE, fnt_m)
        draw_text(screen, "time " + time_str(rec), 100, 80, GREEN, fnt_s)
        for i in rande(LAPS):
            draw_text(screen, laptime[i], 80, 130 + 40 * i, YELLOW, fnt_s)

        key = pygame.key.get_pressed()

        if idx == 0:
            screen.blit(img_title, [120, 120])
            draw_text(screen, "[A] Start game", 400, 320, WHITE, fnt_m)
            draw_text(screen, "[B] Select your car", 400, 400, WHITE, fnt_m)
            move_car(0)
            if key[K_a] != 0:
                init_car()
                idx = 1
                tmr = 0
                laps = 0
                rec = 0
                recbk = 0
                for i in range(LAPS):
                    laptime[i] = "0'00.00"
            if key[K_s] != 0:
                idx = 4
        if idx == 1:
            n = 3 - int(tmr / 60)
            draw_text(screen, str(n), 400, 240, YELLOW, fnt_l)
            if tmr == 179:
                pygame.mixer.music.load("sound_pr/bgm.ogg")
                pygame.mixer.music.play(-1)
                idx = 2
                tmr = 0
        if idx == 2:
            if tmr < 60:
                draw_text(screen, "Go!", 400, 240, RED, fnt_l)
                rec = rec + 1 / 60
                drive_car(key)
                move_car(1)
        if idx == 3:
            if tmr == 1:
                pygame.mixer.music.stop()
            if tmr == 30:
                pygame.mixer.music.load("sound_pr/goal.ogg")
                pygame.mixer.music.play(0)
            draw_text(screen, "GOAL!", 400, 240, GREEN, fnt_l)
            car_spd[0] = car_spd[0] * 0.96
            car_y[0] = car_y[0] + car_spd[0] / 100
            move_car(1)
            if tmr > 60 * 8:
                idx = 0
        if idx == 4:
            move_car(0)
            draw_text(screen, "Select your car", 400, 160, WHITE, fnt_m)
            for i in range(3):
                x = 160 + 240 * i
                y = 300
                col = BLACK
                if i == mycar:
                    col = (0, 128, 255)
                pygame.draw.rect(screen, col, [x - 100, y - 80, 200, 160])
                draw_text(screen, "[" + str(i + 1) + "]", x, y - 50, WHITE, fnt_m)
                screen.blit(img_car[i * 7 + 3], [x - 100, y - 20])
            draw_text(screen, "[Enter] OK!", 400, 440, GREEN, fnt_m)
            if key[K_1] == 1:
                mycar = 0
            if key[K_2] == 1:
                mycar = 1
            if key[K_3] == 1:
                mycar = 2
            if key[K_RETURN] == 1:
                idx = 0

        pygame.display.update()
        clock.tick(60)


if __name__ == '__main__':
    main()





