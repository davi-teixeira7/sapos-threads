from flask import Flask, render_template, Response
import threading
import random
import time
import json
import queue

app = Flask(__name__)

DISTANCIA_TOTAL = 50

SAPOS = [
    {"nome": "Gamabunta",  "imagem": "https://static.wikia.nocookie.net/naruto/images/8/84/Gamabunta.png/revision/latest?cb=20130701190020&path-prefix=pt-br", "cor": "#b70bbc"},
    {"nome": "Gamakichi",  "imagem": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQbHby0rCdTZKKiERWEIXghsKbK75UoP6VnRw&s", "cor": "#B8C044"},
    {"nome": "Gamatatsu",  "imagem": "https://static.wikia.nocookie.net/naruto/images/f/f5/Gamatatsu.PNG/revision/latest?cb=20160702223810&path-prefix=pt-br", "cor": "#ae2727"},
    {"nome": "Fukasaku",   "imagem": "https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcSOBeeaq6ks_N-f-Z3FQ5ooH4UYsbfylbnTl5j2ws-kbcbPWkHi", "cor": "#15836f"},
]

corrida_ativa = False
fila_eventos = queue.Queue()


class Sapo(threading.Thread):
    def __init__(self, dados, fila, lock_vencedor, vencedor_ref):
        super().__init__()
        self.dados = dados
        self.nome = dados["nome"]
        self.posicao = 0
        self.fila = fila
        self.lock_vencedor = lock_vencedor
        self.vencedor_ref = vencedor_ref
        self.daemon = True

    def run(self):
        while self.posicao < DISTANCIA_TOTAL:
            with self.lock_vencedor:
                if self.vencedor_ref[0] is not None:
                    return

            avanco = random.randint(1, 5)
            self.posicao = min(self.posicao + avanco, DISTANCIA_TOTAL)

            self.fila.put({
                "tipo": "progresso",
                "nome": self.nome,
                "posicao": self.posicao,
            })

            if self.posicao >= DISTANCIA_TOTAL:
                with self.lock_vencedor:
                    if self.vencedor_ref[0] is None:
                        self.vencedor_ref[0] = self.nome
                        self.fila.put({"tipo": "vencedor", "nome": self.nome})
                return

            time.sleep(random.uniform(0.1, 0.5))


@app.route("/")
def index():
    return render_template("index.html", sapos=SAPOS, distancia=DISTANCIA_TOTAL)


@app.route("/iniciar")
def iniciar():
    global corrida_ativa, fila_eventos

    fila_eventos = queue.Queue()
    corrida_ativa = True

    lock_vencedor = threading.Lock()
    vencedor_ref = [None]

    threads = []
    for dados in SAPOS:
        t = Sapo(dados, fila_eventos, lock_vencedor, vencedor_ref)
        threads.append(t)

    for t in threads:
        t.start()

    def monitorar():
        for t in threads:
            t.join()
        fila_eventos.put({"tipo": "fim"})

    threading.Thread(target=monitorar, daemon=True).start()

    return ("", 204)


@app.route("/stream")
def stream():
    def gerar():
        while True:
            try:
                evento = fila_eventos.get(timeout=30)
                yield f"data: {json.dumps(evento)}\n\n"
                if evento["tipo"] in ("fim",):
                    break
            except queue.Empty:
                yield "data: {\"tipo\": \"ping\"}\n\n"

    return Response(gerar(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
