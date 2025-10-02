import pyxel

class Personagem:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.largura = 24
        self.altura = 24
        self.vida = 100
        self.velo = 1.5
        self.direcao = 0   # 0 = direita, 1 = esquerda
        self.frame = 1 # controla a animação do boneco
        self.vy = 0 # velocidade da gravidade
        self.chao = y
        self.no_chao = True
        self.invulneravel = False
        self.tempo_invulneravel = 0
        self.duracao_invulneravel = 30  # fps
        self.sofrendo_dano = False
        self.tempo_dano = 0
        self.duracao_dano = 30  # fps
        self.dash_ativo = False
        self.dash_duracao = 10          # duração do dash em frames
        self.dash_velo = 4.5            # velocidade do dash
        self.dash_cooldown = 30         # tempo de recarga do dash
        self.tempo_dash = 0             # frame em que o dash começou
        self.tempo_ultimo_dash = -60    # último frame em que o dash foi usado
        self.travado = False
        self.objetos = []

    def movimento(self):
        if self.vida <= 0:
            return
        
        movendo = False

        if self.invulneravel:
            if pyxel.frame_count - self.tempo_invulneravel > self.duracao_invulneravel:
                self.invulneravel = False

        if self.sofrendo_dano:
            if pyxel.frame_count - self.tempo_dano > self.duracao_dano:
                self.sofrendo_dano = False  # libera o movimento
            return

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
        if (pyxel.btn(pyxel.KEY_W) or pyxel.btn(pyxel.KEY_UP)) and self.no_chao:
            self.vy = -5
            self.no_chao = False

        if not self.no_chao:
            self.vy += 0.3
            self.y += self.vy
            self.verificar_colisao(self.objetos)

        if (pyxel.btnp(pyxel.KEY_SHIFT) or pyxel.btnp(pyxel.KEY_LSHIFT)) and not self.dash_ativo:
            if pyxel.frame_count - self.tempo_ultimo_dash > self.dash_cooldown:
                self.dash_ativo = True
                self.tempo_dash = pyxel.frame_count
                self.tempo_ultimo_dash = pyxel.frame_count

        # Se dash estiver ativo, mover rapidamente e ignorar controle normal
        if self.dash_ativo:
            if pyxel.frame_count - self.tempo_dash <= self.dash_duracao:
                if self.direcao == 0:
                    self.x += self.dash_velo
                else:
                    self.x -= self.dash_velo
                return  # ignora controles enquanto dashing
            else:
                self.dash_ativo = False

        #limites da tela com o personagem
        if self.x < 0:
            self.x = 0
        if self.x + self.largura > 240: 
            self.x = 240 - self.largura

        # Fix do dash ultrapassar a tela
        if self.x < 0:
            self.x, self.y = 0, 54
        elif self.x > 240:
            self.x, self.y = 216, 54

        # escolha do frame
        if not self.no_chao:  # no ar (pulo animado)
            self.frame = (pyxel.frame_count // 8) % 4
        elif movendo:  # andando
            self.frame = (pyxel.frame_count // 8) % 4
        else:  # parado
            self.frame = 1

    def verificar_colisao(self, objetos):
        tocou_chao = False  # controle local
        colidiu = None

        for obj in objetos:
            #    colisão em cima do objeto
            if (self.x + self.largura > obj.x and
                self.x < obj.x + obj.largura and
                self.y + self.altura >= obj.y and
                self.y + self.altura <= obj.y + 7 and
                self.vy >= 0):
                
                self.y = obj.y - self.altura
                self.vy = 0
                tocou_chao = True
                colidiu = obj

            #  colisão embaixo do objeto
            elif (self.x + self.largura > obj.x and
                self.x < obj.x + obj.largura and
                self.y <= obj.y + obj.altura and
                self.y >= obj.y + obj.altura - 7 and
                self.vy < 0):
                
                self.y = obj.y + obj.altura
                self.vy = 0
                colidiu = obj

            # --- colisão lateral
            elif (self.y + self.altura > obj.y and
                self.y < obj.y + obj.altura):

                # bateu pela direita
                if self.x + self.largura >= obj.x and self.x < obj.x and self.velo > 0:
                    self.x = obj.x - self.largura
                    colidiu = obj

                # bateu pela esquerda
                if self.x <= obj.x + obj.largura and self.x > obj.x and self.velo > 0:
                    self.x = obj.x + obj.largura + 1
                    colidiu = obj

        # só considera no chão se realmente tocou o chão
        self.no_chao = tocou_chao
        return colidiu

    def desenhar(self):
        u = self.frame * self.largura

        if not self.no_chao:  
            v = 2 * self.altura  # linha do pulo (linha 2)
        else:
            v = self.direcao * self.altura  # direita (0) ou esquerda (1)

        if self.vida <= 0:
            # sprite de morte
            u, v = 24, 72
            pyxel.blt(self.x, self.y, 0, u, v, self.largura, self.altura, 3)
            return

        if self.sofrendo_dano:
            # sprite de dano
            u, v = 0, 72
            pyxel.blt(self.x, self.y, 0, u, v, self.largura, self.altura, 3)
            return

        if self.dash_ativo:
            pyxel.circ(self.x + self.largura // 2, self.y + self.altura // 2, 2, 7)

        pyxel.blt(self.x, self.y, 0, u, v, self.largura, self.altura, 3)

class GerenciadorFases:
    def __init__(self):
        self.fase_atual = 0
        self.arquivos = [
            'imagens/fase_0.png',
            'imagens/fase_1.png',
            'imagens/fase_2.png',
            'imagens/fase_3.png',
            'imagens/fase_4.png',
            'imagens/fase_5.png',
            'imagens/fase_6.jpeg',
            'imagens/fase_7.png',
            'imagens/fase_8.png', 
            'imagens/fase_9.png',
            'imagens/fase_10.png'
        ]
        self.arquivos_morte = [
            None,  # fase 0 não tem imagem de morte
            'imagens/fase_1_morte.png',
            'imagens/fase_2_morte.png', 
            'imagens/fase_3_morte.png',
            'imagens/fase_4_morte.png',
            'imagens/fase_5_morte.png',
            'imagens/fase_6_morte.png',
            'imagens/fase_7_morte.png',
            'imagens/fase_8_morte.png',
            'imagens/fase_9_morte.png'
        ]
        self.total_fases = len(self.arquivos)

    def carregar(self):
        pyxel.image(2).load(0, 0, self.arquivos[self.fase_atual])

    def carregar_morte(self):
        if self.arquivos_morte[self.fase_atual]:
            pyxel.image(2).load(0, 0, self.arquivos_morte[self.fase_atual])

    def avancar(self):
        if self.fase_atual < self.total_fases - 1:
            self.fase_atual += 1
            self.carregar()

    def reiniciar(self):
        self.fase_atual = 0
        self.carregar()

class Objetos:
    def __init__(self, x, y, largura, altura, cor, is_porta = False, is_morte = False, is_perigo = False, is_vida = False, is_porta_falsa = False, is_fim = False):
        self.x = x
        self.y = y
        self.largura = largura
        self.altura = altura
        self.cor = cor
        self.is_fim = is_fim
        self.is_porta = is_porta
        self.is_morte = is_morte
        self.is_perigo = is_perigo
        self.is_vida = is_vida
        self.is_porta_falsa = is_porta_falsa

    def atualizar(self):
        pass

    def desenhar(self):
        if self.cor != 0:
            pyxel.rect(self.x, self.y, self.largura, self.altura, self.cor)

class Morcego:
    def __init__(self, x, y, amplitude, velocidade):
        self.x = x
        self.y = y
        self.cor = 0
        self.y_inicial = y  # guarda o ponto inicial
        self.amplitude = amplitude # até onde ele pode subir/descer
        self.velocidade = velocidade
        self.direcao = 1  # 1 = descendo, -1 = subindo
        self.is_fim = False
        self.is_perigo = True
        self.is_porta = False
        self.is_morte = False
        self.is_vida = False
        self.is_porta_falsa = False

        # cada pixel do morcego em relação ao ponto (dx, dy)
        self.pixels = [
            (4, 1), (3, 0), (5, 0), (3, 1), 
            (1, 3), (0, 2), (1, 2), (2, 2), 
            (1, 3), (2, 4), (3, 5), (4, 6), 
            (6, 4), (7, 3), (8, 2), (7, 3), 
            (5, 1), (7, 2), (3, 2), (4, 2), 
            (5 ,2), (5, 5), (6, 2), (3, 3),
            (4, 3), (5, 3), (2, 3), (6, 3),
            (4, 4), (5, 4), (3, 4), (4, 5)
        ]

        # bounding box (pra colisão simples)
        self.largura = 9
        self.altura = 7

    def atualizar(self):
        # Move para cima/baixo
        self.y += self.velocidade * self.direcao

        # Se chegou no limite, inverte a direção
        if self.y >= self.y_inicial + self.amplitude:
            self.direcao = -1
        elif self.y <= self.y_inicial - self.amplitude:
            self.direcao = 1
    
    def desenhar(self):
        for dx, dy in self.pixels:
            pyxel.pset(int(self.x + dx), int(self.y + dy), self.cor)

class Vida:
    def __init__(self, x, y, personagem):
        self.x = x
        self.y = y
        self.personagem = personagem
        self.largura = 54  
        self.altura = 9 
        self.max_vida = 100 

    def desenhar(self):
        # calcula índice da linha
        linha = (self.max_vida - self.personagem.vida) // 10

        # garante que não ultrapasse o último frame (10)
        if linha > 10:
            linha = 10

        pyxel.blt(self.x, self.y, 1, 0, linha * self.altura, self.largura, self.altura, 3)

class Coração:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.largura = 10
        self.altura = 9
        self.velo = 0
        self.is_fim = False
        self.is_perigo = False
        self.is_porta = False
        self.is_morte = False
        self.is_vida = True
        self.is_porta_falsa = False

        # cada pixel do morcego em relação ao ponto (dx, dy)
        self.pixels_dentro = [
            (2, 1), (3, 1), (6, 1), (7, 1), 
            (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (8, 2),
            (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3),
            (1, 4), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4),
            (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (7, 5),
            (3 ,6), (4, 6), (5, 6), (6, 6),
            (4, 7), (5, 7),
        ]

        self.pixels_fora = [
            (2, 0), (3,0), (6, 0), (7, 0),
            (1, 1), (4, 1), (5, 1), (8, 1),
            (0, 2), (9, 2),
            (0, 3), (9, 3),
            (0, 4), (9, 4),
            (1, 5), (8, 5),
            (2, 6), (7, 6),
            (3, 7), (6, 7),
            (4, 8), (5, 8)
        ]

    def atualizar(self):
        pass

    def desenhar(self):
        for dx, dy in self.pixels_dentro:
            pyxel.pset(int(self.x + dx), int(self.y + dy), 8)

        for dx, dy in self.pixels_fora:
            pyxel.pset(int(self.x + dx), int(self.y + dy), 0)
            

class Jogo:
    def __init__(self):
        self.fases = []

        self.objetos_fase0 = []
        self.objetos_fase1 = []
        self.objetos_fase2 = []
        self.objetos_fase3 = []
        self.objetos_fase4 = []
        self.objetos_fase5 = []
        self.objetos_fase6 = []
        self.objetos_fase7 = []
        self.objetos_fase8 = []
        self.objetos_fase9 = []
        self.objetos_fase10 = []

        self.objeto_por_fase = []
        self.fase_atual = 0
        self.estado = 'menu'   # 'menu', 'jogando', 'controles'
        self.opcoes = ['Jogar', 'Controles', 'Sair']
        self.opcao_coords = []  # vai guardar as posições de cada botão

        self.personagem = Personagem(0, 95)
        self.vida = Vida(177, 9, self.personagem)

        self.spawn_por_fase = {
            0: (0, 95),
            1: (10, 50), 
            2: (0, 90), 
            3: (23, 63), 
            4: (0, 90), 
            5: (0, 95), 
            6: (0, 88), 
            7: (0, 54),
            8: (0, 71), 
            9: (0, 90),
            10: (30, 100)
        }

        self.objetos_fase0.append(Objetos(0, 119, 240, 16, 0)) # chao
        self.objetos_fase0.append(Objetos(200, 95, 10, 24, 0, is_porta = True))   # Teleporte

        self.objetos_fase1.append(Objetos(0, 103, 94, 1, 0))#  chao
        self.objetos_fase1.append(Objetos(170, 103, 185, 1, 0))#  chao
        self.objetos_fase1.append(Objetos(94, 130, 76, 1, 0, is_morte = True))#  agua
        self.objetos_fase1.append(Objetos(165, 0, 10, 25, 0))#  teto/parede caverna ao final da caverna
        self.objetos_fase1.append(Objetos(165, 20, 52, 5, 0))#  teto/parede caverna ao final da caverna
        self.objetos_fase1.append(Objetos(222, 20, 10, 28, 0))#  teto/parede caverna ao final da caverna
        self.objetos_fase1.append(Objetos(227, 38, 13, 10, 0))#  teto/parede caverna ao final da caverna
        self.objetos_fase1.append(Objetos(151, 68, 25, 8, 0))#  plataforma
        self.objetos_fase1.append(Objetos(100, 91, 14, 8, 0))#  plataforma
        self.objetos_fase1.append(Objetos(95, 54, 16, 8, 0)) #  plataforma
        self.objetos_fase1.append(Objetos(239, 49, 1, 51, 0, is_porta = True)) #  teleporte
        self.objetos_fase1.append(Morcego(139, 69, 18, 0.4)) # morcego
        self.objetos_fase1.append(Morcego(55, 75, 18, 0.4)) # morcego
        

        self.objetos_fase2.append(Objetos(0, 105, 23, 1, 0)) # chão
        self.objetos_fase2.append(Objetos(205, 104, 11, 1, 0)) # chão
        self.objetos_fase2.append(Objetos(216, 87, 23, 1, 0)) # chão
        self.objetos_fase2.append(Objetos(239, 41, 1, 64, 0, is_porta = True)) # teleporte
        self.objetos_fase2.append(Objetos(30, 134, 169, 1, 0, is_morte= True)) # buraco/chão falso
        self.objetos_fase2.append(Objetos(0, 54, 2, 51, 0)) # parede para não sair da imagem da fase
        self.objetos_fase2.append(Objetos(17, 16, 1, 25, 0)) # teto/parede
        self.objetos_fase2.append(Objetos(17, 15, 13, 1, 0)) # teto/parede
        self.objetos_fase2.append(Objetos(29, 0, 1, 15, 0)) # teto/parede
        self.objetos_fase2.append(Objetos(30, 0, 132, 1, 0)) # teto/parede
        self.objetos_fase2.append(Objetos(162, 0, 1, 16, 0)) # teto/parede
        self.objetos_fase2.append(Objetos(162, 16, 55, 1, 0)) # teto/parede
        self.objetos_fase2.append(Objetos(216, 16, 1, 25, 0)) # teto/parede
        self.objetos_fase2.append(Objetos(216, 41, 24, 1, 0)) # teto/parede
        self.objetos_fase2.append(Objetos(35, 67, 15, 5, 0)) # plataforma
        self.objetos_fase2.append(Objetos(71, 53, 13, 5, 0)) # plataforma
        self.objetos_fase2.append(Objetos(92, 68, 3, 1, 0)) # mini-plataforma 
        self.objetos_fase2.append(Objetos(128, 73, 12, 5, 0)) # plataforma
        self.objetos_fase2.append(Objetos(102, 1, 1, 20, 0, is_perigo= True)) # Obstaculo
        self.objetos_fase2.append(Objetos(165, 58, 12, 5, 0)) # plataforma
        self.objetos_fase2.append(Morcego(150, 62, 18, 0.4)) # morcego


        self.objetos_fase3.append(Objetos(0, 106, 240, 1, 0, is_morte= True))
        self.objetos_fase3.append(Objetos(239, 34, 1, 30, 0, is_porta = True))
        self.objetos_fase3.append(Objetos(0, 130, 240, 5, 1)) # listra no chão para a imagem ficar uniforme
        self.objetos_fase3.append(Objetos(23, 69, 11, 5, 0)) # plataforma
        self.objetos_fase3.append(Objetos(75, 67, 8, 5, 0)) # plataforma
        self.objetos_fase3.append(Objetos(135, 60, 10, 5, 0)) # plataforma
        self.objetos_fase3.append(Objetos(185, 62, 9, 5, 0)) # plataforma
        self.objetos_fase3.append(Objetos(235, 69, 10, 5, 0)) # plataforma
        self.objetos_fase3.append(Objetos(203, 77, 7, 5, 0)) # plataforma
        self.objetos_fase3.append(Objetos(216, 0, 1, 33, 0)) # teto
        self.objetos_fase3.append(Objetos(217, 32, 23, 1, 0)) # teto
        self.objetos_fase3.append(Morcego(206, 35, 18, 0.4)) # morcego
        self.objetos_fase3.append(Morcego(107, 40, 18, 0.4)) # morcego
        self.objetos_fase3.append(Morcego(158, 40, 18, 0.4)) # morcego
        self.objetos_fase3.append(Morcego(55, 40, 18, 0.4)) # morcego

        self.objetos_fase4.append(Objetos(0, 105, 51, 1, 0)) # chão
        self.objetos_fase4.append(Objetos(56, 134, 123, 1, 0, is_morte= True)) # agua
        self.objetos_fase4.append(Objetos(184, 105, 56, 1, 0)) # chão
        self.objetos_fase4.append(Objetos(239, 0, 1, 105, 0, is_porta= True)) # teleporte
        self.objetos_fase4.append(Objetos(75, 85, 10, 1, 0)) # plataforma
        self.objetos_fase4.append(Objetos(123, 58, 20, 1, 0)) # plataforma
        self.objetos_fase4.append(Morcego(100, 60, 18, 0.4)) # morcego
        self.objetos_fase4.append(Morcego(180, 70, 18, 0.8)) # morcego
        self.objetos_fase4.append(Coração(143, 48))  #Vida

        self.objetos_fase5.append(Objetos(0, 96, 18, 1, 0)) # plataforma
        self.objetos_fase5.append(Objetos(21, 110, 22, 1, 0)) # plataforma
        self.objetos_fase5.append(Objetos(51, 134, 39, 1, 0, is_morte= True)) # água
        self.objetos_fase5.append(Objetos(91, 71, 9, 1, 0)) # plataforma
        self.objetos_fase5.append(Objetos(113, 134, 12, 1, 0, is_morte= True)) # plataforma falsa
        self.objetos_fase5.append(Objetos(133, 78, 1, 57, 0)) # parede
        self.objetos_fase5.append(Objetos(133, 78, 9, 1, 0)) # plataforma
        self.objetos_fase5.append(Objetos(142, 78, 1, 37, 0)) # parede
        self.objetos_fase5.append(Objetos(143, 114, 97, 1, 0)) # chão
        self.objetos_fase5.append(Objetos(239, 50, 1, 64, 0, is_porta= True)) # porta
        self.objetos_fase5.append(Morcego(70, 75, 18, 0.7)) # morcego
        self.objetos_fase5.append(Morcego(111, 35, 18, 0.5)) # morcego
        self.objetos_fase5.append(Morcego(130, 42, 18, 0.7)) # morcego
        self.objetos_fase5.append(Morcego(175, 75, 18, 0.7)) # morcego

        self.objetos_fase6.append(Objetos(0, 89, 24, 1, 0)) # plataforma
        self.objetos_fase6.append(Objetos(70, 66, 20, 1, 0)) # plataforma
        self.objetos_fase6.append(Objetos(138, 82, 20, 1, 0)) # plataforma
        self.objetos_fase6.append(Objetos(170, 116, 70, 1, 0)) # plataforma
        self.objetos_fase6.append(Objetos(30, 134, 140, 1, 0, is_morte= True)) # lava
        self.objetos_fase6.append(Objetos(95, 15, 8, 17, 0)) # teto
        self.objetos_fase6.append(Objetos(239, 80, 1, 38, 0, is_porta_falsa= True, is_perigo= True)) # porta falsa
        self.objetos_fase6.append(Objetos(214, 46, 26, 1, 0)) # plataforma
        self.objetos_fase6.append(Objetos(239, 14, 1, 30, 0, is_porta= True)) # porta
        self.objetos_fase6.append(Morcego(185, 75, 18, 0.9)) # morcego
        self.objetos_fase6.append(Morcego(55, 65, 18, 0.5)) # morcego
        self.objetos_fase6.append(Morcego(105, 65, 18, 0.7)) # morcego

        self.objetos_fase7.append(Objetos(0, 57, 53, 1, 0)) # plataforma
        self.objetos_fase7.append(Objetos(58, 67, 21, 1, 0)) # plataforma
        self.objetos_fase7.append(Objetos(83, 77, 21, 1, 0)) # plataforma
        self.objetos_fase7.append(Objetos(104, 87, 70, 1, 0)) # plataforma
        self.objetos_fase7.append(Objetos(190, 77, 25, 1, 0)) # plataforma
        self.objetos_fase7.append(Objetos(210, 54, 30, 1, 0)) # plataforma
        self.objetos_fase7.append(Objetos(205, 4, 35, 1, 0)) # teto
        self.objetos_fase7.append(Objetos(0, 15, 20, 1, 0)) # teto
        self.objetos_fase7.append(Objetos(26, 27, 40, 1, 0)) # teto
        self.objetos_fase7.append(Objetos(78, 15, 20, 1, 0)) # teto
        self.objetos_fase7.append(Objetos(239, 5, 1, 49, 0, is_porta= True)) # porta
        self.objetos_fase7.append(Morcego(80, 40, 18, 0.6)) # morcego
        self.objetos_fase7.append(Morcego(135, 60, 16, 0.8)) # morcego

        self.objetos_fase8.append(Objetos(0, 90, 60, 1, 0)) # chão
        self.objetos_fase8.append(Objetos(0, 72, 12, 1, 0)) # chão
        self.objetos_fase8.append(Objetos(61, 120, 179, 1, 0, is_morte= True)) 
        self.objetos_fase8.append(Objetos(105, 86, 10, 1, 0)) # plataforma
        self.objetos_fase8.append(Objetos(127, 75, 10, 1, 0)) # plataforma
        self.objetos_fase8.append(Objetos(180, 100, 60, 1, 0)) # chão
        self.objetos_fase8.append(Morcego(70, 68, 20, 0.8)) # morcego
        self.objetos_fase8.append(Morcego(82, 70, 25, 0.5)) # morcego
        self.objetos_fase8.append(Morcego(145, 68, 20, 0.8)) # morcego
        self.objetos_fase8.append(Morcego(157, 70, 25, 0.5)) # morcego
        self.objetos_fase8.append(Objetos(171, 0, 1, 20, 0)) # parede
        self.objetos_fase8.append(Objetos(178, 20, 1, 12, 0)) # parede
        self.objetos_fase8.append(Objetos(185, 32, 1, 8, 0)) # parede
        self.objetos_fase8.append(Objetos(217, 40, 1, 14, 0)) # parede
        self.objetos_fase8.append(Objetos(230, 55, 1, 12, 0)) # parede
        self.objetos_fase8.append(Objetos(230, 67, 10, 1, 0)) # parede
        self.objetos_fase8.append(Objetos(239, 67, 1, 33, 0, is_porta= True)) # porta

        self.objetos_fase9.append(Objetos(0, 115, 60, 1, 0)) # chão
        self.objetos_fase9.append(Objetos(60, 134, 180, 1, 0, is_morte= True))
        self.objetos_fase9.append(Objetos(40, 75, 12, 1, 0)) # plataforma
        self.objetos_fase9.append(Objetos(93, 64, 12, 1, 0)) # plataforma
        self.objetos_fase9.append(Objetos(102, 31, 18, 1, 0)) # plataforma
        self.objetos_fase9.append(Objetos(150, 45, 13, 1, 0)) # plataforma
        self.objetos_fase9.append(Objetos(130, 79, 13, 1, 0)) # plataforma
        self.objetos_fase9.append(Objetos(203, 70, 10, 1, 0)) # plataforma
        self.objetos_fase9.append(Objetos(0, 0, 240, 1, 0)) # plataforma
        self.objetos_fase9.append(Objetos(130, 0, 1, 5, 0, is_perigo= True)) # parte do teto onde acontece o dano
        self.objetos_fase9.append(Objetos(150, 0, 1, 5, 0, is_perigo= True)) # parte do teto onde acontece o dano
        self.objetos_fase9.append(Objetos(170, 0, 1, 5, 0, is_perigo= True)) # parte do teto onde acontece o dano
        self.objetos_fase9.append(Objetos(190, 0, 1, 5, 0, is_perigo= True)) # parte do teto onde acontece o dano
        self.objetos_fase9.append(Objetos(239, 40, 1, 60, 0, is_porta= True)) # porta
        self.objetos_fase9.append(Morcego(115, 70, 25, 1.5)) # morcego
        self.objetos_fase9.append(Morcego(68, 50, 25, 1.0)) # morcego
        self.objetos_fase9.append(Morcego(180, 50, 20, 1.2)) # morcego

        self.objetos_fase10.append(Objetos(0, 113, 240, 1, 0)) # chão
        self.objetos_fase10.append(Objetos(0, 0, 1, 135, 0)) # parede para nao sair da tela
        self.objetos_fase10.append(Objetos(0, 239, 1, 135, 0)) # parede para nao sair da tela
        self.objetos_fase10.append(Objetos(180, 60, 1, 53, 0, is_fim= True))

        self.objeto_por_fase = [self.objetos_fase0,
                                self.objetos_fase1,
                                self.objetos_fase2,
                                self.objetos_fase3,
                                self.objetos_fase4,
                                self.objetos_fase5,
                                self.objetos_fase6,
                                self.objetos_fase7,
                                self.objetos_fase8,
                                self.objetos_fase9,
                                self.objetos_fase10
                                ]
        
        self.objetos = self.objeto_por_fase[self.fase_atual]
        self.personagem.objetos = self.objetos

        self.fases = GerenciadorFases()

        pyxel.init(240, 135, title='Cavern Escape', fps=60, display_scale=8)
        pyxel.mouse(True)  # habilitar mouse

        pyxel.image(0).load(0, 0, 'imagens/personagem_caverna.png')
        pyxel.image(1).load(0, 0, 'imagens/vida.png')
        self.fases.carregar()

        pyxel.run(self.update, self.draw)

    def spawn_personagem(self, x, y):
        self.personagem.x = x
        self.personagem.vy = 0
        self.personagem.no_chao = True  # assume que está no chão

        # encontra o chão mais próximo abaixo da posição 'x'
        chao_encontrado = None
        menor_dist = float('inf')

        for obj in self.objetos:
            if obj.y >= y and obj.x <= x <= obj.x + obj.largura:
                dist = obj.y - y
                if dist < menor_dist:
                    menor_dist = dist
                    chao_encontrado = obj

        if chao_encontrado:
            self.personagem.y = chao_encontrado.y - self.personagem.altura
        else:
            self.personagem.y = y

    def reiniciar_jogo(self):
        self.fases.reiniciar()
        self.objetos = self.objeto_por_fase[0]
        self.personagem.objetos = self.objetos
        self.personagem.vida = 100
        self.personagem.travado = False
        self.spawn_personagem(0, 95)
        
        # Voltar intens coletaveis para o jogo ao reiniciar
        self.objetos_fase4.append(Coração(143, 48))  #Vida

        self.estado = "jogando"

    def update(self):
        if self.personagem.travado:
            return
        
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
            obj_colidido = self.personagem.verificar_colisao(self.objetos)

            for obj in self.objetos:
                obj.atualizar()

            if obj_colidido and obj_colidido.is_porta:
                self.fases.avancar()
                self.objetos = self.objeto_por_fase[self.fases.fase_atual]
                self.personagem.objetos = self.objetos

                # pega spawn correto da fase
                x, y = self.spawn_por_fase[self.fases.fase_atual]
                self.spawn_personagem(x, y)

            if obj_colidido and obj_colidido.is_morte:
                self.personagem.vida = 0
                self.fases.carregar_morte()

            if obj_colidido and obj_colidido.is_porta_falsa:
                self.personagem.x, self.personagem.y = 0, 63

            if obj_colidido and obj_colidido.is_perigo and not self.personagem.invulneravel:
                self.personagem.vida -= 10 
                self.personagem.invulneravel = True
                self.personagem.tempo_invulneravel = pyxel.frame_count
                self.personagem.sofrendo_dano = True
                self.personagem.tempo_dano = pyxel.frame_count
                

                if self.personagem.vida > 0:
                    x, y = self.spawn_por_fase[self.fases.fase_atual]
                    self.spawn_personagem(x, y)
                
                else:
                    self.fases.carregar_morte()  
                return
            
            if obj_colidido and obj_colidido.is_vida:
                self.personagem.vida += 20
                if self.personagem.vida > 100:
                    self.personagem.vida = 100
                self.objetos.remove(obj_colidido)

            if obj_colidido and obj_colidido.is_fim:
                self.personagem.travado = True
                pyxel.mouse(True)
                return

            if pyxel.btnp(pyxel.KEY_M):
                pyxel.mouse(True)
                self.estado = 'menu'

        elif self.estado == 'controles':
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.estado = 'menu'

    def draw(self):
        pyxel.cls(0)
        obj_colidido = self.personagem.verificar_colisao(self.objetos)

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
            # desenha a imagem da fase
            pyxel.blt(0, 0, 2, 0, 0, 240, 135, 0)

            # título da fase
            if self.fases.fase_atual == 0:
                pyxel.text(7, 10, 'ENTRADA DA CAVERNA', 7)
            elif self.fases.fase_atual == 10:
                pyxel.text(7, 10, 'SAIDA DA CAVERNA - FIM', 7)
            else:
                pyxel.text(7, 10, f'Fase {self.fases.fase_atual}', 7)

            # desenha objetos
            for obj in self.objetos:
                obj.desenhar()

            # morte / reiniciar
            if self.personagem.vida == 0:
                pyxel.mouse(True)
                pyxel.blt(0, 0, 2, 0, 0, 240, 135, 0)
                pyxel.rect(99, 63, 45, 10, 0)

                cor = 10 if (99 <= pyxel.mouse_x <= 144 and 63 <= pyxel.mouse_y <= 73) else 7
                pyxel.text(104, 66, 'Reiniciar', cor)

                if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    if 99 <= pyxel.mouse_x <= 144 and 63 <= pyxel.mouse_y <= 73:
                        self.reiniciar_jogo()
            
            if obj_colidido and obj_colidido.is_fim:
                pyxel.mouse(True)
                pyxel.blt(0, 0, 2, 0, 0, 240, 135, 0)
                pyxel.rect(70, 63, 100, 10, 0)

                pyxel.rect(50, 40, 140, 10, 0)
                pyxel.text(56, 43, 'PARABÊNS! VOCE ESCAPOU DA CAVERNA,', 7)
                pyxel.rect(68, 50, 104, 10, 0)
                pyxel.text(74, 53, 'E CHEGOU AO SEU DESTINO!', 7)

                cor = 10 if (75 <= pyxel.mouse_x <= 140 and 63 <= pyxel.mouse_y <= 73) else 7
                pyxel.text(75, 66, 'DESEJA JOGAR NOVAMENTE?', cor)

                if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    if 75 <= pyxel.mouse_x <= 140 and 63 <= pyxel.mouse_y <= 73:
                        self.reiniciar_jogo()

            # personagem
            self.personagem.desenhar()
            self.vida.desenhar()
            if self.personagem.vida == 0:
                pyxel.mouse(True)
            elif obj_colidido and obj_colidido.is_fim:
                pyxel.mouse(True)
            else:
                pyxel.mouse(False)
            
        elif self.estado == 'controles':
            pyxel.text(80, 15, 'CONTROLES:', 11)
            pyxel.text(60, 35, 'A / <-  = Esquerda', 2)
            pyxel.text(60, 50, 'D / ->  = Direita', 2)
            pyxel.text(60, 65, 'W / Cima = Pular', 2)
            pyxel.text(60, 80, 'Shift / L-Shift = Dash', 2)
            pyxel.text(60, 95, 'M = Voltar ao Menu', 2)
            pyxel.text(60, 115, 'Mouse Esquerdo = Voltar', 2)

Jogo()