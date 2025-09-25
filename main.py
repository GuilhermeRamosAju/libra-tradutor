import cv2
import mediapipe as mp
import asyncio
import websockets
import threading

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

def classificar_gesto(landmarks):
    polegar = landmarks.landmark[4].y
    indicador = landmarks.landmark[8].y
    medio = landmarks.landmark[12].y
    anelar = landmarks.landmark[16].y
    minimo = landmarks.landmark[20].y

    if indicador < medio and indicador < anelar and indicador < minimo:
        return "SINAL: 1"
    elif indicador < medio and medio < anelar and minimo > medio:
        return "SINAL: 2"
    elif indicador < medio and medio < anelar and anelar < minimo:
        return "SINAL: 3"
    elif todos_baixos([indicador, medio, anelar, minimo], polegar):
        return "SINAL: PUNHO"
    elif indicador < polegar:
        return "SINAL: A"
    else:
        return "SINAL: B"


def todos_baixos(dedos, polegar):
    """Verifica se todos os dedos estão dobrados em relação ao polegar"""
    return all(dedo > polegar for dedo in dedos)


def capturar_video():
    cap = cv2.VideoCapture(0)

    with mp_hands.Hands(max_num_hands=1) as hands:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            gesto = None
            if results.multi_hand_landmarks:
                for lm in results.multi_hand_landmarks:
                    mp_draw.draw_landmarks(frame, lm, mp_hands.HAND_CONNECTIONS)
                    gesto = classificar_gesto(lm)

            if gesto:
                asyncio.run(enviar_traducao(gesto))

            cv2.imshow("Reconhecimento LIBRAS", frame)
            if cv2.waitKey(1) & 0xFF == 27:  # ESC
                break

    cap.release()
    cv2.destroyAllWindows()

async def enviar_traducao(texto):
    uri = "ws://localhost:8765"
    try:
        async with websockets.connect(uri) as websocket:
            await websocket.send(texto)
    except Exception as e:
        print("Erro ao conectar ao servidor:", e)

if __name__ == "__main__":
    capturar_video()
