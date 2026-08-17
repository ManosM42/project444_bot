# Χρησιμοποιούμε μια ελαφριά και επίσημη εικόνα Python
FROM python:3.11-slim

# Ορίζουμε τον φάκελο εργασίας μέσα στο container
WORKDIR /app

# Εγκατάσταση βασικών εργαλείων συστήματος
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Αντιγράφουμε πρώτα το requirements.txt για σωστό caching
COPY requirements.txt .

# Εγκατάσταση των Python βιβλιοθηκών με timeout και retries για αποφυγή κολλημάτων δικτύου
RUN pip install --no-cache-dir --timeout=120 --retries=5 -r requirements.txt

# Αντιγράφουμε όλο τον υπόλοιπο κώδικα
COPY . .

# Εντολή εκκίνησης του bot
CMD ["python", "main.py"]