import math
import pygame
import pid
from utils import scale_image, blit_rotate_center, blit_text_center


pygame.init()
pygame.font.init()

clock = pygame.time.Clock()
debug = False

wind = False
steer_bias = True

FrameHeight = 400
FrameWidth = 1200

pygame.display.set_caption("PID controller simulation")
screen = pygame.display.set_mode((FrameWidth, FrameHeight))

bg = pygame.image.load("background_small.png").convert()
RED_CAR = scale_image(pygame.image.load("imgs/red-car_small.png"), 1.0)

MAIN_FONT = pygame.font.SysFont("courier", 35)


def draw(win, player_car, scroll):

    i = 0
    while(i < tiles):
        screen.blit(bg, (bg.get_width()*i + scroll, 0))
        i += 1

    # RESET THE SCROLL FRAME
    if abs(scroll) > bg.get_width():
        scroll = 0

    if debug:
        level_text = MAIN_FONT.render(
            f"CTE {player_car.y - 266}", 1, (255, 255, 255))
        win.blit(level_text, (10, FrameHeight - level_text.get_height() - 70))

        steer_text = MAIN_FONT.render(
            f"Steering angle: {player_car.steering_angle}", 1, (255, 255, 255))
        win.blit(steer_text, (10, FrameHeight - steer_text.get_height() - 40))

        vel_text = MAIN_FONT.render(
            f"Vel: {round(player_car.vel, 1)} px/s", 1, (255, 255, 255))
        win.blit(vel_text, (10, FrameHeight - vel_text.get_height() - 10))
        print(player_car.x)


    player_car.draw(win)
    pygame.display.update()

    return scroll


def move_player(player_car):

    keys = pygame.key.get_pressed()
    moved = False
    prev_CTE = player_car.prev_y - 266
    current_CTE = player_car.y - 266
    # print(f"CTE = {current_CTE}")

    player_car.steering_angle = controller.process(prev_CTE, current_CTE)

    if steer_bias:
        player_car.steering_angle += .3

    player_car.rotate()

    if debug:
        if keys[pygame.K_w]:
            moved = True
            player_car.move_forward()
        if keys[pygame.K_s]:
            moved = True
            player_car.move_backward()
        if not moved:
            player_car.reduce_speed()

    if not debug:
        player_car.move_forward()



class AbstractCar:
    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.max_steering_angle = 4.0
        self.steering_angle = 0.0
        self.angle = 220
        self.x, self.y = self.START_POS
        self.prev_x, self.prev_y = self.START_POS
        self.acceleration = 0.1

    def rotate(self):
        if self.steering_angle > self.max_steering_angle:
            self.steering_angle = self.max_steering_angle
        if self.steering_angle < -self.max_steering_angle:
            self.steering_angle = -self.max_steering_angle

        # test for velocity-related steering speed, uncomment for original
        self.angle -= (self.vel / self.max_vel) * self.steering_angle
        

    def draw(self, win):
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()

    def move_backward(self):
        self.vel = max(self.vel - self.acceleration, -self.max_vel/2)
        self.move()

    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        self.prev_x = self.x
        self.prev_y = self.y
        self.y -= vertical
        self.x -= horizontal

        if wind:
            self.y -= .2

    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(car_mask, offset)
        return poi

    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 0
        self.vel = 0


class PlayerCar(AbstractCar):
    IMG = RED_CAR
    START_POS = (45, 200)

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()

    def bounce(self):
        self.vel = -self.vel
        self.move()


player_car = PlayerCar(1, 4)


tiles = math.ceil(FrameWidth / bg.get_width()) + 1

def drive():

    sum_abs_CTE = 0
    scroll = 0
    count_timer= 0  # count 'timer' for 'stuck in loop' detection

    while 1:
        clock.tick(12000)

        count_timer += 1

        # scroll = draw(screen, player_car, scroll)

        move_player(player_car)
        
        sum_abs_CTE += abs(player_car.y - 266)

        if player_car.x > 1200:
            return sum_abs_CTE

        elif player_car.x < 0 or player_car.y < 0 or player_car.y > 400 or count_timer > 1500:
            return 1000000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()


p = [0.16, 7, 0.001]       # initial parameter values
dp = [0.001,0.001,0.001]    # initial parameter deltas


controller = pid.PIDcontroller(p)

best_goodness = drive()     # initial value best performance variable

print('fG', best_goodness) 

threshhold = 0.001

while sum(dp) > threshhold:
    for i in range(len(p)):
        player_car = PlayerCar(1, 4)
        p[i] += dp[i] 
        controller = pid.PIDcontroller(p)
        goodness = drive()
        print("goodness: ", goodness, 'BESTgoodness', best_goodness)
        print('sum_dp: ', sum(dp))
        print()
        if goodness < best_goodness:
            best_goodness = goodness
            dp[i] *= 1.1
        else:
            p[i] -= 2 * dp[i]  # Go into the other direction
            player_car = PlayerCar(1, 4)
            controller = pid.PIDcontroller(p)
            goodness = drive()
            print("else goodness: ", goodness)
            if goodness < best_goodness:  # There was an improvement
                best_goodness = goodness
                dp[i] *= 1.05
            else:  # There was no improvement
                p[i] += dp[i]
                # As there was no improvement, the step size in either
                # direction, the step size might simply be too big.
                dp[i] *= 0.95

print("Final p: ", p)
pygame.quit()