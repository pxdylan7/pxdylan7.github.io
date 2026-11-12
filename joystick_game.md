# 🚀 Space Dodger: An Arduino Joystick Game

*Innovator's Journal Entry*

---

## Overview

I've always played my Python games with the keyboard, and for this project I wanted to swap that out for a real joystick I wired up myself. I don't know how to code yet, so I worked with Claude (an AI assistant) to write both the Arduino code and the game. My job was the hands-on part: wiring the joystick, uploading the code, installing everything, running the game, and going back to the AI with every error until it finally worked.

The game is called **Space Dodger**. You fly a little spaceship with the joystick, grab the yellow stars, and try not to get hit by meteors. Collect 4 stars and your shield charges up. Push the joystick down and you're protected for a few seconds.

## Why I Chose This

I already had a few Python games that only worked with the keyboard. I thought it would be really cool to play one with a controller I built myself, and it was a good excuse to finally figure out how an Arduino talks to a computer.

## Components & Sources

| | |
|---|---|
| **Input** | Joystick module |
| **Output** | The game running on my laptop screen |
| **Code** | Written by Claude (AI) |
| **Software I installed** | `pygame-ce` and `pyserial` (Python add-ons the game needs) |

---

## The Build Process

### Step 1: Wiring the Joystick

The joystick module has 5 pins. The AI told me which Arduino pin each one connects to, and I hooked them up with jumper wires.

### Step 2: Uploading the Arduino Code

I pasted the code into the Arduino IDE and uploaded it to the board. To make sure it was working, I opened the Serial Monitor. Numbers started showing up, and they changed whenever I moved the stick, so I knew the Arduino was reading it.

### Step 3: Running the Game

I ran the game from Terminal on my Mac. This step took way longer than I expected, because it didn't work the first few times (see below).

---

## What Went Wrong (and How I Fixed It)

Honestly, this was most of the project.

- **"No module named pygame."** I was sure I'd already installed it. It turned out it went into a *different* version of Python than the one I was running. The AI gave me a new install command that put it in the right place.

- **pygame wouldn't install at all.** The install crashed with a huge error message. I pasted the whole thing to the AI, and it explained that my Mac has a really new version of Python that regular pygame doesn't support yet. It had me install **pygame-ce** instead (a version that does support it), and that one worked.

- **The game crashed right when it opened** with an "invalid color" error. I sent that to the AI too. It said one of the color values in its code went over 255, which is the highest number a color can have. It fixed the code and the game opened.

- **The game couldn't find the joystick.** This one took me a while. If the Arduino Serial Monitor is still open, it hogs the connection and the game can't use it. Now I always close the Serial Monitor before I play.

---

## Final Build

### Wiring

| Joystick Pin | Arduino Pin |
|---|---|
| GND | GND |
| +5V | 5V |
| VRx | A0 |
| VRy | A1 |
| SW | Pin 2 |

### Arduino Code (written by Claude)

```cpp
// Arduino joystick -> Python games
// Wiring (standard 5-pin joystick module):
// GND -> GND, +5V -> 5V, VRx -> A0, VRy -> A1, SW -> D2
// Sends one line about 50 times a second: x,y,button
// x and y are 0-1023 (about 512 when centered), button is 1 when pressed
const int PIN_X = A0;
const int PIN_Y = A1;
const int PIN_SW = 2;

void setup() {
  Serial.begin(9600);
  pinMode(PIN_SW, INPUT_PULLUP); // button reads LOW when pressed
}

void loop() {
  int x = analogRead(PIN_X);
  int y = analogRead(PIN_Y);
  int pressed = digitalRead(PIN_SW) == LOW ? 1 : 0;
  Serial.print(x);
  Serial.print(',');
  Serial.print(y);
  Serial.print(',');
  Serial.println(pressed);
  delay(20);
}
```

### Game Code: `space_dodger.py` (written by Claude)

