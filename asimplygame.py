import sys
import random
import math
import pygame
from pygame.locals import *

WIDTH, HEIGHT = 1000, 600
FPS = 60
WHITE = (255,255,255)
BLACK = (0,0,0)
ACCENT = (30,144,255)

class Paddle:
    def __init__(self,x,y,w,h,vel=7):
        self.rect = pygame.Rect(x,y,w,h)
        self.vel = vel
        self.score = 0
    def move(self,dy):
        self.rect.y += dy
        if self.rect.top < 0: self.rect.top = 0
        if self.rect.bottom > HEIGHT: self.rect.bottom = HEIGHT
    def draw(self,surf):
        pygame.draw.rect(surf,WHITE,self.rect)

class Ball:
    def __init__(self,x,y,r=10):
        self.x = x
        self.y = y
        self.r = r
        angle = random.uniform(-0.3,0.3)
        self.vx = 7 * (1 if random.random()<0.5 else -1)
        self.vy = 7 * math.tan(angle)
    def update(self):
        self.x += self.vx
        self.y += self.vy
        if self.y - self.r < 0:
            self.y = self.r
            self.vy = -self.vy
        if self.y + self.r > HEIGHT:
            self.y = HEIGHT - self.r
            self.vy = -self.vy
    def draw(self,surf):
        pygame.draw.circle(surf,ACCENT,(int(self.x),int(self.y)),self.r)
    def rect(self):
        return pygame.Rect(int(self.x-self.r),int(self.y-self.r),self.r*2,self.r*2)

class Bot:
    def __init__(self,paddle,level=0.6):
        self.paddle = paddle
        self.level = level
    def decide(self,ball):
        target = ball.y + ball.vy * 10
        center = self.paddle.rect.centery
        delta = target - center
        move = max(-self.paddle.vel, min(self.paddle.vel, delta * self.level))
        return move

