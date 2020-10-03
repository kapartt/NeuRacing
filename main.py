import math
import pygame
import sys

icon_dir = 'img/icon.png'
track_dir = 'img/map.png'
car_dir = 'img/car.jpg'
heading = 'NeuRacing'
GRAY = (220, 220, 220)
BLACK = (0, 0, 0)
screen_scale = 1.5
start_x = 358.26271662491143 * screen_scale
start_y = 107.887105126521 * screen_scale
border_dx = 5
border_dy = 5
angle_start = -174.4
polar_angle_start = -264.4
rectangle_width = int(100 * screen_scale)
rectangle_height = int(30 * screen_scale)
font_name = 'freesansbold.ttf'
font_size = int(18 * screen_scale)

# Physics
delta_angle_turn = 0.5
min_velocity = -1 * screen_scale
max_velocity = 5 * screen_scale
acceleration_gas = 0.003 * screen_scale
acceleration_break = -0.005 * screen_scale
acceleration_reverse = -0.003 * screen_scale
friction_mu = 0.001 * screen_scale

pygame.init()
pygame.display.set_caption(heading)
icon_img = pygame.image.load(icon_dir)
pygame.display.set_icon(icon_img)

track_img = pygame.image.load(track_dir)
screen_width = int(track_img.get_width() * screen_scale)
screen_height = int(track_img.get_height() * screen_scale)
screen = pygame.display.set_mode((screen_width, screen_height))
scale_track = pygame.transform.scale(track_img, (screen_width, screen_height))

car_img = pygame.image.load(car_dir)
scale_car = pygame.transform.scale(car_img, (int(car_img.get_width() // 8 * screen_scale),
                                         int(car_img.get_height() // 8 * screen_scale)))

car_x = start_x
car_y = start_y
angle = angle_start
polar_angle = polar_angle_start
velocity = 0
acceleration = 0
state_label = 'Stop'
flag_up = False
flag_down = False
flag_left = False
flag_right = False


def get_acceleration():
    if flag_down:
        if velocity > 0:
            return acceleration_break
        return acceleration_reverse
    if flag_up:
        return acceleration_gas
    return 0


def get_delta_angle():
    if flag_left and velocity > 0 or flag_right and velocity < 0:
        return delta_angle_turn
    elif flag_left and velocity < 0 or flag_right and velocity > 0:
        return -delta_angle_turn
    return 0


def update_screen():
    screen.blit(scale_track, (0, 0))
    rot = pygame.transform.rotate(scale_car, angle)
    rot_rect = rot.get_rect(center=(int(car_x), int(car_y)))
    screen.blit(rot, rot_rect)

    pygame.draw.rect(screen, GRAY, (screen_width - rectangle_width, screen_height - rectangle_height,
                                    rectangle_width, rectangle_height))
    font_state = pygame.font.Font(font_name, font_size)
    text_state = font_state.render(state_label, True, BLACK)
    text_state_rect = text_state.get_rect()
    text_state_rect.center = (screen_width - rectangle_width // 2, screen_height - rectangle_height // 2)
    screen.blit(text_state, text_state_rect)

    pygame.draw.rect(screen, GRAY, (screen_width - rectangle_width, screen_height - 2 * rectangle_height,
                                    rectangle_width, rectangle_height))
    font_velocity = pygame.font.Font(font_name, font_size)
    text_velocity = font_velocity.render("%.0f km/h" % (100 * abs(velocity)), True, (0, 0, 0))
    text_velocity_rect = text_velocity.get_rect()
    text_velocity_rect.center = (screen_width - rectangle_width // 2, screen_height - (3 * rectangle_height) // 2)
    screen.blit(text_velocity, text_velocity_rect)

    pygame.display.update()


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                flag_up = True
                state_label = 'Gas'
            if event.key == pygame.K_DOWN:
                flag_down = True
                state_label = 'Break'
            if event.key == pygame.K_LEFT:
                flag_left = True
                state_label = 'Left'
            if event.key == pygame.K_RIGHT:
                flag_right = True
                state_label = 'Right'
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                flag_up = False
            if event.key == pygame.K_DOWN:
                flag_down = False
            if event.key == pygame.K_LEFT:
                flag_left = False
            if event.key == pygame.K_RIGHT:
                flag_right = False

    if flag_up and not (flag_right or flag_left or flag_down):
        state_label = 'Gas'
    if flag_right and not (flag_up or flag_left or flag_down):
        state_label = 'Right'
    if flag_left and not (flag_right or flag_up or flag_down):
        state_label = 'Left'
    if flag_down and not (flag_up or flag_left or flag_right):
        state_label = 'Break'

    acceleration = get_acceleration()
    velocity += acceleration
    if velocity > 0:
        velocity = max(velocity - friction_mu, 0)
    elif velocity < 0:
        velocity = min(velocity + friction_mu, 0)
    if velocity == 0 and acceleration == 0:
        state_label = 'Stop'
    if velocity < 0:
        state_label = 'Reverse'
    velocity = max(min(max_velocity, velocity), min_velocity)

    delta_angle = get_delta_angle()
    polar_angle += delta_angle
    angle += delta_angle
    polar_angle_degree = polar_angle * math.pi / 180

    car_x += velocity * math.sin(polar_angle_degree)
    car_y += velocity * math.cos(polar_angle_degree)

    if not (border_dx <= car_x <= screen_width - border_dx and border_dy <= car_y <= screen_height - border_dy):
        velocity = 0
        acceleration = 0
        car_x = max(min(screen_width - border_dx, car_x), border_dx)
        car_y = max(min(screen_height - border_dy, car_y), border_dy)

    update_screen()
