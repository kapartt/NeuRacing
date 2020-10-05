import math
import pygame
import sys
from ai import nn

icon_dir = 'img/icon.png'
track_dir = 'img/map.png'
car_dir = 'img/car.jpg'
heading = 'NeuRacing'
colors = {'TRACK': (179, 179, 179, 255), 'GRAVE': (100, 110, 100, 255), 'GRASS': (50, 100, 50, 255),
          'WHITE': (255, 255, 255, 255), 'CURB': (117, 70, 70, 255), 'BLACK': (0, 0, 0, 255),
          'GRAY': (220, 220, 220, 255), 'CURB_': (190, 100, 100, 255)}
screen_colors = {'RED': (255, 0, 0, 255), 'GREEN': (0, 255, 0, 255)}
screen_scale = 1.5
start_x = 355 * screen_scale
start_y = 108 * screen_scale
border_dx = 5
border_dy = 5
angle_start = -174.4
polar_angle_start = -264.4
rectangle_width = int(100 * screen_scale)
rectangle_height = int(30 * screen_scale)
font_name = 'freesansbold.ttf'
font_size = int(18 * screen_scale)
checkpoints = [[(557, 120), (563, 200)], [(650, 81), (691, 197)], [(789, 76), (800, 170)],
               [(902, 32), (925, 104)], [(1012, 18), (1000, 99)], [(1097, 124), (1017, 125)],
               [(1047, 214), (1017, 125)], [(943, 132), (935, 210)], [(802, 201), (883, 225)],
               [(804, 266), (880, 230)], [(877, 322), (958, 290)], [(868, 337), (935, 389)],
               [(834, 340), (838, 429)], [(715, 304), (672, 373)], [(597, 241), (558, 311)],
               [(454, 232), (510, 299)], [(440, 355), (515, 310)], [(518, 420), (599, 392)],
               [(528, 453), (596, 500)], [(507, 460), (462, 530)], [(407, 346), (347, 403)],
               [(264, 287), (258, 371)], [(148, 311), (128, 394)], [(82, 265), (5, 297)],
               [(88, 244), (17, 197)], [(110, 211), (67, 126)], [(114, 219), (180, 132)],
               [(192, 270), (200, 180)], [(344, 221), (323, 140)], [(555, 122), (561, 202)]]

# Physics
delta_angle_turn = 1
min_velocity = -1 * screen_scale
max_velocity = 5 * screen_scale
acceleration_gas = 0.003 * screen_scale
acceleration_break = -0.005 * screen_scale
acceleration_reverse = -0.003 * screen_scale
frictions = {'TRACK': 0.001, 'GRAVE': 0.001, 'GRASS': 0.001, 'WHITE': 0.001, 'CURB': 0.001, 'BLACK': 0.001,
             'FINISH': 0.001, 'ALMOST BLACK': 0.001, 'GRAY': 0.001, 'CURB_': 0.001}

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
state_label = 'Stop'
flag_up = False
flag_down = False
flag_left = False
flag_right = False
cur_checkpoint = 0
checkpoints_eq_abc = []
checkpoints_colors = []
for ch in checkpoints:
    checkpoints_colors.append('RED')
    a = ch[0][1] - ch[1][1]
    b = ch[1][0] - ch[0][0]
    c = - a * ch[0][0] - b * ch[0][1]
    checkpoints_eq_abc.append((a, b, c))
seconds = 0
minutes = 0
hours = 0


def get_acceleration() -> float:
    if flag_down:
        if velocity > 0:
            return acceleration_break
        return acceleration_reverse
    if flag_up:
        return acceleration_gas
    return 0


def get_surface(x: float, y: float) -> str:
    color = scale_track.get_at((int(x), int(y)))
    if abs(color[0] - color[1]) < 5 and abs(color[0] - color[1]) < 5 and abs(color[0] - color[1]) < 5:
        return 'TRACK'
    errors = [(col, sum([(color[i_col] - colors[col][i_col]) ** 2 for i_col in range(4)])) for col in colors]
    return min(errors, key=lambda q: q[1])[0]