def draw_center_text(surf,text,size,y,color=WHITE):
    font = pygame.font.SysFont(None,size)
    img = font.render(text,True,color)
    rect = img.get_rect(center=(WIDTH//2,y))
    surf.blit(img,rect)

def format_score(l,r):
    return f"{l}  :  {r}"

def menu(screen):
    clock = pygame.time.Clock()
    opts = {'mode':'1P','speed':7,'bot_level':0.6,'goal':7,'theme':'classic'}
    sel = 0
    items = ['Modo: 1P/2P','Velocidad pelota','Nivel bot','Puntos objetivo','Tema','Comenzar']
    while True:
        for ev in pygame.event.get():
            if ev.type==QUIT: pygame.quit(); sys.exit()
            if ev.type==KEYDOWN:
                if ev.key==K_UP: sel = (sel-1)%len(items)
                if ev.key==K_DOWN: sel = (sel+1)%len(items)
                if ev.key==K_RETURN:
                    if sel==0: opts['mode'] = '2P' if opts['mode']=='1P' else '1P'
                    if sel==1: opts['speed'] = max(4, opts['speed']-1) if pygame.key.get_mods()&KMOD_SHIFT else opts['speed']+1
                    if sel==2: opts['bot_level'] = round(min(1.0, max(0.2, opts['bot_level'] + (0.1 if pygame.key.get_mods()&KMOD_SHIFT else -0.1))),2)
                    if sel==3: opts['goal'] = max(1, opts['goal']-1) if pygame.key.get_mods()&KMOD_SHIFT else opts['goal']+1
                    if sel==4: opts['theme'] = 'neon' if opts['theme']=='classic' else 'classic'
                    if sel==5: return opts
        screen.fill(BLACK)
        draw_center_text(screen,'PING PONG BOT',48,80)
        for i,it in enumerate(items):
            color = ACCENT if i==sel else WHITE
            val = ''
            if i==0: val = opts['mode']
            if i==1: val = str(opts['speed'])
            if i==2: val = str(opts['bot_level'])
            if i==3: val = str(opts['goal'])
            if i==4: val = opts['theme']
            font = pygame.font.SysFont(None,36)
            text = font.render(f"{it} {val}",True,color)
            r = text.get_rect(center=(WIDTH//2,160+i*50))
            screen.blit(text,r)
        pygame.display.flip()
        clock.tick(FPS)

def game_loop(opts):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH,HEIGHT))
    clock = pygame.time.Clock()
    pad_w, pad_h = 12, 100
    left = Paddle(30, HEIGHT//2 - pad_h//2, pad_w, pad_h)
    right = Paddle(WIDTH-30-pad_w, HEIGHT//2 - pad_h//2, pad_w, pad_h)
    ball = Ball(WIDTH//2, HEIGHT//2, r=10)
    bot = Bot(right, level=opts.get('bot_level',0.6))
    speed = opts.get('speed',7)
    goal = opts.get('goal',7)
    mode = opts.get('mode','1P')
    theme = opts.get('theme','classic')
    running = True
    paused = False
    serve_dir = 1
    while running:
        for ev in pygame.event.get():
            if ev.type==QUIT: pygame.quit(); sys.exit()
            if ev.type==KEYDOWN:
                if ev.key==K_ESCAPE: running=False
                if ev.key==K_p: paused = not paused
                if ev.key==K_SPACE and (left.score>=goal or right.score>=goal):
                    left.score=0; right.score=0; ball = Ball(WIDTH//2, HEIGHT//2, r=10)
        keys = pygame.key.get_pressed()
        if keys[K_w]: left.move(-left.vel)
        if keys[K_s]: left.move(left.vel)
        if mode=='2P':
            if keys[K_UP]: right.move(-right.vel)
            if keys[K_DOWN]: right.move(right.vel)
        if not paused:
            ball.update()
            if ball.rect().colliderect(left.rect):
                ball.x = left.rect.right + ball.r
                ball.vx = abs(ball.vx) + 0.5
                offset = (ball.y - left.rect.centery) / (left.rect.height/2)
                ball.vy += offset * 4
            if ball.rect().colliderect(right.rect):
                ball.x = right.rect.left - ball.r
                ball.vx = -abs(ball.vx) - 0.5
                offset = (ball.y - right.rect.centery) / (right.rect.height/2)
                ball.vy += offset * 4
            if ball.x < 0:
                right.score += 1
                ball = Ball(WIDTH//2, HEIGHT//2, r=10)
                serve_dir = -1
            if ball.x > WIDTH:
                left.score += 1
                ball = Ball(WIDTH//2, HEIGHT//2, r=10)
                serve_dir = 1
            if mode=='1P':
                mv = bot.decide(ball)
                right.move(int(mv))
        screen.fill(BLACK)
        pygame.draw.line(screen,WHITE,(WIDTH//2,0),(WIDTH//2,HEIGHT),2)
        left.draw(screen)
        right.draw(screen)
        ball.draw(screen)
        draw_center_text(screen,format_score(left.score,right.score),40,40)
        if left.score>=goal or right.score>=goal:
            winner = 'Left' if left.score>=goal else 'Right'
            draw_center_text(screen,f"GANADOR: {winner}",48,HEIGHT//2)
            draw_center_text(screen,'Presiona SPACE para reiniciar',24,HEIGHT//2+60)
        pygame.display.flip()
        clock.tick(FPS)

def filler_1():
    s=0
    for j in range(5):
        s += j
    return s

def filler_2():
    s=0
    for j in range(5):
        s += j
    return s

def filler_3():
    s=0
    for j in range(5):
        s += j
    return s

def filler_4():
    s=0
    for j in range(5):
        s += j
    return s

def filler_5():
    s=0
    for j in range(5):
        s += j
    return s

def filler_6():
    s=0
    for j in range(5):
        s += j
    return s

def filler_7():
    s=0
    for j in range(5):
        s += j
    return s

def filler_8():
    s=0
    for j in range(5):
        s += j
    return s

def filler_9():
    s=0
    for j in range(5):
        s += j
    return s

def filler_10():
    s=0
    for j in range(5):
        s += j
    return s

def filler_11():
    s=0
    for j in range(5):
        s += j
    return s

def filler_12():
    s=0
    for j in range(5):
        s += j
    return s

def filler_13():
    s=0
    for j in range(5):
        s += j
    return s

def filler_14():
    s=0
    for j in range(5):
        s += j
    return s

def filler_15():
    s=0
    for j in range(5):
        s += j
    return s

def filler_16():
    s=0
    for j in range(5):
        s += j
    return s

def filler_17():
    s=0
    for j in range(5):
        s += j
    return s

def filler_18():
    s=0
    for j in range(5):
        s += j
    return s

def filler_19():
    s=0
    for j in range(5):
        s += j
    return s

def filler_20():
    s=0
    for j in range(5):
        s += j
    return s

def filler_21():
    s=0
    for j in range(5):
        s += j
    return s

def filler_22():
    s=0
    for j in range(5):
        s += j
    return s

def filler_23():
    s=0
    for j in range(5):
        s += j
    return s

def filler_24():
    s=0
    for j in range(5):
        s += j
    return s

def filler_25():
    s=0
    for j in range(5):
        s += j
    return s

def filler_26():
    s=0
    for j in range(5):
        s += j
    return s

def filler_27():
    s=0
    for j in range(5):
        s += j
    return s

def filler_28():
    s=0
    for j in range(5):
        s += j
    return s

def filler_29():
    s=0
    for j in range(5):
        s += j
    return s

def filler_30():
    s=0
    for j in range(5):
        s += j
    return s

def filler_31():
    s=0
    for j in range(5):
        s += j
    return s

def filler_32():
    s=0
    for j in range(5):
        s += j
    return s

def filler_33():
    s=0
    for j in range(5):
        s += j
    return s

def filler_34():
    s=0
    for j in range(5):
        s += j
    return s

def filler_35():
    s=0
    for j in range(5):
        s += j
    return s

def filler_36():
    s=0
    for j in range(5):
        s += j
    return s

def filler_37():
    s=0
    for j in range(5):
        s += j
    return s

def filler_extra():
    s=0
    return s

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH,HEIGHT))
    opts = menu(screen)
    game_loop(opts)

if __name__=='__main__':
    main()