```python
"""
SPACE DODGER - an Arduino joystick game
Move your ship with the joystick, grab the yellow stars, dodge the meteors.
Push the stick down (button) to use a shield when the bar is full.
Run: python space_dodger.py
Needs: pip install pygame pyserial
Works with the keyboard too (arrow keys + space) if no Arduino is plugged in.
"""
import math
import random
import sys
import threading
import time
import pygame

# ---------------- Arduino joystick ----------------
class Joystick:
    """Reads 'x,y,button' lines from the Arduino. Falls back silently if none found."""
    def __init__(self, deadzone=0.2):
        self.x = 0.0
        self.y = 0.0
        self.pressed = False
        self.connected = False
        self.deadzone = deadzone
        try:
            import serial
            import serial.tools.list_ports
            ports = list(serial.tools.list_ports.comports())
            port = None
            for p in ports:
                text = f"{p.description} {p.manufacturer or ''} {p.device}".lower()
                if any(w in text for w in ("arduino", "ch340", "usb serial", "usbmodem", "usbserial", "wch")):
                    port = p.device
                    break
            if port is None and ports:
                port = ports[0].device
            if port is None:
                print("No Arduino found - using keyboard (arrow keys + space).")
                return
            self.ser = serial.Serial(port, 9600, timeout=1)
            time.sleep(2)  # Arduino restarts when the port opens
            self.ser.reset_input_buffer()
            self.connected = True
            threading.Thread(target=self._read, daemon=True).start()
            print(f"Joystick connected on {port}")
        except Exception as e:
            print(f"Joystick not available ({e}) - using keyboard.")

    def _read(self):
        while True:
            try:
                line = self.ser.readline().decode(errors="ignore").strip()
                rx, ry, b = (int(v) for v in line.split(","))
            except ValueError:
                continue
            except Exception:
                self.connected = False
                return
            x = (rx - 512) / 512
            y = (ry - 512) / 512
            self.x = 0.0 if abs(x) < self.deadzone else max(-1.0, min(1.0, x))
            self.y = 0.0 if abs(y) < self.deadzone else max(-1.0, min(1.0, y))
            self.pressed = b == 1

# Flip these to True if a direction is backwards on your joystick
INVERT_X = False
INVERT_Y = False

# ---------------- Game ----------------
WIDTH, HEIGHT = 800, 600
FPS = 60
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Dodger")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 24, bold=True)
big_font = pygame.font.SysFont("arial", 64, bold=True)
stick = Joystick()
stars_bg = [[random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(1, 3)]
            for _ in range(120)]


def read_controls():
    """Returns (dx, dy, button) from the joystick, or the keyboard as a backup."""
    keys = pygame.key.get_pressed()
    dx = stick.x * (-1 if INVERT_X else 1)
    dy = stick.y * (-1 if INVERT_Y else 1)
    if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx = -1
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx = 1
    if keys[pygame.K_UP] or keys[pygame.K_w]: dy = -1
    if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy = 1
    button = stick.pressed or keys[pygame.K_SPACE]
    return dx, dy, button


class Player:
    def __init__(self):
        self.x = WIDTH / 2
        self.y = HEIGHT - 100
        self.speed = 7
        self.radius = 18
        self.shield_charge = 0  # fills up to 100
        self.shield_time = 0    # frames left of active shield

    def update(self, dx, dy):
        self.x = max(self.radius, min(WIDTH - self.radius, self.x + dx * self.speed))
        self.y = max(self.radius, min(HEIGHT - self.radius, self.y + dy * self.speed))
        if self.shield_time > 0:
            self.shield_time -= 1

    def draw(self, surf):
        x, y = self.x, self.y
        # flame
        flame = random.randint(10, 18)
        pygame.draw.polygon(surf, (255, 140, 0), [(x - 7, y + 14), (x + 7, y + 14), (x, y + 14 + flame)])
        # ship body
        pygame.draw.polygon(surf, (90, 200, 255), [(x, y - 22), (x - 18, y + 16), (x + 18, y + 16)])
        pygame.draw.circle(surf, (230, 250, 255), (int(x), int(y - 2)), 6)
        if self.shield_time > 0:
            pulse = 4 * math.sin(pygame.time.get_ticks() / 80)
            pygame.draw.circle(surf, (120, 255, 200), (int(x), int(y)), int(32 + pulse), 3)


class Meteor:
    def __init__(self, level):
        self.radius = random.randint(14, 34)
        self.x = random.randint(self.radius, WIDTH - self.radius)
        self.y = -self.radius
        self.vy = random.uniform(2.5, 4.5) + level * 0.5
        self.vx = random.uniform(-1.5, 1.5)
        self.angle = 0
        self.spin = random.uniform(-3, 3)
        n = 9
        self.shape = [(math.cos(2 * math.pi * i / n) * self.radius * random.uniform(0.75, 1.1),
                       math.sin(2 * math.pi * i / n) * self.radius * random.uniform(0.75, 1.1))
                      for i in range(n)]

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.angle += self.spin

    def draw(self, surf):
        a = math.radians(self.angle)
        pts = [(self.x + px * math.cos(a) - py * math.sin(a),
                self.y + px * math.sin(a) + py * math.cos(a)) for px, py in self.shape]
        pygame.draw.polygon(surf, (140, 110, 90), pts)
        pygame.draw.polygon(surf, (90, 70, 55), pts, 3)


class Star:
    def __init__(self):
        self.x = random.randint(20, WIDTH - 20)
        self.y = -20
        self.vy = 3
        self.radius = 12

    def update(self):
        self.y += self.vy

    def draw(self, surf):
        t = pygame.time.get_ticks() / 200
        pts = []
        for i in range(10):
            r = self.radius if i % 2 == 0 else self.radius / 2.2
            ang = t + i * math.pi / 5
            pts.append((self.x + r * math.cos(ang), self.y + r * math.sin(ang)))
        pygame.draw.polygon(surf, (255, 220, 50), pts)


class Particle:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        ang = random.uniform(0, 2 * math.pi)
        spd = random.uniform(1, 6)
        self.vx, self.vy = math.cos(ang) * spd, math.sin(ang) * spd
        self.life = random.randint(20, 40)
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surf):
        if self.life > 0:
            pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), max(1, self.life // 10))


def hit(a, b, extra=0):
    return math.hypot(a.x - b.x, a.y - b.y) < a.radius + b.radius - extra


def draw_background():
    screen.fill((8, 8, 25))
    for s in stars_bg:
        s[1] += s[2]
        if s[1] > HEIGHT:
            s[0], s[1] = random.randint(0, WIDTH), 0
        shade = int(70 * s[2])
        pygame.draw.circle(screen, (shade, shade, min(255, shade + 20)), (int(s[0]), int(s[1])), 1)


def center_text(text, f, y, color=(255, 255, 255)):
    img = f.render(text, True, color)
    screen.blit(img, (WIDTH / 2 - img.get_width() / 2, y))


def wait_for_button(title, subtitle):
    """Shows a screen until the button (or space) is pressed and released."""
    released = False
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                pygame.quit(); sys.exit()
        _, _, button = read_controls()
        if not button:
            released = True
        elif released:
            return
        draw_background()
        center_text(title, big_font, 190, (90, 200, 255))
        for i, line in enumerate(subtitle):
            center_text(line, font, 300 + i * 36)
        status = "Joystick connected" if stick.connected else "No joystick - using keyboard"
        center_text(status, font, HEIGHT - 50, (120, 255, 200) if stick.connected else (255, 150, 150))
        pygame.display.flip()
        clock.tick(FPS)


def play():
    player = Player()
    meteors, stars, particles = [], [], []
    score, frame = 0, 0
    button_was_down = True
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                pygame.quit(); sys.exit()
        frame += 1
        level = score // 10
        dx, dy, button = read_controls()
        # shield: press the button once when the bar is full
        if button and not button_was_down and player.shield_charge >= 100:
            player.shield_time = FPS * 3
            player.shield_charge = 0
        button_was_down = button
        player.update(dx, dy)
        # spawn things (faster as the level goes up)
        if random.random() < 0.025 + level * 0.006:
            meteors.append(Meteor(level))
        if random.random() < 0.012:
            stars.append(Star())
        for m in meteors: m.update()
        for s in stars: s.update()
        for p in particles: p.update()
        # collect stars
        for s in stars[:]:
            if hit(player, s):
                stars.remove(s)
                score += 1
                player.shield_charge = min(100, player.shield_charge + 25)
                particles += [Particle(s.x, s.y, (255, 220, 50)) for _ in range(12)]
        # meteor hits
        for m in meteors[:]:
            if hit(player, m, extra=6):
                if player.shield_time > 0:
                    meteors.remove(m)
                    score += 1
                    particles += [Particle(m.x, m.y, (160, 130, 100)) for _ in range(20)]
                else:
                    return score
        meteors = [m for m in meteors if m.y < HEIGHT + 50]
        stars = [s for s in stars if s.y < HEIGHT + 30]
        particles = [p for p in particles if p.life > 0]
        # draw
        draw_background()
        for s in stars: s.draw(screen)
        for m in meteors: m.draw(screen)
        for p in particles: p.draw(screen)
        player.draw(screen)
        screen.blit(font.render(f"Score: {score}", True, (255, 255, 255)), (15, 12))
        screen.blit(font.render(f"Level: {level + 1}", True, (255, 255, 255)), (15, 42))
        # shield bar
        pygame.draw.rect(screen, (60, 60, 80), (WIDTH - 215, 15, 200, 20), border_radius=6)
        pygame.draw.rect(screen, (120, 255, 200), (WIDTH - 215, 15, 2 * player.shield_charge, 20), border_radius=6)
        label = "SHIELD READY - press button!" if player.shield_charge >= 100 else "Shield"
        img = font.render(label, True, (120, 255, 200))
        screen.blit(img, (WIDTH - 15 - img.get_width(), 40))
        pygame.display.flip()
        clock.tick(FPS)


def main():
    high = 0
    wait_for_button("SPACE DODGER", [
        "Move with the joystick, collect stars, dodge meteors",
        "4 stars = full shield, push the stick down to use it",
        "Press the joystick button to start",
    ])
    while True:
        score = play()
        high = max(high, score)
        wait_for_button("GAME OVER", [
            f"Score: {score}   Best: {high}",
            "Press the joystick button to play again",
            "Esc to quit",
        ])


if __name__ == "__main__":
    main()
```

> **Note:** The comment at the top of the game says `pip install pygame`, but on my Mac I had to use `pip install pygame-ce pyserial` instead (see "What Went Wrong" above).

---

## 🔧 Technical Tidbit: How the Joystick Works

Here's what I figured out along the way. The joystick is basically two knobs (like volume knobs) stacked together, one for left/right and one for up/down. The Arduino reads each one as a number from **0 to 1023**, and when the stick is sitting in the middle, it reads about **512**. The Arduino sends those numbers to my laptop through the USB cable around 50 times a second, and the game turns them into ship movement. Pressing the stick straight down clicks a little button hidden inside it, and that's what turns on the shield.

---

## 💡 Use-Case Reflection

**What problem could this solve, and who would it help?**
A homemade controller like this could help people who have trouble using a regular keyboard still be able to play games. A joystick only needs one hand and simple movements.

**What would need to change to make it real?**
Right now it's a bunch of jumper wires that fall out if you bump them. To actually be useful, it would need to be wireless and have a proper case to hold everything together.

**The skill I relied on most:**
**Troubleshooting.** Most of my time wasn't spent building. It was spent reading error messages, sending them to the AI, trying the fix, and doing it again until the game finally ran. I learned that getting something to work is mostly about not giving up when it breaks.
