from core.common.names import *
import core.common.resources as cr
import core.common.utils as utils
from core.event_holder import EventHolder
from core.rope import *
#import numpy
global square_wave
square_wave = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 4, 6, 8, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 8, 6, 4, 2, 0]
cr.screen = pg.display.set_mode([1280, 720])
"""
event holder takes care of getting the events and
the game's fps
"""
cr.event_holder = EventHolder()
cr.event_holder.determined_fps = 60
global mouse_collider
mouse_collider = Collider(0, 61.3)
mouse_collider.size = 50
fish_sprites = [pygame.image.load("assets/Spritesheets/fish1/fish-0001.png").convert(), pygame.image.load("assets/Spritesheets/fish1/fish-0002.png").convert(), pygame.image.load("assets/Spritesheets/fish1/fish-0003.png").convert()]
fish_sprites = [utils.scale_image(f, 2) for f in fish_sprites]
def sawtooth_sample(amplitude, freq, samplerate, i):
    value = atan(tan(2.0 * pi * float(freq) * (float(i) / float(samplerate))))
    return amplitude * value

def plot_sawtooth(num_samples, frequency):
    # Generate the samples
    samples = []
    for i in range(num_samples):
        samples.append(sawtooth_sample(1.0, frequency, 44100, i))
    return samples
def triangle(length, amplitude):
    section = length // 4
    for direction in (1, -1):
        for i in range(section):
            yield i * (amplitude / section) * direction
        for i in range(section):
            yield (amplitude - (i * (amplitude / section))) * direction
sawtooth = plot_sawtooth(800, 300)
triangle_wave = list(triangle(150, 50))
class Fish:
    def __init__(self, x, elevation, type_):
        self.pos = [x, elevation]
        self.orig_pos = [x, elevation]
        
        self.speed = 5
        self.crossed = False
        self.pattern = random.randint(0, 2)
        self.type = self.pattern
        self.stage = -1
        self.adders = [5, 1, 0]
        self.adding = False
        self.delay = 0
    def update(self):
        global square_wave
        self.stage+=self.adders[self.pattern]
        self.delay+=1
        if (self.pattern == 1):
            if self.stage > len(triangle_wave)-1:
                self.stage = 0
        self.pos[0]+=self.speed
        if (self.pattern==0):
            self.pos[1]=self.orig_pos[1]+(sin(radians(self.stage))*60)
        if (self.pattern==1):
            self.pos[1]=self.orig_pos[1]+(triangle_wave[self.stage])
        if (self.pattern==2):
            if (self.delay%3==0):
                self.stage+=1
                if (self.stage>len(square_wave)-1):
                    self.stage=0
            self.pos[1]=self.orig_pos[1]+(square_wave[self.stage])*10
                    
        cr.screen.blit(fish_sprites[self.type], self.pos)
        if (self.pos[0]>1180+fish_sprites[self.type].get_width()/2):
            self.crossed = True
    def regen(self):
        self.pos = [random.randint(-(1280+fish_sprites[self.type].get_width()), 0-fish_sprites[self.type].get_width()), random.randint(0, 150)]
        self.crossed = False
        self.pattern = random.randint(0, 2)
        self.type = self.pattern
        self.stage = -1
        self.orig_pos=[self.pos[0], self.pos[1]]
class FishManager:
    def __init__(self):
        self.fishes = [Fish(random.randint(-1280, 0), random.randint(0, 150), random.randint(0, 1)) for i in range(20)]
    def update(self):
        num_fish = -1
        for fish in self.fishes:
            num_fish+=1
            if not fish.crossed:
                fish.update()
            else:
                self.fishes[num_fish].regen()
