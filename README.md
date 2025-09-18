# PDF-Parser

A simple, open-source Python project to parse PDF files into structured JSON.  
It extracts page-wise content including headings, paragraphs, tables, and images, and provides a user-friendly Streamlit interface to view and download parsed results.

---

## ✨ Features

- Parses PDFs into **structured JSON**
- Extracts:
  - **Headings**
  - **Paragraphs**
  - **Tables**
  - **Images** (saved in `Images/` folder)
- Streamlit web app for:
  - Uploading and parsing PDFs
  - Page-wise navigation
  - Viewing content with proper formatting
  - Adjusting image display size
  - Downloading parsed JSON

---

## ⚙️ Installation

Make sure you have **Python 3.x** installed.

```bash
# Clone the repository
git clone https://github.com/Om-711/PDF-Parser.git
cd PDF-Parser

# (Optional) Create virtual environment
python3 -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt
