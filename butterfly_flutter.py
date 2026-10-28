import turtle as t
import math
import random
import time

SCALE = 10
WIDTH, HEIGHT = 900, 900
BACKGROUND = "#000000"
CENTER_X, CENTER_Y = 0, -8
SEED = 27

DRAW_DELAY = 0.0005
FPS_DELAY = 0.015
FLAP_SPEED = 0.11
MIN_WING_WIDTH = 0.34

random.seed(SEED)
screen = t.Screen()
screen.setup(WIDTH, HEIGHT)
screen.title("Silver Butterfly")
screen.bgcolor(BACKGROUND)
screen.tracer(0, 0)

pen = t.Turtle(visible=False)
pen.speed(0)

wing_data = []

def gray(value):
    value = max(0, min(255, int(value)))
    return f"#{value:02x}{value:02x}{value:02x}"

def cubic_point(p0, p1, p2, p3, u):
    v = 1.0 - u
    v3 = v ** 3
    u3 = u ** 3
    x = v3 * p0[0] + 3 * v * v * u * p1[0] + 3 * v * u * u * p2[0] + u3 * p3[0]
    y = v3 * p0[1] + 3 * v * v * u * p1[1] + 3 * v * u * u * p2[1] + u3 * p3[1]
    return x, y

def transform_segments(local_segments, side):
    return [[(CENTER_X + side * x, CENTER_Y + y) for x, y in segment]
            for segment in local_segments]

UPPER_WING = [
    ((0,0),(5.8,15.5),(21.5,38.0),(37.5,40.0)),
    ((37.5,40.0),(38.5,28.5),(31.0,3.5),(23.0,0)),
    ((23.0,0),(15.0,0.7),(5.5,-0.1),(0,0)),
]
LOWER_WING = [
    ((0,0),(6.5,-0.1),(17.0,0.8),(23.5,-1.4)),
    ((23.5,-1.4),(25.0,-10.5),(17.0,-30.0),(10.5,-30.0)),
    ((10.5,-30.0),(4.5,-29.0),(0.8,-9.0),(0,0)),
]

def make_boundary(segments, samples_per_curve=100):
    boundary = []
    for index, (p0,p1,p2,p3) in enumerate(segments):
        for i in range(0 if index == 0 else 1, samples_per_curve+1):
            boundary.append(cubic_point(p0,p1,p2,p3, i/samples_per_curve))
    return boundary

def fill_wing(boundary):
    pen.penup()
    pen.goto(boundary[0][0]*SCALE, boundary[0][1]*SCALE)
    pen.pencolor("#151515")
    pen.fillcolor("#101010")
    pen.pensize(1)
    pen.begin_fill()
    pen.pendown()
    for x, y in boundary[1:]:
        pen.goto(x*SCALE, y*SCALE)
    pen.goto(boundary[0][0]*SCALE, boundary[0][1]*SCALE)
    pen.end_fill()
    pen.penup()

def draw_and_record_strand(start, end, side, steps=19):
    sx = start[0] + random.uniform(-0.045, 0.045)
    sy = start[1] + random.uniform(-0.045, 0.045)
    ex, ey = end
    dx, dy = ex - sx, ey - sy
    bend = (abs(dy)*random.uniform(0.015,0.065) + abs(dx)*random.uniform(0.008,0.030)) * side
    c1 = (sx + dx*0.24 + bend*0.20, sy + dy*0.34)
    c2 = (sx + dx*0.72 + bend, sy + dy*0.82)

    shade = random.randint(38, 100)
    chance = random.random()
    if chance < 0.055: shade = random.randint(112, 158)
    elif chance < 0.13: shade = random.randint(82, 125)

    color = gray(shade)
    size = random.choice((0.45,0.55,0.65,0.75,0.85))

    pen.pencolor(color)
    pen.pensize(size)
    pen.penup()
    pen.goto(sx*SCALE, sy*SCALE)
    pen.pendown()
    
    points = []
    for step in range(0, steps+1):
        pt = cubic_point((sx,sy), c1, c2, (ex,ey), step/steps)
        points.append(pt)
        pen.goto(pt[0]*SCALE, pt[1]*SCALE)
    pen.penup()
    wing_data.append(('strand', points, color, size))

def draw_wing_with_process(side, is_upper):
    local = UPPER_WING if is_upper else LOWER_WING
    segments = transform_segments(local, side)
    boundary = make_boundary(segments)
    
    fill_wing(boundary)
    wing_data.append(('fill', boundary))

    counts = (190, 220, 130) if is_upper else (155, 170, 110)
    start = (CENTER_X, CENTER_Y)
    strands_done = 0

    for segment, count in zip(segments, counts):
        p0,p1,p2,p3 = segment
        for i in range(1, count+1):
            endpoint = cubic_point(p0,p1,p2,p3, i/count)
            draw_and_record_strand(start, endpoint, side)
            strands_done += 1
            if strands_done % 15 == 0:
                screen.update()
            time.sleep(DRAW_DELAY)

    edge_shades = (139,94,72) if is_upper else (122,94,81)
    edge_widths = (1.25,1.05,0.90)
    for segment, shade, width in zip(segments, edge_shades, edge_widths):
        p0,p1,p2,p3 = segment
        pen.pencolor(gray(shade))
        pen.pensize(width)
        pen.penup()
        pen.goto(p0[0]*SCALE, p0[1]*SCALE)
        pen.pendown()
        points = []
        for i in range(0, 111):
            pt = cubic_point(p0,p1,p2,p3, i/110)
            points.append(pt)
            pen.goto(pt[0]*SCALE, pt[1]*SCALE)
        pen.penup()
        wing_data.append(('edge', points, gray(shade), width))

def draw_center_glow():
    pen.penup()
    pen.goto(CENTER_X*SCALE, CENTER_Y*SCALE)
    for size, colour in [(21,"#181818"),(16,"#2c2c2c"),(11,"#515151"),
                          (7,"#858585"),(4,"#c5c5c5"),(2,"#ffffff")]:
        pen.dot(size, colour)

    for i in range(24):
        angle = 2*math.pi*i/24
        length = random.uniform(0.35, 0.9)
        x2 = CENTER_X + math.cos(angle)*length
        y2 = CENTER_Y + math.sin(angle)*length
        pen.pencolor(gray(random.randint(95,175)))
        pen.pensize(random.choice((0.5,0.7,0.9)))
        pen.goto(CENTER_X*SCALE, CENTER_Y*SCALE)
        pen.pendown()
        pen.goto(x2*SCALE, y2*SCALE)
        pen.penup()

def render_frame(factor):
    pen.clear()
    for item in wing_data:
        if item[0] == 'fill':
            boundary = item[1]
            pen.penup()
            init_x = (CENTER_X + (boundary[0][0] - CENTER_X) * factor) * SCALE
            pen.goto(init_x, boundary[0][1]*SCALE)
            pen.pencolor("#151515")
            pen.fillcolor("#101010")
            pen.pensize(1)
            pen.begin_fill()
            pen.pendown()
            for x, y in boundary[1:]:
                curr_x = (CENTER_X + (x - CENTER_X) * factor) * SCALE
                pen.goto(curr_x, y*SCALE)
            pen.end_fill()
            
        elif item[0] == 'strand':
            _, points, color, size = item
            pen.pencolor(color)
            pen.pensize(size)
            pen.penup()
            init_x = (CENTER_X + (points[0][0] - CENTER_X) * factor) * SCALE
            pen.goto(init_x, points[0][1]*SCALE)
            pen.pendown()
            for x, y in points[1:]:
                curr_x = (CENTER_X + (x - CENTER_X) * factor) * SCALE
                pen.goto(curr_x, y*SCALE)
            pen.penup()
            
        elif item[0] == 'edge':
            _, points, color, width = item
            pen.pencolor(color)
            pen.pensize(width)
            pen.penup()
            init_x = (CENTER_X + (points[0][0] - CENTER_X) * factor) * SCALE
            pen.goto(init_x, points[0][1]*SCALE)
            pen.pendown()
            for x, y in points[1:]:
                curr_x = (CENTER_X + (x - CENTER_X) * factor) * SCALE
                pen.goto(curr_x, y*SCALE)
            pen.penup()

    draw_center_glow()
    screen.update()

draw_wing_with_process(-1, is_upper=True)
draw_wing_with_process(1, is_upper=True)
draw_wing_with_process(-1, is_upper=False)
draw_wing_with_process(1, is_upper=False)
draw_center_glow()
screen.update()

time.sleep(0.3)

phase = 0.0
try:
    while True:
        phase += FLAP_SPEED
        current_factor = MIN_WING_WIDTH + (1.0 - MIN_WING_WIDTH) * (0.5 + 0.5 * math.cos(phase))
        render_frame(current_factor)
        time.sleep(FPS_DELAY)
except t.Terminator:
    pass
