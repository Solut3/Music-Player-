# Music Player

Player de música open source para **Windows** e **Linux**, licenciado sob **GPL-3.0**.

## Funcionalidades

- Reprodução de MP3, FLAC, OGG, WAV, M4A, AAC, Opus e WMA
- **Detecção automática** de músicas em Music, Downloads, Desktop e outras pastas do PC
- **Tema escuro** e **tema claro** — alternância com um clique
- Interface moderna com barra de player, lista otimizada e ícone na bandeja
- **Segundo plano** — minimiza para a bandeja do sistema sem fechar
- **Baixo uso de RAM** — cache de metadados, varredura em thread separada, timer só durante reprodução
- Controles: play/pause, anterior, próximo, shuffle, repeat
- Atalhos: `Espaço`, `←` / `→`, `Ctrl+O`

## Requisitos

- Python 3.10 ou superior
- Windows 10+ ou Linux com ambiente gráfico

## Instalação

```bash
pip install -r requirements.txt
```

No Linux, pode ser necessário instalar plugins multimídia do Qt:

```bash
# Debian/Ubuntu
sudo apt install libxcb-cursor0

# Fedora
sudo dnf install qt6-qtmultimedia
```

## Executar

```bash
python main.py
```

## Gerar executável para Linux (opcional)

O executável Linux precisa ser gerado **em um sistema Linux** (ou WSL). Não é
possível criar um binário Linux diretamente pelo Windows.

No Debian/Ubuntu, instale as dependências e gere a build com:

```bash
sudo apt update
sudo apt install python3-pip libxcb-cursor0
python3 -m pip install --user -r requirements.txt pyinstaller
python3 -m PyInstaller --noconfirm --clean --onefile --windowed \
  --name MusicPlayer --hidden-import PySide6.QtMultimedia main.py
```

O executável será criado em `dist/MusicPlayer`. Caso seja necessário, permita
a execução com `chmod +x dist/MusicPlayer` e inicie-o com:

```bash
./dist/MusicPlayer
```

## Temas

Use o botão **Tema: escuro** / **Tema: claro** na barra de ferramentas para alternar.

## Segundo plano

Ao fechar a janela, o player continua na **bandeja do sistema**. Clique duplo no ícone para reabrir. Use **Sair** no menu da bandeja para encerrar.

## Licença

Este projeto é software livre sob a [GNU General Public License v3.0](LICENSE).
