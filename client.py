import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import sys, threading, pygame, random, socket, math, time, pickle, pyautogui


class Game:
    def __init__(self):

        self.screen_size = (1600, 900)

        self.player_size = 15
        self.bullet_size = 3

        self.movement_speed = 5
        self.bulltet_speed = 10
        self.shot_d = 15
        self.max_packet_r_size = 4096
        self.max_packet_t_size = 1024
        

        pygame.init()
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("ELO Game")
        # self.screen = pygame.display.set_mode(self.screen_size, pygame.FULLSCREEN)
        self.screen = pygame.display.set_mode((1200,600))
        
        pygame.mixer.init()
        # pygame.mixer.music.load(os.path.join(os.getcwd(), "music.mp3"))
        # pygame.mixer.music.play(loops=1000)
        # self.shoot_sound = pygame.mixer.Sound(os.path.join(os.getcwd(), "shot.wav"))
        

        self.font = pygame.font.SysFont("Arial", 18)

        IP = input("Enter server IP address: ")
        self.network = Network(IP, 6968)
        

        id, x, y, color = self.network.connect()

        print(f"Identity: {id} {x} {y} {color}")
        
        self.player = Player(id, x, y, color)
        self.bullets = []
        self.bullet_id = 0

        self.ping = 0
        self.packet_r_size = 0
        self.packet_t_size = 0
        
        self.velX = 0
        self.velY = 0
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.mouse_button = False
        self.speed = 4


    def run_game(self):
        self.running = True
        
        shot_counter = 0
        self.data = {"id": self.player.id,
                    "x": self.player.x,
                    "y": self.player.y,
                    "c": self.player.color,
                    "b": []}
        
        net_client = threading.Thread(target=self.network_client, args=())
        net_client.start()
        time.sleep(3)
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    exit()
                    
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        pygame.quit()
                        exit()
                        
                    if event.key == pygame.K_a:
                        self.left_pressed = True
                    if event.key == pygame.K_d:
                        self.right_pressed = True
                    if event.key == pygame.K_w:
                        self.up_pressed = True
                    if event.key == pygame.K_s:
                        self.down_pressed = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.left_pressed = False
                    if event.key == pygame.K_d:
                        self.right_pressed = False
                    if event.key == pygame.K_w:
                        self.up_pressed = False
                    if event.key == pygame.K_s:
                        self.down_pressed = False
                if pygame.mouse.get_pressed()[0]:
                    self.mouse_button = True
                else:
                    self.mouse_button = False


            self.mouse_x, self.mouse_y = pygame.mouse.get_pos()
            self.player.r = math.atan2(self.player.y-self.mouse_y, self.player.x-self.mouse_x)*180.0/math.pi


            shot_counter = self.update_shot(shot_counter)


            self.update_player()
            self.updata_own_bullets()


            self.screen.fill((0, 0, 0))

            self.blit_player()
            self.blit_own_bullets()
            
            
            data = {"id": self.player.id,
                    "x": round(self.player.x),
                    "y": round(self.player.y),
                    "c": self.player.color,
                    "b": []}
            for bullet in self.bullets:
                data["b"].append((round(bullet.x), round(bullet.y)))
            self.data = data
            # print(data)
            
            
            try:
                self.blit_players()
                self.blit_bullets()
            except Exception as e:
                print(e)
            
            
            self.screen.blit(self.update_packet_size(), (10, 10))
            self.screen.blit(self.update_ping(), (10, 38))
            self.screen.blit(self.update_fps(), (10, 66))
            pygame.display.flip()
            self.clock.tick(60)



    def update_fps(self):
        fps = str(int(self.clock.get_fps()))
        fps_text = self.font.render(f"FPS: {fps}", 1, pygame.Color("white"))
        return fps_text

    def update_ping(self):
        ping_text = self.font.render(f"Ping: {self.ping}", 1, pygame.Color("white"))
        return ping_text
    
    def update_packet_size(self):
        ping_text = self.font.render(f"Packets size: transmit: {self.packet_t_size}/{self.max_packet_t_size} receive: {self.packet_r_size}/{self.max_packet_r_size}", 1, pygame.Color("white"))
        return ping_text


    def update_shot(self, counter):
        if self.mouse_button:
            if self.shot_d == counter:
                self.bullet_id = self.bullet_id + 1
                vx, vy = self.vectro_scale((self.mouse_x - self.player.x), (self.mouse_y - self.player.y), self.bulltet_speed)
                bullet = Bullet(self.player.id, self.bullet_id, self.player.x, self.player.y, vx, vy, self.player.color)
                self.bullets.append(bullet)
                # pygame.mixer.Sound.play(self.shoot_sound).set_volume(0.5)
                return 0
            return counter + 1
        return counter


    def blit_player(self):
        pygame.draw.circle(self.screen, self.player.color, (self.player.x, self.player.y), self.player_size, self.player_size)
        return True


    def update_player(self):
        self.velX = 0
        self.velY = 0
        if self.left_pressed and not self.right_pressed and self.player.x >= 0:
            self.velX = -self.speed
        if self.right_pressed and not self.left_pressed and self.player.x <= self.screen.get_width():
            self.velX = self.speed
        if self.up_pressed and not self.down_pressed and self.player.y >= 0:
            self.velY = -self.speed
        if self.down_pressed and not self.up_pressed and self.player.y <= self.screen.get_height():
            self.velY = self.speed
        if self.up_pressed and self.right_pressed and self.player.y >= 0 and self.player.x <= self.screen.get_width():
            self.velX, self.velY = self.vectro_scale(self.speed, -self.speed, self.speed)
        if self.down_pressed and self.right_pressed and self.player.y <= self.screen.get_height() and self.player.x <= self.screen.get_width():
            self.velX, self.velY = self.vectro_scale(self.speed, self.speed, self.speed)
        if self.down_pressed and self.left_pressed and self.player.y <= self.screen.get_height() and self.player.x >= 0:
            self.velX, self.velY = self.vectro_scale(-self.speed, self.speed, self.speed)
        if self.up_pressed and self.left_pressed and self.player.y >= 0 and self.player.x >= 0:
            self.velX, self.velY = self.vectro_scale(-self.speed, -self.speed, self.speed)

        self.player.x += self.velX
        self.player.y += self.velY


    def blit_own_bullets(self):
        for bullet in self.bullets:
            pygame.draw.circle(self.screen, bullet.color, (bullet.x, bullet.y), self.bullet_size, self.bullet_size)


    def updata_own_bullets(self):
        for bullet in self.bullets:
            bullet.x = bullet.x + bullet.vx
            bullet.y = bullet.y + bullet.vy
            if bullet.x < 0 or bullet.x > self.screen.get_width() or bullet.y < 0 or bullet.y > self.screen.get_height():
                self.bullets.remove(bullet)


    def blit_players(self):
        for p in self.reply:
            if p["id"] != self.player.id:
                pygame.draw.circle(self.screen, p["c"], (p["x"], p["y"]), self.player_size, self.player_size)
        return True


    def blit_bullets(self):
        for p in self.reply:
            if p["id"] != self.player.id:
                for b in p["b"]:
                    pygame.draw.circle(self.screen, p["c"], (b[0], b[1]), self.bullet_size, self.bullet_size)
        return True
    
    
    def vectro_scale(self, x, y, r):
        v_l = (x**2 + y**2)**0.5
        if v_l == 0:
            return 0, 0
        return x*r / v_l, y*r / v_l


    def network_client(self):
        while self.running:
            self.reply, self.ping, self.packet_t_size, self.packet_r_size = self.network.send(self.data, self.max_packet_r_size)
            # print(self.reply)



class Player:
    def __init__(self, id, x, y, color):
        self.id = id
        self.x = x
        self.y = y
        self.color = color

class Bullet:
    def __init__(self, player_id, id, x, y, vx, vy, color):
        self.player_id = player_id
        self.id = id
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color


class Network:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr = (host, port)

    def connect(self):
        self.client.connect(self.addr)
        identity = self.client.recv(2048).decode()
        arr = identity.split(";")
        id = int(arr[0])
        x = int(arr[1])
        y = int(arr[2])
        color = arr[3]
        color = (int(color[1:-1].split(",")[0]), int(color[1:-1].split(",")[1]), int(color[1:-1].split(",")[2]))
        return id, x, y, color

    def send(self, data, max_packet_size):
        try:
            data = pickle.dumps(data)
            
            packet_t_size =sys.getsizeof(data)
            
            start_time = time.time()
            self.client.send(data)
            reply = self.client.recv(max_packet_size)
            ping = round((time.time() - start_time) * 1000)
            
            packet_r_size = sys.getsizeof(reply)
            
            reply = pickle.loads(reply)
            
            return reply, ping, packet_t_size, packet_r_size
        except Exception as e:
            return e, "-", "-", "-"
        


game = Game()
game.run_game()