def get_delta_angle() -> float:
    if flag_left and velocity > 0 or flag_right and velocity < 0:
        return delta_angle_turn
    elif flag_left and velocity < 0 or flag_right and velocity > 0:
        return -delta_angle_turn
    return 0


def get_friction() -> float:
    return frictions[get_surface(car_x, car_y)] * screen_scale


def get_distance_by_direction(dl: float, alpha: float) -> int:
    dist = 0
    max_dist = 500
    alpha *= math.pi / 180
    x0 = car_x + dl * math.sin(alpha)
    y0 = car_y + dl * math.cos(alpha)
    while True:
        x = x0 + dist * math.sin(alpha)
        y = y0 + dist * math.cos(alpha)
        if not (0 <= x < screen_width and 0 <= y < screen_height):
            return dist
        surface = get_surface(x, y)
        if surface == 'GRASS' or surface == 'GRAVE':
            break
        dist += 1
        if dist >= max_dist:
            break
    return dist


def get_distances() -> list:
    car_a = 11
    car_b = 24
    car_c = math.sqrt(car_a * car_a + car_b * car_b)
    alpha = math.atan(car_a / car_b) * 180 / math.pi
    left_backward = get_distance_by_direction(car_c, polar_angle + 180 - alpha)
    left = get_distance_by_direction(car_a, polar_angle + 90)
    left_forward = get_distance_by_direction(car_c, polar_angle + alpha)
    forward = get_distance_by_direction(car_b, polar_angle)
    right_forward = get_distance_by_direction(car_c, polar_angle - alpha)
    right = get_distance_by_direction(car_a, polar_angle - 90)
    right_backward = get_distance_by_direction(car_c, polar_angle - 180 + alpha)
    return [left_backward, left, left_forward, forward, right_forward, right, right_backward]


def update_checkpoints():
    global cur_checkpoint
    abc = checkpoints_eq_abc[cur_checkpoint]
    x = car_x + 24 * math.sin(polar_angle * math.pi / 180)
    y = car_y + 24 * math.cos(polar_angle * math.pi / 180)
    dist = abs(abc[0] * x + abc[1] * y + abc[2]) / math.sqrt(abc[0] * abc[0] + abc[1] * abc[1])
    x_0 = checkpoints[cur_checkpoint][0][0]
    y_0 = checkpoints[cur_checkpoint][0][1]
    x_1 = checkpoints[cur_checkpoint][1][0]
    y_1 = checkpoints[cur_checkpoint][1][1]
    if dist < 2 and (x_0 - x) * (x_1 - x) < 2 and (y_0 - y) * (y_1 - y) < 2:
        checkpoints_colors[cur_checkpoint] = 'GREEN'
        cur_checkpoint += 1
        if cur_checkpoint == len(checkpoints):
            cur_checkpoint = 0
            for i_cc in range(len(checkpoints_colors)):
                checkpoints_colors[i_cc] = 'RED'


def update_time(ticks: int) -> bool:
    global hours, minutes, seconds
    next_ticks = 3600000 * hours + 60000 * minutes + 1000 * (seconds + 1)
    if ticks > next_ticks:
        seconds += 1
        if seconds == 60:
            seconds = 0
            minutes += 1
            if minutes == 60:
                minutes = 0
                hours += 1
        return True
    return False


def update_screen():
    if update_time(pygame.time.get_ticks()):
        s = str(hours) + ':'
        if minutes < 10:
            s += '0'
        s += str(minutes) + ':'
        if seconds < 10:
            s += '0'
        s += str(seconds)
    #    print(s)
    screen.blit(scale_track, (0, 0))
    update_checkpoints()
    for i_chp in range(len(checkpoints)):
        chp = checkpoints[i_chp]
        pygame.draw.line(screen, screen_colors[checkpoints_colors[i_chp]], chp[0], chp[1], 2)
    rot = pygame.transform.rotate(scale_car, angle)
    rot_rect = rot.get_rect(center=(int(car_x), int(car_y)))
    screen.blit(rot, rot_rect)

    pygame.draw.rect(screen, colors['GRAY'], (screen_width - rectangle_width, screen_height - rectangle_height,
                                              rectangle_width, rectangle_height))
    font_state = pygame.font.Font(font_name, font_size)
    text_state = font_state.render(state_label, True, colors['BLACK'])
    text_state_rect = text_state.get_rect()
    text_state_rect.center = (screen_width - rectangle_width // 2, screen_height - rectangle_height // 2)
    screen.blit(text_state, text_state_rect)

    pygame.draw.rect(screen, colors['GRAY'], (screen_width - rectangle_width, screen_height - 2 * rectangle_height,
                                              rectangle_width, rectangle_height))
    font_velocity = pygame.font.Font(font_name, font_size)
    text_velocity = font_velocity.render("%.0f km/h" % (100 * abs(velocity)), True, (0, 0, 0))
    text_velocity_rect = text_velocity.get_rect()
    text_velocity_rect.center = (screen_width - rectangle_width // 2, screen_height - (3 * rectangle_height) // 2)
    screen.blit(text_velocity, text_velocity_rect)

    pygame.display.update()


def update_flags(x: int):
    global flag_up, flag_down, flag_left, flag_right
    flag_up = (x < 3)
    flag_down = (x > 5)
    flag_left = (x % 3 == 0)
    flag_right = (x % 3 == 2)


def do_action(ac: int):
    global velocity, polar_angle, angle, car_x, car_y, state_label
    update_flags(ac)
    acceleration = get_acceleration()
    velocity += acceleration
    friction_mu = get_friction()
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
    polar_angle_rad = polar_angle * math.pi / 180

    car_x += velocity * math.sin(polar_angle_rad)
    car_y += velocity * math.cos(polar_angle_rad)

    if not (border_dx <= car_x <= screen_width - border_dx and border_dy <= car_y <= screen_height - border_dy):
        velocity = 0
        car_x = max(min(screen_width - border_dx, car_x), border_dx)
        car_y = max(min(screen_height - border_dy, car_y), border_dy)


layers = tuple([4])
net = nn.NeuralNetwork(layers=layers, input_sz=8, output_sz=1, bias=True)
prev_checkpoint = 0
is_human = False
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
    if is_human:
        act = 4
        if flag_left:
            act = 3
        elif flag_right:
            act = 5
        if flag_down:
            if flag_left:
                act = 6
            elif flag_right:
                act = 8
            else:
                act = 7
        elif flag_up:
            if flag_left:
                act = 0
            elif flag_right:
                act = 2
            else:
                act = 1
        do_action(act)
        update_screen()
        continue
    old_x = car_x
    old_y = car_y
    old_velocity = velocity
    old_angle = angle
    old_polar_angle = polar_angle
    q_values = []
    for action in range(9):
        do_action(action)
        net_input = get_distances()
        for i in range(len(net_input)):
            net_input[i] *= 0.01
        net_input.append(velocity)
        net_output = net.get_output(net_input)
        q_values.append(net_output[0])
        car_x = old_x
        car_y = old_y
        velocity = old_velocity
        angle = old_angle
        polar_angle = old_polar_angle
    max_q_ind = q_values.index(max(q_values))
    update_checkpoints()
    reward = 0
    if prev_checkpoint != cur_checkpoint:
        reward += 1
        prev_checkpoint = cur_checkpoint
    net_input = get_distances()
    for i in range(len(net_input)):
        net_input[i] *= 0.01
    net_input.append(velocity)
    if min(net_input[:-1]) == 0:
        reward -= 1
    if net_input[-1] <= 0:
        reward -= 0.5
    q_old = q_values[max_q_ind]
    q_new = [(1 - net.learning_rate) * q_old + net.learning_rate * (reward + q_old)]
    net.back_propagation(net_input, q_new)
    q_new_new = net.get_output(net_input)
    do_action(max_q_ind)

    if flag_up and not (flag_right or flag_left or flag_down):
        state_label = 'Gas'
    if flag_right and not (flag_up or flag_left or flag_down):
        state_label = 'Right'
    if flag_left and not (flag_right or flag_up or flag_down):
        state_label = 'Left'
    if flag_down and not (flag_up or flag_left or flag_right):
        state_label = 'Break'
    update_screen()
