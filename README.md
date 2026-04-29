# 🦇 Cavern Escape - Pyxel Platformer

Um jogo de plataforma retro 2D, no estilo "Metroidvania/Precision Platformer", desenvolvido inteiramente em Python utilizando a engine **Pyxel**. Controle um explorador através de 11 níveis desafiadores em uma caverna repleta de morcegos, lavas, plataformas falsas e armadilhas mortais.

![Demonstração do Jogo](cavern_escape_gameplay.gif)

## 🚀 O Problema que Resolve
Este projeto foi construído como um estudo aprofundado no desenvolvimento de jogos do zero (sem o uso de engines visuais como Unity ou Godot). Ele aplica conceitos matemáticos e lógicos de programação de baixo nível para criar motores físicos, tratamento de colisões manuais e manipulação de sprites (Pixel Art) em tempo real, servindo como um forte case de Engenharia de Software voltada para Game Dev.

## ✨ Funcionalidades (Features)
* **Motor Físico Customizado:** Implementação matemática de gravidade, aceleração no eixo Y e atrito simulado para um pulo responsivo e preciso.
* **Sistema Avançado de Colisões (Bounding Boxes):** Diferenciação de contato por eixos, permitindo que o personagem suba em plataformas por cima (tocando o chão), mas seja bloqueado se bater a cabeça no teto ou se colidir lateralmente nas paredes.
* **Mecânicas de Combate e Sobrevivência:**
  * **I-Frames (Invulnerability Frames):** Sistema temporário de proteção (30 fps) ao receber dano, impedindo a morte instantânea do jogador (One-Hit KO).
  * **Dash:** Habilidade de corrida rápida ativada via `Shift` com sistema de recarga (Cooldown) gerenciado por contagem de frames.
* **Inimigos Dinâmicos:** A classe `Morcego` possui rotinas de movimentação vertical autônomas com amplitudes e velocidades variadas que desafiam o *timing* do jogador.
* **Level Design e Gerenciamento de Fases:** Arquitetura de 11 fases distintas interligadas por "portas/teleportes". Cada fase carrega dinamicamente seu próprio array de objetos (plataformas, poços de morte, corações de cura) e seu respectivo plano de fundo.
* **Máquina de Estados (State Machine):** Gerenciamento inteligente do fluxo do jogo, transitando perfeitamente entre Menu Principal, Tela de Controles, Loop Principal de Jogo e Tela de Game Over/Vitória.

## 🛠️ Tecnologias Utilizadas
* **Python 3.x:** Linguagem base de estruturação orientada a objetos.
* **Pyxel:** Uma *retro game engine* fantástica para Python inspirada em consoles de 8-bits, utilizada para renderização do display (240x135 px), leitura de inputs do teclado/mouse, limite de taxa de quadros (60 fps) e renderização de imagens e sprites em malhas de pixels limitadas a 16 cores.

## ⚙️ Como Executar o Projeto

**1. Clone o repositório:**
```bash
git clone https://github.com/uemuralc/cavern-escape
cd cavern-escape
```

**2. Instale a engine Pyxel:**

```Bash
pip install pyxel
```

**3. Execute o jogo:**
(Certifique-se de estar na pasta raiz do projeto, onde a pasta imagens/ se encontra)

```Bash
python cavern-escape.py
```

## 🎮 Controles do Jogo

**A / Seta Esquerda:** Andar para a esquerda

**D / Seta Direita:** Andar para a direita

**W / Seta Cima:** Pular

**Shift / L-Shift:** Executar o Dash

**M:** Pausar e voltar ao Menu Principal

**Mouse Esquerdo:** Selecionar opções no Menu

## 🏗️ Arquitetura do Software

**O projeto aplica a lógica de Orientação a Objetos de forma clara:**

**Personagem:** Contém toda a lógica de estado, movimentação vetorial e desenho do avatar do jogador.

**GerenciadorFases:** Uma estrutura dedicada apenas ao carregamento inteligente das imagens de fundo (Backgrounds) e telas de morte para não sobrecarregar a memória RAM.

**Objetos, Morcego, Vida, Coração:** Entidades distintas que respeitam o contrato de possuírem métodos atualizar() e desenhar(), permitindo o uso eficiente de polimorfismo dentro do laço principal.

**Jogo:** Atua como o Game Controller global, instanciando os objetos corretos para cada fase, processando a física e encapsulando a chamada principal do pyxel.run(update, draw)
