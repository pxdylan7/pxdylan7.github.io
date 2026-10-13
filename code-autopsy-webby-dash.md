---
layout: default
title: "Code Autopsy: Webby Dash"
---

# Code Autopsy: Webby Dash

Webby Dash is a Geometry Dash style game written in Python with pygame. A square moves forward by itself without any action by the person playing the game, and the player jumps over spikes and onto blocks to reach the end of the level. 


## 1. The Canvas

### Where it is

There is no HTML canvas in pygame. The drawing area is the game window, which is created with pygame.display.set_mode.

```python
WIDTH = 800
HEIGHT = 450

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Webby Dash")
```

### Size

The window of the game is 800 pixels wide and 450 pixels tall.

### What happens if I change it

The window will get bigger or smaller depending on how small or big I want it to be. 
---

## 2. The State Variables

### Where they are declared

The varaibles are declared right before the game is started and during. It tracks your progress, position, your overall status/ health in the game, and most importantly the movement of the player.

```python
state = "menu"
player_y = GROUND_Y - TILE
velocity = 0
angle = 0
on_ground = True
camera_x = 0
progress = 0
```


## 3. The Game Loop

### What runs over and over

```python
running = True
while running:
    ...
    pygame.display.flip()
    clock.tick(FPS)
```

### How often

clock.tick(FPS) with a FPS = 60, which overall makes the loop run 60 times per second. Each run is one frame.

### What it does each time

Checks input, like mouse clicks or closing the window. It moves the camera foward each attempt, each jump by the player always occured. It always checks for collision with blocks or spikes that will result in restarting the game when colliding with these obstacles. It updates the progress each time you get better than your all time best progress point.


## 4. Input Handling

### Controls

- Space, the up arrow, or the left mouse button to jump
- Click Play or Replay to start
- Close the window to quit, very fun and simple

### Events

Each one of these keys has the same function, for example pressing the space up arrow and left mouse button makes you jump in the game. 


### What a key press changes

Jumping changes only one thing, velocity gets set to JUMP_STRENGTH, which is -15. The negative number makes the player move up. 

## 5. Collision and Win-Lose Logic

The game uses rectangles to check whether things are touching or colliding. The player is a rectangle. 

```python
player_rect = pygame.Rect(PLAYER_X, int(player_y), TILE, TILE)
```

### Hitting the ground

This checks whether the bottom of the player has gone hit the ground line that it is supposed to be on

```python
if player_y + TILE >= GROUND_Y:
    player_y = GROUND_Y - TILE
    velocity = 0
    on_ground = True
```

### Hitting a spike

Hitting a spike causes you to restart your progress back to the beginning, each spikes spkies hitbox is just a little smaller than the triangle shown on the screen, so even if you just barely scrap the edge of a spike does not mean it was a hit.

```python
if obstacle["kind"] == "spike":
    if player_rect.colliderect(spike_hitbox(rect)):
        state = "crashed"
```

### Hitting a block

Hitting a block could mean two different things in this game, one you could have just landed on the block from a jump, two you ran into the block which would result in a restart of the game.

```python
elif player_rect.colliderect(rect):
    landed_on_top = velocity >= 0 and previous_bottom <= rect.top + 10
    if landed_on_top:
        player_y = rect.top - TILE
        velocity = 0
        on_ground = True
        player_rect.y = int(player_y)
    else:
        state = "crashed"
```

### Winning

When you complete the course you win it overall stops running and shows a Level Complete, if you crash it shows Crashed 

```python
if camera_x >= LEVEL_END:
    state = "won"
```

## 6. Scoring

### Where the score lives

My game doesn't have points, it scores progress. So the percent of the level finished. 

```python
progress = 0
```

### The line that changes it

This divides how far the player has gone by the length of the whole level, then it multiplies it by 100 to get the overall percent. 

```python
progress = min(100, 100 * camera_x // LEVEL_END)
```

### Where it's shown

When the player crashes, the score is displayed on the center top of the window. 

```python
draw_text(str(progress) + "% complete", font, HEIGHT // 2 - 50)
```
### Goals/Reflection 

Today, I saw my classes games and code, and I was suprised and interested in many of them. Some were simple and fun and some were complex and fun too. My goal for the future for my game is to potentially add more features in the game, create different color sections throughou the level, and understand every line of code througout my game. 
