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
fish_sprites = [[pygame.image.load("assets/Spritesheets/fish1/fish-000"+str(i)+".png").convert() for i in range(1, 4)], [pygame.image.load("assets/Spritesheets/fish3/fish-000"+str(i)+".png").convert() for i in range(1, 4)], [pygame.image.load("assets/Spritesheets/fish4/fish-000"+str(i)+".png").convert() for i in range(1, 4)], [pygame.image.load("assets/Spritesheets/fish2/fish2-00"+str(i)+".png").convert() for i in range(3)]]
fish_sprites[0] = [utils.scale_image(f, 3) for f in fish_sprites[0]]
fish_sprites[1] = [utils.scale_image(f, 3) for f in fish_sprites[1]]
fish_sprites[2] = [utils.scale_image(f, 3) for f in fish_sprites[2]]
fish_sprites[3] = [utils.scale_image(f, 3) for f in fish_sprites[3]]
[utils.swap_color(sprite, [102, 57, 49], [0, 0, 0]) for sprite in fish_sprites[0]]
[sprite.set_colorkey([0, 0, 0]) for sprite in fish_sprites[0]]
[sprite.set_colorkey([0, 0, 0]) for sprite in fish_sprites[1]]
[sprite.set_colorkey([0, 0, 0]) for sprite in fish_sprites[2]]
[sprite.set_colorkey([0, 0, 0]) for sprite in fish_sprites[3]]
pygame.init()
pygame.mixer.Channel(0).play(pygame.mixer.Sound('assets/Audio/background_track.wav'), -1)
pygame.mixer.Channel(0).set_volume(0.7)
pygame.mixer.Channel(1).play(pygame.mixer.Sound('assets/Audio/waves.wav'), -1)
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
triangle_wave = list(triangle(100, 50))
class Fish:
    def __init__(self, x, elevation, type_):
        self.pos = [x, elevation]
        self.orig_pos = [x, elevation]
        self.speed = 4
        self.crossed = False
        self.pattern = random.randint(0, 2)
        self.type = random.randint(0, len(fish_sprites)-2)
        if random.randint(0, 12) == 12:
            self.type= len(fish_sprites)-1
            self.speed = 6
        self.stage = -1
        self.adders = [4, 1, 0]
        self.adding = False
        self.delay = 0
        self.sprite = [s.copy() for s in fish_sprites[self.type]]
        self.frame = 0
        self.masks = [pygame.mask.from_surface(surf) for surf in self.sprite]
        self.caught = False
        self.food_req = random.randint(8, 10)
        self.alpha_surf = pygame.Surface([self.sprite[0].get_width(), self.sprite[0].get_height()])
        self.alpha_surf.fill([0, 0, 0])
        self.alpha = 0
        self.score = 1
        if self.food_req == 8:
            self.alpha = 0
            self.score = 1
        if self.food_req == 9:
            self.alpha = 60
            self.score = 0.6
        if self.food_req == 10:
            self.alpha = 120
            self.score = 0.3
        if self.type == len(fish_sprites)-1:
            self.score+=2
        self.alpha_surf.set_alpha(self.alpha)
        [self.sprite[n].blit(self.alpha_surf, [0, 0]) for n in range(len(self.sprite))]
    def update(self):
        global square_wave
        self.stage+=self.adders[self.pattern]
        self.delay+=1
        if self.delay%6==0:
            self.frame+=1
            if (self.frame>len(self.sprite)-1):
                self.frame = 0
        if (self.pattern == 1):
            if self.stage > len(triangle_wave)-1:
                self.stage = 0
        if not self.caught:
            self.pos[0]-=self.speed
            if (self.pattern==0):
                self.pos[1]=self.orig_pos[1]+(sin(radians(self.stage))*60)
                #self.sprite = pygame.transform.rotate(fish_sprites[self.type], degrees(asin(sin(radians(self.stage)))))
            if (self.pattern==1):
                self.pos[1]=self.orig_pos[1]+(triangle_wave[self.stage])
            if (self.pattern==2):
                if (self.delay%3==0):
                    self.stage+=1
                    if (self.stage>len(square_wave)-1):
                        self.stage=0
                self.pos[1]=self.orig_pos[1]+(square_wave[self.stage])*10
        
        if player.fishing and player.recreated:
            
            if player.rope is not None:
                if player.rope.lowest_point is not None:
                    bait_pos = [player.rope.lowest_point[0]-player.bait_sprite.get_width()/2, player.rope.lowest_point[1]]
                    if (self.masks[self.frame].overlap(player.bait_mask, [bait_pos[0]-self.pos[0], bait_pos[1]-self.pos[1]])!=None and ((not player.fished))) or (self.caught):
                        self.pos = bait_pos
                        if not self.caught:
                            player.fish+=self.score
                            player.fished = True
                        self.caught = True
        if self.masks[self.frame].overlap(player.mask, [player.player_pos[0]-self.pos[0], player.player_pos[1]-self.pos[1]])!=None:
            self.crossed = True
        cr.screen.blit(self.sprite[self.frame], self.pos)
        if (self.pos[0]<0):
            self.crossed = True
