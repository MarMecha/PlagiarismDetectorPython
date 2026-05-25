# Plagiarism Detection Platform

A web-based plagiarism detection platform developed to identify and visualize textual similarities between PDF documents.

The system combines Natural Language Processing (NLP), fingerprinting techniques and document annotation to detect potential plagiarism cases and generate visual similarity reports.

---

## Features

✔ PDF document upload and comparison

✔ Greek language text processing

✔ Text lemmatization using NLP

✔ Shingle generation and filtering

✔ Fingerprint extraction using Winnowing

✔ Similarity detection and ranking

✔ Automatic PDF highlighting

✔ Comparison history tracking

✔ Interactive web interface

---

## System Architecture

Frontend

- HTML
- CSS
- JavaScript
- Dynamic Modals
- AJAX (Fetch API)

↓

Backend

- Python
- Django

↓

Processing Pipeline

Text Extraction

↓

Lemmatization

↓

Shingle Generation

↓

Fingerprinting (Winnowing)

↓

Similarity Detection

↓

PDF Highlight Generation

---

## Technologies Used

### Backend
- Python
- Django

### NLP
- SpaCy
- el_core_news_sm

### PDF Processing
- pdfplumber
- PyMuPDF (fitz)

### Algorithms
- Winnowing
- Hash-based Fingerprinting

### Frontend
- HTML
- CSS
- JavaScript

### Storage
- SQLite (development)

---

## Detection Workflow

1. Upload PDF documents

2. Extract text and word positions

3. Perform lemmatization

4. Generate shingles

5. Evaluate shingle quality

6. Generate fingerprints

7. Detect similarities

8. Produce highlighted PDF reports

---

## Key Technical Concepts

### Fingerprinting

Documents are transformed into representative fingerprints to reduce comparison complexity while preserving meaningful textual information.

### Winnowing Algorithm

The platform applies the Winnowing algorithm to select representative hashes and improve plagiarism detection efficiency.

### PDF Highlighting

Detected similarities are rendered directly on generated PDF reports using visual highlights and ranking labels.

---

## Installation

Clone repository

```bash
git clone https://github.com/YOUR_USERNAME/plagiarism-detection-platform.git
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run migrations

```bash
python manage.py migrate
```

Start server

```bash
python manage.py runserver
```

Open

```text
http://127.0.0.1:8000/
```

---

## Screenshots

### Home Page

<img width="1896" height="857" alt="image" src="https://github.com/user-attachments/assets/e6d53975-7931-41a0-b713-4d6b31d8ac5b" />


### Upload Documents

<img width="1897" height="861" alt="image" src="https://github.com/user-attachments/assets/43207739-ef98-4733-90cb-cdc11ce2ed4a" />


### Results

<img width="1714" height="744" alt="image" src="https://github.com/user-attachments/assets/599081d5-3201-44cb-ae87-3e35d79adc77" />


---

## Future Improvements

- PostgreSQL migration
- Docker deployment
- Authentication improvements
- REST API support
- Semantic similarity models
- Performance optimization

---


## Author

Mariol Mehalla
