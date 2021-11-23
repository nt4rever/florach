from scipy import interpolate
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import time 
import pygame
import random
from random import randint
from sys import exit
pygame.init()

# 5 levels [score , time]
levels = [[20, 30], [40, 40], [60, 50], [80, 60], [100, 70]]
# level mac dinh
level = 1
# bien diem thoi gian
seconds = 0
# thoi gian bat dau
time_start = 0

# tao chuyen dong theo chieu doc, chuyen dong gon song cho fish
x_ax = 50
patterns_num = 5   # Number of Available patterns (integer)

# khoang cach chuyen dong theo chieu doc (5px)
vertical_displacement = 10
# toc do dich chuyen theo chieu ngang (mac dinh 0,2)
x_displacement = 0.2

# diem
score = 0
# kich co ca cua minh
big_fish_size = 2.2

# mang texture dc load tu photos
texture = ()
photos = ['Fishleft1.png', 'Fishright1.png', 'Fishleft2.png', 'Fishright2.png', 'Fishleft3.png', 'Fishright3.png', 'Fishleft4.png', 'Fishright4.png', 'Fishleft5.png', 'Fishright5.png', 'Fishleft6.png', 'Fishright6.png',
          'Fishleft7.png', 'Fishright7.png', 'Fishleft8.png', 'Fishright8.png', 'Fishleft9.png', 'Fishright9.png', 'Fishleft10.png', 'Fishright10.png', 'Fishleft11.png', 'Fishright11.png', 'bgaov.png', 'menuflo.jpg']

# huong chuyen dong nhan vat, vi tri nhan vat (con ca cua minh)
mouse_dir = 1
current_x = 200
current_y = 200

# random vi tri y hien thi cua con ca
def random_offset():
    return randint(vertical_displacement+10, 600-vertical_displacement-10)

# list cac vi tri gon song [-50, 0, 50, 100, ..., 650, 700]
x_points = [i for i in range(-50, 750, x_ax)]
num_points = len(x_points)

# A[0_X_pos, 1_Y_pos, 2_Scale, 3_dir_X, 4_pattern_num, 5_y_offset, 6 Shape ]
# ma tran 7 vecto, 1 vecto tuong ung voi 1 con ca
A = [[0, 120, 1.5, 1, 0, random_offset(), 1],
     [0, 240, 3, 1, 1, random_offset(), 3],
     [0, 360, 1.5, 1, 2, random_offset(), 5],
     [0, 480, 3, 1, 3, random_offset(), 7],
     [0, 600, 1.5, 1, 4, random_offset(), 9],
     [600, 120, 3, -1, 4, random_offset(), 0],
     [600, 240, 1.5, -1, 3, random_offset(), 2],
     [600, 360, 3, -1, 2, random_offset(), 4],
     [600, 480, 1.5, -1, 1, random_offset(), 6],
     [600, 600, 3, -1, 0, random_offset(), 8]]
count = len(A)
paths = []

# trang thai tro choi (playing/lost)
lost_flag = 0

def generate_patterns():
    global paths, num_points, patterns_num, vertical_displacement
    paths = []
    for j in range(patterns_num):
        new_path = []
        for i in range(num_points):
            new_path.append(randint(300-vertical_displacement,
                            300+vertical_displacement))
        paths.append(interpolate.splrep(x_points, new_path))

# tinh vi tri y de tao gon song
def f(i):
    global paths, A
    if A[i][3] == 1:
        f_x = interpolate.splev(A[i][0], paths[A[i][4]])
    else:
        f_x = 600 - interpolate.splev(A[i][0], paths[A[i][4]])
    # doi huong chuyen dong khi di het man hinh, doi hinh dang con ca (trai<->phai)
    if A[i][0] > 650:
        A[i][3] = -A[i][3]
        A[i][6] = A[i][6]-1
    elif A[i][0] < -50:
        A[i][3] = -A[i][3]
        A[i][6] = A[i][6]+1
    return f_x + A[i][5] - 300

# hien thi text len man hinh
def drawText(string, x, y):
    glLineWidth(2)
    glColor(0, 0, 0)
    glLoadIdentity()
    glTranslate(x, y, 0)
    glRotate(180, 1, 0, 0)
    glScale(.16, .16, 1)
    string = string.encode()  # conversion from Unicode string to byte string
    for c in string:
        glutStrokeCharacter(GLUT_STROKE_ROMAN, c)

