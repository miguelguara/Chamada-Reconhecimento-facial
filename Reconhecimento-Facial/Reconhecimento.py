import cv2
import requests
import os
import json
import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
from Limpar_Rostos import limpar_rostos

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


def log(msg):
    output_area.configure(state='normal')
    output_area.insert(tk.END, msg + "\n")
    output_area.see(tk.END)
    output_area.configure(state='disabled')
# ---------------------------
# Cadastro de alunos
# ---------------------------
def cadastrar_alunos():
    # caminho absoluto da pasta "alunos", mesmo diretório do script
    pasta = os.path.join(os.path.dirname(__file__), "alunos")

    if not os.path.exists(pasta):
        log("❌ Pasta 'alunos' não encontrada.")
        return

    arquivos = os.listdir(pasta)
    if not arquivos:
        log("⚠️ Nenhuma foto encontrada na pasta 'alunos'.")
        return

    for foto in arquivos:
        nome = os.path.splitext(foto)[0]
        caminho = os.path.join(pasta, foto)

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
            log(f"✅ {nome} cadastrado com sucesso.")
        else:
            log(f"❌ Nenhum rosto detectado em {foto}")

    salvar_tokens()

def adicionar_foto(event):
    caminhos = root.splitlist(event.data)
    for caminho in caminhos:
        if os.path.isfile(caminho):
            nome_arquivo = os.path.basename(caminho)
            destino = os.path.join("alunos", nome_arquivo)
            try:
                with open(caminho, "rb") as f_origem, open(destino, "wb") as f_dest:
                    f_dest.write(f_origem.read())
                log(f"📁 Foto adicionada: {nome_arquivo}")
            except Exception as e:
                log(f"❌ Erro ao adicionar {nome_arquivo}: {e}")

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
                    log(f"✅ {nome} está presente!")
                else:
                    log("❌ Rosto detectado, mas não corresponde a nenhum aluno.")
            else:
                log("❌ Nenhum rosto detectado.")

        if cv2.waitKey(1) & 0xFF == 27:  # ESC para sair
            break

    cap.release()
    cv2.destroyAllWindows()


# ---------------------------
# Execução (escolha o que rodar)
# ---------------------------
alunos_tokens = {}

root = TkinterDnD.Tk()
root.title("Chamada Escolar - Face++")
root.geometry("500x400")

tk.Button(root, text="Cadastrar Alunos", width=25, command=cadastrar_alunos).pack(pady=5)
tk.Button(root, text="Fazer Chamada", width=25, command=chamada_webcam).pack(pady=5)
tk.Button(root,text= "Limpar Rostos Da nuvem",width=25,command=limpar_rostos).pack(pady= 5)

instrucao = tk.Label(root, text="📌 Arraste fotos dos alunos para esta janela")
instrucao.pack(pady=5)

output_area = scrolledtext.ScrolledText(root, width=60, height=15, state='disabled')
output_area.pack(pady=10)

# Ativar Drag & Drop
root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', adicionar_foto)

root.mainloop()
