import cv2
import requests
import os
import json

API_KEY = "OUTmMmgnd1NZh3QIDYvqAZvD3Rv4cJjS"
API_SECRET = "TTvZC61AT3b71riYHtspWvU7CrYaNo7k"
FACESET_ID = "ChamadaAlunos"

ARQUIVO_MAPA = "alunos_tokens.json"  # onde salvamos os tokens

# ---------------------------
# Funções auxiliares
# ---------------------------
def salvar_tokens():
    with open(ARQUIVO_MAPA, "w") as f:
        json.dump(alunos_tokens, f)

def carregar_tokens():
    global alunos_tokens
    if os.path.exists(ARQUIVO_MAPA):
        with open(ARQUIVO_MAPA, "r") as f:
            alunos_tokens = json.load(f)
    else:
        alunos_tokens = {}

# ---------------------------
# Cadastro de alunos
# ---------------------------
def cadastrar_alunos():
    for foto in os.listdir("alunos"):
        nome = os.path.splitext(foto)[0]
        caminho = os.path.join("alunos", foto)

        with open(caminho, "rb") as f:
            detect_url = "https://api-us.faceplusplus.com/facepp/v3/detect"
            detect_response = requests.post(
                detect_url,
                files={"image_file": f},
                data={"api_key": API_KEY, "api_secret": API_SECRET}
            ).json()

        if detect_response.get("faces"):
            face_token = detect_response["faces"][0]["face_token"]
            alunos_tokens[face_token] = nome

            addface_url = "https://api-us.faceplusplus.com/facepp/v3/faceset/addface"
            requests.post(addface_url, data={
                "api_key": API_KEY,
                "api_secret": API_SECRET,
                "outer_id": FACESET_ID,
                "face_tokens": face_token
            })
            print(f"✅ {nome} cadastrado com sucesso.")
        else:
            print(f"❌ Nenhum rosto detectado em {foto}")

    salvar_tokens()


# ---------------------------
# Chamada via webcam
# ---------------------------
def chamada_webcam():
    carregar_tokens()

    cap = cv2.VideoCapture(0)
    print("📷 Pressione 'q' para capturar e verificar presença.")

    while True:
        ret, frame = cap.read()
        cv2.imshow("Chamada - Pressione Q", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.imwrite("frame_temp.jpg", frame)

            with open("frame_temp.jpg", "rb") as f:
                search_url = "https://api-us.faceplusplus.com/facepp/v3/search"
                response = requests.post(
                    search_url,
                    files={"image_file": f},
                    data={"api_key": API_KEY, "api_secret": API_SECRET, "outer_id": FACESET_ID}
                ).json()

            if response.get("results"):
                aluno = response["results"][0]
                if aluno["confidence"] > 80:
                    token = aluno["face_token"]
                    nome = alunos_tokens.get(token, "Desconhecido")
                    print(f"✅ {nome} está presente!")
                else:
                    print("❌ Rosto detectado, mas não corresponde a nenhum aluno.")
            else:
                print("❌ Nenhum rosto detectado.")

        if cv2.waitKey(1) & 0xFF == 27:  # ESC para sair
            break

    cap.release()
    cv2.destroyAllWindows()


# ---------------------------
# Execução (escolha o que rodar)
# ---------------------------
alunos_tokens = {}
cadastrar_alunos()   # roda uma vez para registrar
chamada_webcam() 