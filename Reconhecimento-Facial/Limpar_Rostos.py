import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OUTmMmgnd1NZh3QIDYvqAZvD3Rv4cJjS")
API_SECRET = os.getenv("TTvZC61AT3b71riYHtspWvU7CrYaNo7k")
OUTER_ID = "ChamadaAlunos"

BASE_URL = "https://api-us.faceplusplus.com/facepp/v3"

def api_post(endpoint, data=None):
    payload = {"api_key": API_KEY, "api_secret": API_SECRET}
    if data:
        payload.update(data)
    resp = requests.post(f"{BASE_URL}/{endpoint}", data=payload)
    resp.raise_for_status()
    return resp.json()

def remover_todos_rostos():
    try:
        # 1) Pega todos os face_tokens do FaceSet
        detail = api_post("faceset/getdetail", data={"outer_id": OUTER_ID})
        face_tokens = detail.get("face_tokens", [])

        if not face_tokens:
            print("FaceSet já está vazio.")
            return

        # 2) Remove todos de uma vez
        tokens_str = ",".join(face_tokens)
        res = api_post("faceset/removeface", data={
            "outer_id": OUTER_ID,
            "face_tokens": tokens_str
        })
        print(f"Rostos removidos: {res.get('face_count', 0)}")
    except Exception as e:
        print("Erro ao remover rostos:", e)

if __name__ == "__main__":
    confirmar = input("Tem certeza que deseja remover todos os rostos do FaceSet? (s/n) ")
    if confirmar.lower() == "s":
        remover_todos_rostos()
        print("Todos os rostos foram removidos.")
    else:
        print("Operação cancelada.")