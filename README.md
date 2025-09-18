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

# Run the program
streamlit run app.py

PDF-Parser/
├── app.py                  # Streamlit app
├── pdf_parser.py           # Core parsing logic
├── requirements.txt        # Dependencies
├── Images/                 # Extracted images
└── README.md

```
Photos :
<img width="1912" height="868" alt="image" src="https://github.com/user-attachments/assets/9fa1e8d1-39d7-4e26-b362-5347d099bcdd" />
<img width="1919" height="863" alt="image" src="https://github.com/user-attachments/assets/2292e078-ae34-4cea-b193-9386ecbb2116" />


