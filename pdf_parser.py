import pdfplumber
from collections import Counter
import re
import json
import fitz #pdf to image
import os

def detect_headings(pdf_path, page_number=None, top_fraction=0.25, score_threshold=0.45):
    """
    Detect headings in a PDF based on font size, bold, position, and uppercase ratio.
    """
    headings = []
    debug_lines = []

    page_filter = {page_number} if page_number is not None else None

    with pdfplumber.open(pdf_path) as pdf:
        for pnum, page in enumerate(pdf.pages, start=1):
            if page_filter and pnum not in page_filter:
                continue

            chars = page.chars
            if not chars:
                continue

            # Group into lines by top coordinate
            lines_map = {}
            for c in chars:
                top_key = round(c.get("top", 0), 1)
                if top_key not in lines_map:
                    lines_map[top_key] = {"chars": [], "sizes": [], "fonts": []}
                lines_map[top_key]["chars"].append(c.get("text", ""))
                lines_map[top_key]["sizes"].append(c.get("size", 0))
                lines_map[top_key]["fonts"].append(c.get("fontname", ""))

            # Font size stats
            sizes = [round(s, 1) for s in (c.get("size", 0) for c in chars) if s > 0]
            if not sizes:
                continue
            size_counts = Counter(sizes)
            common_size = size_counts.most_common(1)[0][0]
            largest_size = max(sizes)
            median_size = sorted(sizes)[len(sizes) // 2]
            page_height = getattr(page, "height", 0)

            for top in sorted(lines_map.keys()):
                text = "".join(lines_map[top]["chars"]).strip()
                if not text:
                    continue

                avg_size = sum(lines_map[top]["sizes"]) / max(1, len(lines_map[top]["sizes"]))
                avg_size_r = round(avg_size, 1)
                fonts_concat = " ".join(lines_map[top]["fonts"])

                # Size score (use median size for better stability)
                denom = max(0.1, (largest_size - median_size))
                size_score = (avg_size_r - median_size) / denom if denom > 0 else 1.0
                size_score = max(0.0, min(1.0, size_score))

                # Bold score
                bold_score = 1.0 if re.search(r'Bold|Black|Heavy|Bd', fonts_concat, re.I) else 0.0

                # Position score
                pos_score = 0.0
                if page_height:
                    pos_score = max(0.0, 1.0 - (top / page_height))
                    if top <= page_height * top_fraction:
                        pos_score = max(pos_score, 0.85)

                # Uppercase ratio
                alpha_chars = [c for c in text if c.isalpha()]
                up_ratio = (sum(1 for ch in alpha_chars if ch.isupper()) / len(alpha_chars)) if alpha_chars else 0.0
                upper_score = min(1.0, up_ratio * 1.2)

                # Weighted score
                score = 0.6 * size_score + 0.2 * bold_score + 0.15 * pos_score + 0.05 * upper_score
                is_heading = score >= score_threshold

                debug_lines.append({
                    "page": pnum, "top": top, "page_height": page_height,
                    "text": text, "avg_size": avg_size_r,
                    "common_size": common_size, "largest_size": largest_size,
                    "size_score": round(size_score, 2),
                    "bold_score": bold_score, "pos_score": round(pos_score, 2),
                    "upper_score": round(upper_score, 2), "score": round(score, 2),
                    "is_heading": is_heading
                })

                if is_heading:
                    headings.append({
                        "page": pnum, "top": top, "text": text,
                        "avg_size": avg_size_r, "score": round(score, 3)
                    })

    debug_lines = sorted(debug_lines, key=lambda d: (d['page'], d['top'], -d['score']))

    return headings, debug_lines



def extract_table_structured(pdf_path, page_number=None):
    
    tables_structured = []
    page_filter = None
    if page_number is not None:
        page_filter = {page_number}

    with pdfplumber.open(pdf_path) as pdf:
        for idx, page in enumerate(pdf.pages, start=1):
            if page_filter and idx not in page_filter:
                continue
            raw_tables = page.extract_tables()
            if not raw_tables:
                continue
            for t in raw_tables:
                cleaned = [[(cell if cell is not None else "") for cell in row] for row in t]
                tables_structured.append({
                    "type": "table",
                    "page": idx,
                    "table_data": cleaned
                })
    return tables_structured

def extract_images_from_pdf(pdf_path, page_number=None, out_dir="images"):
    """
    Extract images using fitz and stored it in Images.
    """

    os.makedirs(out_dir, exist_ok=True)
    results = []
    seen_xrefs = set()

    pages_filter = None
    if page_number is not None:
        if isinstance(page_number, int):
            pages_filter = {page_number}
        else:
            pages_filter = set(page_number)

    with fitz.open(pdf_path) as doc:
        
        for pidx in range(len(doc)):
            pnum = pidx + 1
            if pages_filter and pnum not in pages_filter:
                continue
            page = doc.load_page(pidx)
            image_list = page.get_images(full=True)

            if not image_list:
                continue

            img_counter = 0
            for img in image_list:

                xref = img[0]
                if xref in seen_xrefs:
                    continue
                seen_xrefs.add(xref)
                img_counter += 1

                img_data = doc.extract_image(xref)
                ext = img_data.get("ext", "png")
                image_bytes = img_data.get("image")
                width = img_data.get("width")
                height = img_data.get("height")

                filename = f"page{pnum}_img{img_counter}.{ext}"
                path = os.path.join(out_dir, filename)

                with open(path, "wb") as f:
                    f.write(image_bytes)

                results.append({
                    "path": path,
                    "page": pnum,
                    "ext": ext,
                    "width": width,
                    "height": height
                })

    return results


def page_content(pdf_path, page_number):
    """Extract structured content from a specific page of a PDF."""


    # 1) Detect headings from PDF 
    headings, debug = detect_headings(pdf_path, page_number)

    # Group lines by page
    page_dict = {}
    for line in debug:
        page_num = line.get('page')
        if(page_number and page_num != page_number):
            continue
        page_dict.setdefault(page_num, []).append(line)

    all_pages_content = []

    for page_num, lines in sorted(page_dict.items()):
        content = []
        current_section = None
        current_subsection = None
        current_paragraph_lines = []

        all_size = [line.get('avg_size', 0) for line in lines]
        max_size = max(all_size) if all_size else 0

        def flush_paragraph():
            """Helper to flush paragraph lines into content list."""
            nonlocal current_paragraph_lines
            if current_paragraph_lines:
                para_text = "\n".join(line.strip() for line in current_paragraph_lines).strip()
                if para_text:
                    content.append({
                        # "page": page_num,
                        "type": "paragraph",
                        "section": current_section,
                        "subsection": current_subsection,
                        "text": para_text
                    })
                current_paragraph_lines = []

        for line in lines:
            text = line.get('text', '').strip()
            is_heading = bool(line.get('is_heading', False))
            size = line.get('avg_size', 0)

            if is_heading:
                flush_paragraph()  # close paragraph before heading

                if size == max_size:
                    current_section = text
                    current_subsection = None
                else:
                    current_subsection = text

                content.append({
                    # "page": page_num,
                    "type": "heading",
                    "section": current_section,
                    "subsection": current_subsection,
                    "text": text,
                    "size": size
                })

            elif text:
                current_paragraph_lines.append(text)

        flush_paragraph()

    # 2) Tables using pdfplumber
    tables = extract_table_structured(pdf_path, page_number)
    for t in tables:
        if t["page"] == page_num:
            table_entry = {
                # "page": t["page"],
                "type": "table",
                "section": current_section,
                "table_data": t["table_data"]
            }
            content.append(table_entry)

    # 3)Images
    images = extract_images_from_pdf(pdf_path, page_number)
    for img in images:
        if img["page"] == page_num:
            content.append({
                "type": "image",
                "path": img["path"],
                "width": img.get("width"),
                "height": img.get("height")
            })

    all_pages_content.append({
        "page_number": page_num,
        "content": content
    })

    return all_pages_content


def pdf_to_json(pdf_path, out_dir="images"):
    """
    Convert entire PDF to structured JSON with headings, paragraphs, tables, and images.
    Saves images into out_dir.
    """
    os.makedirs(out_dir, exist_ok=True)
    results = []

    with fitz.open(pdf_path) as pdf:
        total_pages = len(pdf)

    for p in range(1, total_pages + 1):
        page_data = page_content(pdf_path, page_number=p)
        results.extend(page_data)

    return results


# if __name__ == "__main__":
#     PDF_FILE = "E:\GenAI\PDF_Parser\pcheck.pdf"
#     out = pdf_to_json(PDF_FILE, out_dir="Images")
#     print(json.dumps(out, indent=2))