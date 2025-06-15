import socket
from _thread import *
import pickle

# 서버 설정
server = "127.0.0.1"  # 로컬호스트 IP (테스트용)
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    print(str(e))

s.listen(2)  # 동시에 2명까지 접속 대기 (필요에 따라 늘릴 수 있음)
print("Waiting for a connection, Server Started")

# 플레이어 데이터를 저장할 딕셔너리. {id: {'x': x, 'y': y, ...}}
players = {}
player_count = 0

def threaded_client(conn, player_id):
    """
    각 클라이언트와의 통신을 담당하는 함수 (스레드에서 실행)
    """
    global player_count
    # 클라이언트에게 플레이어 ID 전송
    conn.send(pickle.dumps(player_id))

    # 초기 플레이어 위치 전송
    # players[player_id] = {'x': 400, 'y': 300, 'seated': False} # 예시 데이터
    reply = ""
    while True:
        try:
            data = pickle.loads(conn.recv(2048))
            players[player_id] = data # 클라이언트로부터 받은 데이터로 업데이트

            if not data:
                print("Disconnected")
                break
            else:
                # 자신을 제외한 다른 모든 플레이어 정보 보내기
                reply = {p_id: p_data for p_id, p_data in players.items() if p_id != player_id}
                print("Received: ", data)
                print("Sending : ", reply)

            conn.sendall(pickle.dumps(reply))
        except:
            break

    print("Lost connection")
    conn.close()
    del players[player_id]
    player_count -= 1

while True:
    conn, addr = s.accept()
    print("Connected to:", addr)
    
    player_count += 1
    player_id = player_count # 간단하게 접속 순서로 ID 부여

    start_new_thread(threaded_client, (conn, player_id)) 