fish_manager = FishManager()
class Slider:
    def __init__(self, args):
        self.pos = args[0]
        self.font = args[1]
        self.div = args[2]
        self.rect_surf = pygame.Surface((32, 32))
        self.mask = pygame.mask.from_surface(self.rect_surf)
        self.outlines = self.mask.outline()
        self.bg_surf = pygame.Surface((32, 32))
        self.bg_surf.set_colorkey((0, 0, 0))
    def update(self):
        self.bg_surf.fill((0, 0, 0))
        self.overall_rect = pygame.Rect(self.pos[0], self.pos[1]-10, 120, 40)
        self.bar_rect = pygame.Rect(self.pos[0], self.pos[1], 120, 20)
        self.slider_rect = pygame.Rect(self.pos[0]+self.x_offset, self.pos[1]-10, 20, 40)
        if self.overall_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            self.x_offset = pygame.mouse.get_pos()[0]-self.pos[0]
        if self.x_offset > 100:
            self.x_offset = 100
        #pygame.draw.rect(cr.screen, (0, 0, 255), self.overall_rect)
        pygame.draw.rect(cr.screen, (0, 0, 50), self.bar_rect)
        pygame.draw.rect(cr.screen, (255, 255, 255), self.slider_rect)
        self.value = round(self.x_offset/10)
        if not self.div:
            self.value *= 10
        value = self.font.render(str(self.value), False, (255, 255, 255), (0, 0, 0))
        value.set_colorkey((0, 0, 0))
        pygame.draw.lines(self.bg_surf, (1, 1, 1), True, self.outlines, 3)
        self.bg_surf.blit(value, [self.bg_surf.get_width()/2-value.get_width()/2, self.bg_surf.get_height()/2-value.get_height()/2])
        cr.screen.blit(self.bg_surf, [self.pos[0]+self.overall_rect.w+25, self.pos[1]-(self.bar_rect.h/4)])
