import pyxel

class Personagem:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.largura = 24
        self.altura = 24
        self.velo = 1.5
        self.direcao = 0   # 0 = direita, 1 = esquerda
        self.frame = 1 # controla a animação do boneco
        self.vy = 0 # velocidade da gravidade
        self.chao = y
        self.no_chao = True

    def movimento(self):
        movendo = False

        # esquerda e direita
        if pyxel.btn(pyxel.KEY_A) or pyxel.btn(pyxel.KEY_LEFT):
            self.x -= self.velo
            self.direcao = 1
            movendo = True
        elif pyxel.btn(pyxel.KEY_D) or pyxel.btn(pyxel.KEY_RIGHT):
            self.x += self.velo
            self.direcao = 0
            movendo = True

        # pulo
        if (pyxel.btn(pyxel.KEY_SPACE) or pyxel.btn(pyxel.KEY_UP)) and self.no_chao:
            self.vy = -5
            self.no_chao = False

        # gravidade
        if not self.no_chao:
            self.vy += 0.3
            self.y += self.vy

            if self.y >= self.chao:
                self.y = self.chao
                self.vy = 0
                self.no_chao = True

        # escolha do frame
        if not self.no_chao:  # no ar (pulo animado)
            self.frame = (pyxel.frame_count // 8) % 4
        elif movendo:  # andando
            self.frame = (pyxel.frame_count // 8) % 4
        else:  # parado
            self.frame = 1

    def desenhar(self):
        u = self.frame * self.largura

        if not self.no_chao:  
            v = 2 * self.altura  # linha do pulo (linha 2)
        else:
            v = self.direcao * self.altura  # direita (0) ou esquerda (1)

        pyxel.blt(self.x, self.y, 0, u, v, self.largura, self.altura, 3)

class Cenarios:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def desenhar(self, img, larg, alt):
        pyxel.blt(0, 0, img, 0, 0, larg, alt, 0, scale=1)

class Jogo:
    def __init__(self):
        self.estado = 'menu'   # 'menu', 'jogando', 'controles'
        self.opcoes = ['Jogar', 'Controles', 'Sair']
        self.opcao_coords = []  # vai guardar as posições de cada botão

        self.personagem = Personagem(0, 95)
        self.tela_inicial = Cenarios(0, 0)

        pyxel.init(240, 135, title='Cavern Escape', fps=60, display_scale=8)
        pyxel.mouse(True)  # habilitar mouse

        pyxel.image(0).load(0, 0, 'imagens/personagem_caverna.png')
        pyxel.image(1).load(0, 0, 'imagens/cenario_inicial.png')

        pyxel.run(self.update, self.draw)

    def update(self):
        if self.estado == 'menu':
            # verificar clique do mouse em cada opção
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                for i, (x, y, w, h) in enumerate(self.opcao_coords):
                    if x <= pyxel.mouse_x <= x + w and y <= pyxel.mouse_y <= y + h:
                        if self.opcoes[i] == 'Jogar':
                            self.estado = 'jogando'
                        elif self.opcoes[i] == 'Controles':
                            self.estado = 'controles'
                        elif self.opcoes[i] == "Sair":
                            pyxel.quit()

        elif self.estado == 'jogando':
            self.personagem.movimento()

            if self.personagem.x < 0 and (pyxel.btn(pyxel.KEY_A) or pyxel.btn(pyxel.KEY_LEFT)):
                self.personagem.velo = 0
            elif self.personagem.x + self.personagem.largura > 240 and (pyxel.btn(pyxel.KEY_D) or pyxel.btn(pyxel.KEY_RIGHT)):
                self.personagem.velo = 0
            else:
                self.personagem.velo = 1.5

            if pyxel.btnp(pyxel.KEY_M):
                pyxel.mouse(True)
                self.estado = 'menu'

        elif self.estado == 'controles':
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.estado = 'menu'

    def draw(self):
        pyxel.cls(0)

        if self.estado == 'menu':
            pyxel.text(90, 20, 'CAVERN ESCAPE', 11)

            self.opcao_coords = []
            for i, texto in enumerate(self.opcoes):
                x, y = 95, 60 + i * 20
                w, h = 50, 12  # largura e altura do 'botão'
                cor = 10 if (x <= pyxel.mouse_x <= x + w and y <= pyxel.mouse_y <= y + h) else 7

                # desenhar retângulo do botão
                pyxel.rect(x - 5, y - 3.5, w, h, 2)
                pyxel.text(x, y, texto, cor)

                # guardar posição para clique
                self.opcao_coords.append((x - 5, y - 3.5, w, h))

        elif self.estado == 'jogando':
            self.tela_inicial.desenhar(1, 259, 135)
            self.personagem.desenhar()
            pyxel.mouse(False)

        elif self.estado == 'controles':
            pyxel.text(80, 40, 'CONTROLES:', 11)
            pyxel.text(60, 60, 'A / <-  = Esquerda', 2)
            pyxel.text(60, 75, 'D / ->  = Direita', 2)
            pyxel.text(60, 90, 'Espaco / Cima = Pular', 2)
            pyxel.text(60, 110, 'Mouse Esquerdo = Voltar', 2)

Jogo()
