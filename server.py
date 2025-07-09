import socket, random, threading, pickle
from datetime import datetime


class Player:
    def __init__(self, id, x, y, color):
        self.id = id
        self.x = x
        self.y = y
        self.color = color
        self.hits = 0

    def encode_identity(self):
        identity = f"{self.id};{self.x};{self.y};{self.color}"
        return identity


class Bullet:
    def __init__(self, player_id, x, y, color):
        self.player_id = player_id
        self.x = x
        self.y = y
        self.color = color



def threaded_client(conn, player):
    conn.send(str.encode(player.encode_identity()))

    while True:
        try:
            data = conn.recv(1024)

            if not data:
                conn.send(str.encode("Goodbye"))
                break
            else:
                msg = pickle.loads(data)


                for p in players:   # * Move player
                    if p.id == msg["id"]:
                        p.x = msg["x"]
                        p.y = msg["y"]
                        break

                for bullet in bullets:  # * Delete player bullets
                    if bullet.player_id == msg["id"]:
                        bullets.remove(bullet)


                color = msg["c"]
                for bullet_data in msg["b"]:    # * Create player bullets
                    bullet = Bullet(msg["id"], bullet_data[0], bullet_data[1], color)
                    bullets.append(bullet)


                
                reply = []
                for player in players:      # * Prepare reply
                    player_data = {"id": player.id, "x": player.x, "y": player.y, "c": player.color, "b": []}
                    for bullet in bullets:
                        if bullet.player_id == player.id:
                            player_data["b"].append((bullet.x, bullet.y))
                    reply.append(player_data)
                
                
                reply = pickle.dumps(reply)
                
                # print(f"R:{sys.getsizeof(data)}    T:{sys.getsizeof(reply)}")
                
                conn.send(reply)    # * Send reply
        except Exception as e:
            print(e)
            break
    print(f"\33[31mConnection Closed Player ID: {player.id} \33[0m")
    for p in players:       # * Remove player
        if p.id == player.id:
            players.remove(p)
    for b in bullets:       # * Remove bullet
        if b.player_id == player.id:
            bullets.remove(b)
    conn.close()



def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 1))
    local_ip_address = s.getsockname()[0]
    s.close()
    return local_ip_address



s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


server_ip = get_local_ip()

port = 6968

try:
    s.bind((server_ip, port))
except socket.error as e:
    print(str(e))

s.listen(2)
print(datetime.today().strftime('%Y-%m-%d-%H:%M:%S'), " Waiting for a connection ip:", str(server_ip), " port:", str(port))


currentId = 0
currentBulletId = [0]


players = []
bullets = []


while True:     # * Main loop for accepting connections
    conn, addr = s.accept()
    print(f"\33[32mConnected to: {addr}", end=" ")

    currentId = currentId + 1
    player = Player(currentId, random.randrange(100, 1000), random.randrange(100,500), (random.randrange(0,255),random.randrange(0,255),random.randrange(0,255)))
    players.append(player)

    print(f"Player ID: {currentId}\33[0m")

    threading.Thread(target=threaded_client, args=(conn, player,)).start()