# them 1 con ca
def add_small_fish():
    global count, A, level
    count += 1
    # chon vi tri x bat dau -50 hoac 650
    new_rand_x = random.choice([-50, 650])
    new_rand_pattern = randint(0, patterns_num - 1)
    # neu diem so <30 -> size ca 1.5 | >30 size 1.5 hoac 3
    if score <= 30:
        scale = 1.5
    else:
        scale = randint(2,level+3)

    # neu x = -50, ben trai -> hinh dang ca di ve ben phai, huong chuyen dong = 1
    if new_rand_x < 0:
        new_fish_shape = random.choice([1, 3, 5, 7, 9, 11, 13, 15, 17, 19])
        direction = 1
    # neu x = 650, ben phai -> hinh dang ca di ve ben trai, huong chuyen dong = -1
    else:
        new_fish_shape = random.choice([0, 2, 4, 6, 8, 10, 12, 14, 16, 18])
        direction = -1
    # them ca vao list A
    A.append(list((new_rand_x, 0, scale, direction,
             new_rand_pattern, random_offset(), new_fish_shape)))

# xoa 1 con ca trong mang A
def remove_small_fish(i):
    global A, count
    global A
    del A[i]
    count -= 1

# gan co trang thai thua
def remove_big_fish_lost():
    global lost_flag
    lost_flag = 1

# tang diem
def increase_Score():
    global score
    score += 1

# hieu ung am thanh
def eating_soound():
    s_file = pygame.mixer.Sound("audio/eating.wav")
    s_file.play()

def game_over_sound():
    s_file = pygame.mixer.Sound("audio/shutdown.ogg")
    s_file.play()

def mega_kill():
    s_file = pygame.mixer.Sound("audio/megakill.ogg")
    s_file.play()

def fb():
    s_file = pygame.mixer.Sound("audio/fb.mp3")
    s_file.play()

# ham tinh ket qua khi va cham, khoang cach toa do x,y < 30px dc tinh la co va cham
def collsion(i):
    global current_x, current_y, score, count, patterns_num, big_fish_size, seconds
    x = A[i][0]
    y = A[i][1]
    if abs(current_x - x) < 30 and abs(current_y-y) < 30 and A[i][2] > big_fish_size:
        remove_big_fish_lost()
        game_over_sound()

    elif abs(current_x - x) < 30 and abs(current_y-y) < 30 and A[i][2] < big_fish_size:
        remove_small_fish(i)
        increase_Score()
        if score %5==0 and score>0:
            mega_kill()
        if score==1:
            fb()
        add_small_fish()
        eating_soound()

# load texture tu anh
def load_texture():
    global texture, photos
    texture = glGenTextures(24)
    for i in range(24):
        imgload = pygame.image.load("photos/"+photos[i])
        img = pygame.image.tostring(imgload, "RGBA", 1)
        width = imgload.get_width()
        height = imgload.get_height()
        # Set this image in images array
        glBindTexture(GL_TEXTURE_2D, texture[i])
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexImage2D(GL_TEXTURE_2D, 0, 4, width, height,
                     0, GL_RGBA, GL_UNSIGNED_BYTE, img)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture[i])

# khoi tao tro cho
def init():
    # s_file = pygame.mixer.Sound("audio/feeding-frenzy.wav")
    pygame.mixer.music.load('audio/audiobg.wav')
    pygame.mixer.music.play(-1)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, 600, 600, 0, 0, 600)
    load_texture()
    glClearColor(1, 1, 1, .5)
    generate_patterns()

#
def start_game():
    global lost_flag, A, score, big_fish_size, score, time_start, count
    A = [[0, 120, 1.5, 1, 0, random_offset(), 1],
         [0, 240, 3, 1, 1, random_offset(), 3],
         [0, 360, 1.5, 1, 2, random_offset(), 5],
         [0, 480, 3, 1, 3, random_offset(), 7],
         [0, 600, 1.5, 1, 4, random_offset(), 9],
         [600, 120, 3, -1, 4, random_offset(), 0],
         [600, 240, 1.5, -1, 3, random_offset(), 2],
         [600, 360, 3, -1, 2, random_offset(), 4],
         [600, 480, 1.5, -1, 1, random_offset(), 6],
         [600, 600, 3, -1, 0, random_offset(), 8]]
    count = len(A)
    score = 0
    big_fish_size = 2.2
    lost_flag = 0
    time_start = time.time()

# ham lay thoi gian bat dau
def start_time():
    global time_start
    time_start = time.time()

# hien thi menu
def menu():
    global texture
    glBindTexture(GL_TEXTURE_2D, texture[-1])
    glColor(1, 1, 1)
    glBegin(GL_QUADS)
    glTexCoord(1, 1)
    glVertex3f(0, 0, 0)
    glTexCoord(0, 1)
    glVertex3f(600, 0, 0)
    glTexCoord(0, 0)
    glVertex3f(600, 600, 0)
    glTexCoord(1, 0)
    glVertex3f(0, 600, 0)
    glEnd()
    glFlush()

def keyboard(key, x, y):
    global level
    if key == b"x":
        exit("Exit!")
    # bam a de bat dau choi
    if key == b"a":
        start_game()
        glutIdleFunc(main_scene)
    if key == b"r":
        start_game()
        glutIdleFunc(main_scene)