class FishManager:
    def __init__(self):
        self.fishes = [Fish(random.randint(1280, 1280*2), random.randint(475, 575), random.randint(0, 1)) for i in range(6)]
    def update(self):
        num_fish = -1
        for fish in self.fishes:
            num_fish+=1
            if not fish.crossed:
                fish.update()
            else:
                self.fishes.remove(self.fishes[num_fish])
        if len(self.fishes) == 0:
            self.fishes = [Fish(random.randint(1280, 1280*2), random.randint(475, 575), random.randint(0, 1)) for i in range(6)]
fish_manager = FishManager()
def outline_mask(img, loc, color=[255,255,255]):
    mask = pygame.mask.from_surface(img)
    mask_outline = mask.outline()
    n = 0
    for point in mask_outline:
        mask_outline[n] = (point[0] + loc[0], point[1] + loc[1])
        n += 1
    pygame.draw.polygon(cr.screen,color,mask_outline,3)
def get_outline_mask(img, loc):
    mask = pygame.mask.from_surface(img)
    mask_outline = mask.outline()
    n = 0
    for point in mask_outline:
        mask_outline[n] = (point[0] + loc[0], point[1] + loc[1])
        n += 1
    return mask_outline
class Slider:
    def __init__(self, pos, font, div):
        self.pos = pos
        self.font = pygame.font.SysFont(font, 18)
        self.div = div
        self.rect_surf = pygame.Surface((32, 32))
        self.mask = pygame.mask.from_surface(self.rect_surf)
        self.outlines = self.mask.outline()
        self.bg_surf = pygame.Surface((32, 32))
        self.bg_surf.set_colorkey((0, 0, 0))
        self.x_offset = 100
        self.bar_surf = pygame.Surface((120, 20))
        self.bar_surf.fill([99, 155, 255])
    def update(self):
        self.bg_surf.fill((0, 0, 0))
        self.overall_rect = pygame.Rect(self.pos[0], self.pos[1]-10, 120, 40)
        self.bar_rect = pygame.Rect(self.pos[0], self.pos[1], 120, 20)
        self.slider_rect = pygame.Rect(self.pos[0]+self.x_offset, self.pos[1]-10, 20, 40)
        if self.overall_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            self.x_offset = pygame.mouse.get_pos()[0]-self.pos[0]
        if ((pg.K_LSHIFT in pressed_keys) or (pg.K_RSHIFT in pressed_keys)):
            self.x_offset-=10
        if ((pg.K_LCTRL in pressed_keys) or (pg.K_RCTRL in pressed_keys)):
            self.x_offset+=10
        if self.x_offset > 100:
            self.x_offset = 100
        if self.x_offset < 80:
            self.x_offset = 80
        #pygame.draw.rect(cr.screen, (0, 0, 255), self.overall_rect)
        pygame.draw.rect(cr.screen, [99, 155, 255], self.bar_rect)
        outline_mask(self.bar_surf, [self.bar_rect.x, self.bar_rect.y])
        pygame.draw.rect(cr.screen, (255, 255, 255), self.slider_rect)
        self.value = round(self.x_offset/100, 1)
        if not self.div:
            self.value *= 10
        value = self.font.render(str(self.value), False, (1, 1, 1), (0, 0, 0))
        value.set_colorkey((0, 0, 0))
        pygame.draw.lines(self.bg_surf, (1, 1, 1), True, self.outlines, 3)
        self.bg_surf.blit(value, [self.bg_surf.get_width()/2-value.get_width()/2, self.bg_surf.get_height()/2-value.get_height()/2])
        cr.screen.blit(self.bg_surf, [self.pos[0]+self.overall_rect.w+25, self.pos[1]-(self.bar_rect.h/4)])
def get_pixel(surf : pygame.Surface, color):
    for j in range(surf.get_height()):
        for i in range(surf.get_width()):
            if surf.get_at([i, j]).r == color[0] and surf.get_at([i, j]).g == color[1] and surf.get_at([i, j]).b == color[2]:
                return [i, j]
