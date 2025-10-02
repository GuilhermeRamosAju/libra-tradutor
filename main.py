import cv2
import mediapipe as mp
import asyncio
import websockets

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

clientes = set()

def classificar_gesto(landmarks):
    dedo_indicador = landmarks.landmark[8].y
    dedo_polegar = landmarks.landmark[4].y
    return "A" if dedo_indicador < dedo_polegar else "B"

async def servidor_websocket(websocket):
    clientes.add(websocket)
    try:
        async for _ in websocket:
            pass
    finally:
        clientes.remove(websocket)

async def enviar_para_clientes(mensagem):
    if clientes:
        await asyncio.wait([cliente.send(mensagem) for cliente in clientes])

# ------------------------------
# Loop da câmera recebe o loop principal como parâmetro
# ------------------------------
def camera_loop(loop):
    cap = cv2.VideoCapture(0)
    with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7) as hands:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(rgb)

            if result.multi_hand_landmarks:
                for hand_landmarks in result.multi_hand_landmarks:
                    gesto = classificar_gesto(hand_landmarks)
                    print("Detectado gesto:", gesto) 
                    asyncio.run_coroutine_threadsafe(
                        enviar_para_clientes(f"Sinal reconhecido: {gesto}"),
                        loop
                    )
                    mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            cv2.imshow("Camera - Libras", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break

    cap.release()
    cv2.destroyAllWindows()

# ------------------------------
# Função principal
# ------------------------------
async def main():
    loop = asyncio.get_running_loop() 
    async with websockets.serve(servidor_websocket, "localhost", 8765):
        print("Servidor WebSocket rodando em ws://localhost:8765")
        await asyncio.to_thread(camera_loop, loop)

if __name__ == "__main__":
    asyncio.run(main())
