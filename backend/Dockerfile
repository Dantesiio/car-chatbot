# Usa una imagen base de Python optimizada
FROM python:3.9-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia solo los archivos necesarios
COPY ./app /app

# Instala gcc (necesario para algunas dependencias como pgmpy)
RUN apt-get update -y && \
    apt-get install -y gcc && \
    rm -rf /var/lib/apt/lists/*  # Limpiar caché de apt para reducir el tamaño de la imagen

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto 8000
EXPOSE 8000

# Comando para ejecutar FastAPI con Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

