FROM python:3.11-slim
 
# Créer le répertoire de travail
WORKDIR /app
 
# Copier et installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
 
# Copier le code de l'application
COPY . .
 
# Exposer le port 5000
EXPOSE 5000
 
# Démarrer l'application
CMD ["python", "app.py"]