# vong lap main_scene
def main_scene():
    global texture, current_x, current_y, count, big_fish_size, A, lost_flag, mouse_dir, score, levels, level
    # neu thua thi tro ve man hinh menu
    if lost_flag == 1:
        glutIdleFunc(menu)
    # neu diem >= diem max cua level/2 thi tang size ca cua minh len
    size_t = (score+1)/levels[level-1][1]
    big_fish_size = 2 + size_t*(level+1)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glClear(GL_COLOR_BUFFER_BIT)  # | GL_DEPTH_BUFFER_BIT)
    if lost_flag != 1:  # play the game
        glBindTexture(GL_TEXTURE_2D, texture[22])  # background
        glBegin(GL_QUADS)
        glTexCoord(0, 0)
        glVertex3f(600, 600, 0)
        glTexCoord(0, 1)
        glVertex3f(600, 0, 0)
        glTexCoord(1, 1)
        glVertex3f(0, 0, 0)
        glTexCoord(1, 0)
        glVertex3f(0, 600, 0)
        glEnd()

        # Texture Added
        string = "Score: " + str(score)
        drawText(string, 20, 120)
        glLoadIdentity()

        # Texture Added
        string = "Timer: " + str(levels[level-1][1]-seconds)
        drawText(string, 20, 180)
        glLoadIdentity()

        # Texture Added
        string = "Level: " + str(level)
        drawText(string, 20, 150)
        glLoadIdentity()

        glTranslate(current_x, current_y, 0)
        glColor4f(1, 1, 1, 1)
        if mouse_dir == 1:
            glBindTexture(GL_TEXTURE_2D, texture[21])
        else:
            glBindTexture(GL_TEXTURE_2D, texture[20])

        glBegin(GL_QUADS)
        glTexCoord(0, 0)
        glVertex3f(-10 * big_fish_size, 10 * big_fish_size, 0)
        glTexCoord(0, 1)
        glVertex3f(-10 * big_fish_size, -10 * big_fish_size, 0)
        glTexCoord(1, 1)
        glVertex3f(10 * big_fish_size, -10 * big_fish_size, 0)
        glTexCoord(1, 0)
        glVertex3f(10 * big_fish_size, 10 * big_fish_size, 0)
        glEnd()
        glLoadIdentity()

    if lost_flag != 1:
        for i in range(count):
            glLoadIdentity()
            A[i][1] = f(i)
            glTranslate(A[i][0], A[i][1], 0)
            # x ban dau = 100, huong 1, toc do x = 2=> x moi = 100+=1*2
            A[i][0] += (A[i][3] * x_displacement)
            if A[i][3] == 1:
                glBindTexture(GL_TEXTURE_2D, texture[A[i][6]])
            if A[i][3] == -1:
                glBindTexture(GL_TEXTURE_2D, texture[A[i][6]])
            glBegin(GL_QUADS)
            glTexCoord(0, 0)
            glVertex3f(-10 * A[i][2], 10 * A[i][2], 0)
            glTexCoord(0, 1)
            glVertex3f(-10*A[i][2], -10*A[i][2], 0)
            glTexCoord(1, 1)
            glVertex3f(10 * A[i][2], -10 * A[i][2], 0)
            glTexCoord(1, 0)
            glVertex3f(10*A[i][2], 10 * A[i][2], 0)
            glEnd()
            collsion(i)
    glFlush()
    # Check for the Level

    if score >= levels[level-1][0]:    # Only 5 levels then get Error
        next_level(level)
        glutIdleFunc(main_scene)

    # continue timer
    game_timer()

def game_timer():
    global seconds, time_start, levels, level, lost_flag
    seconds = int(time.time() - time_start)
    if seconds >= levels[level-1][1]:
        lost_flag = 1

def next_level(i):
    global x_displacement, patterns_num, vertical_displacement, level, levels
    x_displacement = 0.2 + (i*0.05)
    vertical_displacement = 5 + (i*2)
    patterns_num += 5 + (i*1)
    generate_patterns()
    level += 1
    if level > len(levels):
        patterns_num = 5
        vertical_displacement = 10
        level=1
        x_displacement = 0.2
        generate_patterns()
        glutIdleFunc(menu)
    else:
        start_game()

def mouse(new_x, new_y):
    global current_x, current_y, mouse_dir
    if new_x > current_x:
        mouse_dir = 1
    else:
        mouse_dir = -1
    current_x = new_x
    current_y = new_y

def main():
    glutInit()                           
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGBA)   
    glutInitWindowSize(600, 600)
    glutCreateWindow("Feeding Frenzy")
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)  
    glEnable(GL_BLEND)
    init()
    glutKeyboardFunc(keyboard)
    glutIdleFunc(menu)
    glutPassiveMotionFunc(mouse)
    glutDisplayFunc(menu)
    glutMainLoop()

main()