class Player:
    def __init__(self) -> None:
        self.throw_anim = []
        self.idle_anim = []
        self.pull_anim = []
        self.length_bar = pygame.Surface([225*2.2, 30])
        self.length_bar.set_colorkey([0, 0, 0])
        self.length_bar.fill([255, 255, 255])
        self.fished = False
        self.bait_slider = Slider([(1280-180)/2, 70], "Arial", True)
        self.restart = False
        self.bait_sprite = pygame.image.load("assets/Spritesheets/bait.png").convert()
        self.bait_sprite.set_colorkey([255, 255, 255])
        self.orig_bait_sprite = pygame.image.load("assets/Spritesheets/bait.png").convert()
        self.orig_bait_sprite.set_colorkey([255, 255, 255])
        for i in range(6):
            self.throw_anim.append(pygame.transform.flip(utils.scale_image(pg.image.load("assets/Spritesheets//throw/throw"+str(i)+".png").convert()), False, False))
            self.throw_anim[i].set_colorkey([255, 255, 255])
        for i in range(5):
            self.idle_anim.append(pygame.transform.flip(utils.scale_image(pg.image.load("assets/Spritesheets//idle/idle00"+str(i)+".png").convert()), False, False))
            self.idle_anim[i].set_colorkey([0, 0, 0])
        self.idle_anim[0].set_colorkey([255, 255, 255])
        for i in range(8):
            self.pull_anim.append(pygame.transform.flip(utils.scale_image(pg.image.load("assets/Spritesheets//pull/pull00"+str(i)+".png").convert()), False, False))
            self.pull_anim[i].set_colorkey([255, 255, 255])
        self.boat_sprite = pygame.transform.flip(utils.scale_image(pg.image.load("assets/Spritesheets//boat.png").convert()), False, False)
        self.boat_sprite.set_colorkey([255, 255, 255])
        self.pos = [0, 360 - self.boat_sprite.get_height()+8]
        self.line_length = 70
        self.bait_size = 1
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
        self.moving = True
        self.frame = -1
        self.delay = 0
        self.state = 0
        self.length_bar_pos = [(1280-495)/2, 20]
        self.length_bar_outline = get_outline_mask(self.length_bar, self.length_bar_pos)
        self.length_bar.fill([0, 0, 0])
        self.casting_sound = pygame.mixer.Sound('assets/Audio/casting.wav')
        self.winding_sound = pygame.mixer.Sound('assets/Audio/winding_rod.wav')
        self.player_pos = [self.pos[0]+self.boat_sprite.get_width()-self.idle_anim[0].get_width()+20, self.pos[1]-10]
        self.rope_throw_positions = [[get_pixel(sprite, [103, 57, 49])[0]+self.player_pos[0], get_pixel(sprite, [103, 57, 49])[1]+self.player_pos[1]] for sprite in self.throw_anim]
        self.rope_pull_positions = [[get_pixel(sprite, [103, 57, 49])[0]+self.player_pos[0], get_pixel(sprite, [103, 57, 49])[1]+self.player_pos[1]] for sprite in self.pull_anim]
        self.idle_pos = [get_pixel(self.idle_anim[0], [103, 57, 49])[0]+self.player_pos[0], get_pixel(self.idle_anim[0], [103, 57, 49])[1]+self.player_pos[1]]
        self.delays = [12, 8, 8]
        self.bait_mask = None
        self.angle_pointer = utils.scale_image(pygame.transform.flip(pygame.image.load("assets/Spritesheets/arrow.png").convert(), True, False))
        self.angle_pointer.set_colorkey([255, 255, 255])
    def create_fishing_line(self):
        self.rope = Rope(self.rope_throw_positions[0][0], self.rope_throw_positions[0][0], self.line_length, self.line_length//11)
    def prepare_fishing_line(self):
        self.rope.gravity.x = resultant_gravitational_force*cos(radians(self.fishing_line_angle))
        self.rope.gravity.y = resultant_gravitational_force*sin(radians(self.fishing_line_angle))
    def draw_boat(self):
        cr.screen.blit(self.boat_sprite, self.pos)
    def update(self):
        self.delay +=1
        self.length_bar.fill([0, 0, 0])
        if mouse_pressed_keys[0] and self.rope == None and not self.fishing:
            self.create_fishing_line()
            self.fishing=True
            self.prepare_fishing_line()
        if self.delay%self.delays[self.state]==0:
            self.frame+=1
        if self.state == 0:
            if self.frame>(len(self.idle_anim)-1):
                self.frame = 0
            else:
                if self.rope!=None:
                    self.rope.points[0].pos.x = self.idle_pos[0]
                    self.rope.points[0].pos.y = self.idle_pos[1]
            if self.rope != None:
                if self.delay%12==0:
                    self.frame= 0 
                    #self.rope.points[0].pos.x = self.rope_throw_positions[self.frame][0]
                    #self.rope.points[0].pos.y = self.rope_throw_positions[self.frame][1]
        elif self.state == 1:
            if self.frame>(len(self.throw_anim)-1):
                self.frame = 0
                self.state = 0
            else:
                self.rope.points[0].pos.x = self.rope_throw_positions[self.frame][0]
                self.rope.points[0].pos.y = self.rope_throw_positions[self.frame][1]
        elif self.state == 2:
            if self.frame>(len(self.pull_anim)-1):
                self.frame = 0
                self.state = 0
            else:
                if self.rope!=None:
                    self.rope.points[0].pos.x = self.rope_pull_positions[self.frame][0]
                    self.rope.points[0].pos.y = self.rope_pull_positions[self.frame][1]
        
        if self.state==0:
            cr.screen.blit(self.idle_anim[self.frame], self.player_pos)
            self.mask = pygame.mask.from_surface(self.idle_anim[self.frame])
        elif self.state==1:
            cr.screen.blit(self.throw_anim[self.frame], self.player_pos)
            self.mask = pygame.mask.from_surface(self.throw_anim[self.frame])
        elif self.state==2:
            cr.screen.blit(self.pull_anim[self.frame], self.player_pos)
            self.mask = pygame.mask.from_surface(self.pull_anim[self.frame])
        self.draw_boat()
        pygame.draw.rect(self.length_bar, [255, 255, 255], pygame.Rect(0, 0, self.line_length*2.2, 30))
        cr.screen.blit(self.length_bar, self.length_bar_pos)
        pygame.draw.polygon(cr.screen,[255, 255, 255],self.length_bar_outline,3)
        
        if self.fishing:
            self.rope_screen.fill([0, 0, 0])
            self.prepare_fishing_line()
            self.down_rect.y=360+self.line_length
            self.old_len = len(self.y_points)
            self.rope.update([mouse_collider], delta_time=cr.event_holder.dt/10)
            if not (self.rope.lowest_point[0] in self.y_points):
                self.y_points.append(self.rope.lowest_point[0])
            #self.moving = True
            if cr.event_holder.mouse_held_keys[0] and (pg.K_UP in held_keys) and not self.recreated:
                if (self.line_length<225):
                    self.line_length+=3
            if cr.event_holder.mouse_held_keys[0] and (pg.K_DOWN in held_keys) and not self.recreated:
                if (self.line_length>70):
                    self.line_length-=3
        
            if not mouse_pressed_keys[0] and not cr.event_holder.mouse_held_keys[0] and not self.recreated:
                self.create_fishing_line()
                self.recreated = True
                self.y_points = []
                self.state = 1
                self.casting_sound.play()
            if not self.recreated:
                if (pg.K_RIGHT in pressed_keys) or (pg.K_RIGHT in held_keys):
                    if self.fishing_line_angle > 30:
                        self.fishing_line_angle -= 2

                    print(self.fishing_line_angle)
                if (pg.K_LEFT in pressed_keys) or (pg.K_LEFT in held_keys):
                    if self.fishing_line_angle < 143:
                        self.fishing_line_angle += 2
                    print(self.fishing_line_angle)
                cr.screen.blit(pygame.transform.rotate(self.angle_pointer, 0-self.fishing_line_angle), self.idle_pos)
            if self.recreated:
                #print(self.rope.moving)
                self.rope.draw(self.rope_screen)
                
                if (self.recall_fishing_line):
                    if (self.old_len-len(self.y_points) == 0):
                        self.moving = False
                    if not self.set_angle:
                        self.fishing_line_angle = 90
                        self.set_angle = True
                    if not self.moving and self.delay%3==0:
                        if len(self.rope.points) > 1:
                            self.rope.points.pop(len(self.rope.points)-1)
                            self.rope.points[len(self.rope.points)-1].child = None
                            #self.rope.lowest_point = [self.rope.points[len(self.rope.points)-1].pos.x, self.rope.points[len(self.rope.points)-1].pos.y]              
                        else:
                            self.rope.points = []
                    if (self.rope.points == []):
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
                        self.line_length = 70
                        self.fished = False
                    pygame.draw.rect(self.rope_screen, [0, 0, 0], self.cover_rect)
                
                if (pg.K_SPACE in pressed_keys) or (pg.K_SPACE in held_keys) and not self.recall_fishing_line:
                    self.recall_fishing_line = True
                    self.state = 2
                    self.winding_sound.play()
                    #self.fishing = False
        #self.bait_slider.update()
#103
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
        if player.rope is not None:
            if player.rope.lowest_point is not None:
                player.bait_sprite = player.orig_bait_sprite
                player.bait_mask = pygame.mask.from_surface(player.bait_sprite)
                cr.screen.blit(player.bait_sprite, [player.rope.lowest_point[0]-player.bait_sprite.get_width()/2, player.rope.lowest_point[1]])
                pygame.draw.circle(cr.screen, [155, 173, 183], player.rope.lowest_point, 5*1)
                #print(player.rope.lowest_point[1]-player.rope.orig_pos[1])
    fish_manager.update()
    #print(player.fish)
    #cr.screen.blit(pygame.transform.flip(cr.screen, True, False), (0, 0))
    pg.display.update()