class Player:
    def __init__(self) -> None:
        self.throw_anim = []
        self.idle_anim = []
        self.pull_anim = []
        for i in range(6):
            self.throw_anim.append(pygame.transform.flip(utils.scale_image(pg.image.load("assets/Spritesheets//throw/throw"+str(i)+".png").convert()), False, False))
            self.throw_anim[i].set_colorkey([0, 0, 0])
        for i in range(5):
            self.idle_anim.append(pygame.transform.flip(utils.scale_image(pg.image.load("assets/Spritesheets//idle/idle00"+str(i)+".png").convert()), False, False))
            self.idle_anim[i].set_colorkey([0, 0, 0])
        for i in range(8):
            self.pull_anim.append(pygame.transform.flip(utils.scale_image(pg.image.load("assets/Spritesheets//pull/pull00"+str(i)+".png").convert()), False, False))
            self.pull_anim[i].set_colorkey([0, 0, 0])
        self.boat_sprite = pygame.transform.flip(utils.scale_image(pg.image.load("assets/Spritesheets//boat.png").convert()), False, False)
        self.boat_sprite.set_colorkey([255, 255, 255])
        self.pos = [
            0,
            360 - self.boat_sprite.get_height()+8
            
        ]
        self.line_length = 100
        self.default_length = 256
        self.bait_size = 1
        self.bait_sprite = pg.Surface([20, 20])
        self.scores = []
        self.fish = 0
        self.rope = None
        self.fishing_line_angle = 90
        self.fishing = False
        self.rope_screen = pygame.Surface([1280, 720])
        self.rope_screen.set_colorkey([0, 0, 0])
        self.rope_mask = None
        self.recreated = False
        self.recall_fishing_line = False
        self.cover_rect = pygame.Rect(0, 720, 1280, 720)
        self.set_angle = False
        self.down_rect = pygame.Rect(0, 360, 720, 360)
        self.y_points = []
        self.old_len = 0
        self.moving = False
        self.frame = 0
        self.delay = 0
        self.state = 0
        self.throw_begin_move = [0, 84]
    def create_fishing_line(self):
        self.rope = Rope(self.pos[0]+self.boat_sprite.get_width()+15, self.pos[1]+15, self.line_length, self.line_length//10)
    def prepare_fishing_line(self):
        self.rope.gravity.x = resultant_gravitational_force*cos(radians(self.fishing_line_angle))
        self.rope.gravity.y = resultant_gravitational_force*sin(radians(self.fishing_line_angle))
    def draw_boat(self):
        cr.screen.blit(self.boat_sprite, self.pos)
    def update(self):
        self.delay +=1
        if (pg.K_RIGHT in pressed_keys) or (pg.K_RIGHT in held_keys):
            self.fishing_line_angle -= 1
            print(self.fishing_line_angle)
        if (pg.K_LEFT in pressed_keys) or (pg.K_LEFT in held_keys):
            self.fishing_line_angle += 1
            print(self.fishing_line_angle)
        if mouse_pressed_keys[0] and self.rope == None and not self.fishing:
            self.create_fishing_line()
            self.fishing=True
            self.prepare_fishing_line()
        if self.delay%12==0:
            self.frame+=1
            if self.state == 0:
                if self.frame>(len(self.idle_anim)-1):
                    self.frame = 0
            elif self.state == 1:
                if self.frame>(len(self.throw_anim)-1):
                    self.frame = 0
                    self.state = 0
            elif self.state == 2:
                if self.frame>(len(self.pull_anim)-1):
                    self.frame = 0
                    self.state = 0
        if self.state==0:
            cr.screen.blit(self.idle_anim[self.frame], [self.pos[0]+self.boat_sprite.get_width()-self.idle_anim[0].get_width()+20, self.pos[1]-10])
        elif self.state==1:
            cr.screen.blit(self.throw_anim[self.frame], [self.pos[0]+self.boat_sprite.get_width()-self.idle_anim[0].get_width()+20, self.pos[1]-10])
        elif self.state==2:
            cr.screen.blit(self.pull_anim[self.frame], [self.pos[0]+self.boat_sprite.get_width()-self.idle_anim[0].get_width()+20, self.pos[1]-10])
        self.draw_boat()
        if self.fishing:
            self.rope_screen.fill([0, 0, 0])
            self.prepare_fishing_line()
            self.down_rect.y=360+self.line_length
            self.old_len = len(self.y_points)
            self.rope.update([mouse_collider], delta_time=cr.event_holder.dt/10)
            if not (self.rope.lowest_point[0] in self.y_points):
                self.y_points.append(self.rope.lowest_point[0])
            #self.moving = True
            if cr.event_holder.mouse_held_keys[0] and ((pg.K_LSHIFT in held_keys) or (pg.K_RSHIFT in held_keys)):
                if (self.line_length<300):
                    self.line_length+=1
            if not mouse_pressed_keys[0] and not cr.event_holder.mouse_held_keys[0] and not self.recreated:
                self.create_fishing_line()
                self.recreated = True
                self.y_points = []
                self.state = 1
            if self.recreated:
                #print(self.rope.moving)
                self.rope.draw(self.rope_screen)
                
                if (self.recall_fishing_line):
                    if (self.old_len-len(self.y_points) == 0):
                        self.moving = False
                    if not self.set_angle:
                        self.fishing_line_angle = 90
                        self.set_angle = True
                    if not self.moving:
                        self.cover_rect.y-=12
                        
                    if (self.cover_rect.y <= self.pos[1]):
                        self.cover_rect.y = 720
                        self.rope = None
                        self.rope_screen.fill([0, 0, 0])
                        self.recreated = False
                        self.recreated = False
                        self.recall_fishing_line = False
                        self.set_angle = False
                        self.fishing = False
                        self.y_points = []
                        self.moving = True
                        self.line_length = 100
                    pygame.draw.rect(self.rope_screen, [0, 0, 0], self.cover_rect)
                
                if (pg.K_SPACE in pressed_keys) or (pg.K_SPACE in held_keys) and not self.recall_fishing_line:
                    self.recall_fishing_line = True
                    self.state = 2
                    #self.fishing = False
cloud_sprites = [utils.scale_image(pygame.image.load("assets/Spritesheets//bg/cloud1.png").convert(), 2), utils.scale_image(pygame.image.load("assets/Spritesheets//bg/cloud2.png").convert(), 1)]
for cloud_sprite in cloud_sprites:
    cloud_sprite.set_colorkey([106, 190, 48])

class Cloud:
    def __init__(self, x, elevation, type_):
        self.pos = [x, elevation]
        self.type = type_
        self.speed = 1.5
        self.crossed = False
    def update(self):
        self.pos[0]+=self.speed
        cr.screen.blit(cloud_sprites[self.type], self.pos)
        if (self.pos[0]>1180+cloud_sprites[self.type].get_width()/2):
            self.crossed = True
    def regen(self):
        self.pos = [random.randint(-(1280+cloud_sprites[self.type].get_width()), 0-cloud_sprites[self.type].get_width()), random.randint(0, 150)]
        self.type = random.randint(0, 1)
        self.crossed = False
class CloudManager:
    def __init__(self):
        self.clouds = [Cloud(random.randint(-1280, 0), random.randint(0, 150), random.randint(0, 1)) for i in range(20)]
    def update(self):
        num_cloud = -1
        for cloud in self.clouds:
            num_cloud+=1
            if not cloud.crossed:
                cloud.update()
            else:
                self.clouds[num_cloud].regen()
class WaveManager:
    def __init__(self):
        self.wave_sprites = []
        self.wave_sprite_scale = 2.041467304625199
        for i in range(10):
            self.wave_sprites.append(utils.scale_image(pygame.image.load("assets/Spritesheets//wave/wave00"+str(i)+".png").convert(), self.wave_sprite_scale))
            self.wave_sprites[i].set_colorkey([0, 0, 0])
        for i in range(6):
            self.wave_sprites.append(utils.scale_image(pygame.image.load("assets/Spritesheets//wave/wave01"+str(i)+".png").convert(), self.wave_sprite_scale))
            self.wave_sprites[i+10].set_colorkey([0, 0, 0])
        self.waves = []
        for i in range(11):
            self.waves.append([[i*116.36363636363636, 360-self.wave_sprites[0].get_height()+30], 0])
        self.delay = 0
    def update(self):
        self.delay+=1
        for wave in self.waves:
            cr.screen.blit(self.wave_sprites[wave[1]], wave[0])
            if self.delay%8==0:
                wave[1]+=1
                if (wave[1]>(len(self.wave_sprites)-1)):
                    wave[1] = 0          
cloud_manager = CloudManager()
wave_manager = WaveManager()
player = Player()
ocean_rect = pygame.Rect(0, 360, 1280, 360)
ocean_color = [99, 155, 255]
sea_bed = utils.scale_image(pygame.image.load("assets/Spritesheets//bg/seabed.png").convert())
utils.swap_color(sea_bed, [69, 40, 60], [0, 0, 0])
sea_bed.set_colorkey([0, 0, 0])
while not cr.event_holder.should_quit:
    cr.screen.fill((120, 171, 200))
    cr.event_holder.get_events()
    pressed_keys = cr.event_holder.pressed_keys
    mouse_pressed_keys = cr.event_holder.mouse_pressed_keys
    held_keys = cr.event_holder.held_keys
    released_keys = cr.event_holder.released_keys
    pygame.draw.rect(cr.screen, ocean_color, ocean_rect)
    cr.screen.blit(sea_bed, [0, 720-sea_bed.get_height()])
    cloud_manager.update()
    #print(cr.event_holder.final_fps)
    player.update()
    wave_manager.update()
    if player.fishing and player.recreated:
        cr.screen.blit(player.rope_screen, (0, 0))
    fish_manager.update()
    #cr.screen.blit(pygame.transform.flip(cr.screen, True, False), (0, 0))
    pg.display.update()