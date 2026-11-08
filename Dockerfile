# Usa una imagen oficial de Python (ligera)
FROM python:3.11-slim

# Instala FFmpeg (CRÍTICO para reproducir audio) y limpia el caché para ahorrar espacio
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia primero el archivo de dependencias (optimiza el caché de Docker)
COPY requirements.txt .

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de tu código (incluyendo el doom.mp3)
COPY . .

# Comando para ejecutar el bot
CMD ["python", "bot.py"]