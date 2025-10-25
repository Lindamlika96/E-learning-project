import fitz  # PyMuPDF
import re
import json
from statistics import quantiles
from pathlib import Path

# === Extraction des blocs de texte avec styles ===
def extract_blocks_with_styles(pdf_path):
    doc = fitz.open(pdf_path)
    pages = []
    for pno, page in enumerate(doc):
        blocks = []
        for b in page.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                for s in l.get("spans", []):
                    blocks.append({
                        "text": s["text"].strip(),
                        "size": s["size"],
                        "bold": "Bold" in (s.get("font", "") or ""),
                        "page": pno + 1
                    })
        pages.append(blocks)
    return pages

# === Segmentation par chapitres / sections ===
def segment_headings(pages):
    sizes = [s["size"] for page in pages for s in page if s["text"]]
    if not sizes:
        return []

    p80 = quantiles(sizes, n=5)[3]
    doc_struct = []
    current_chapter = {"title": None, "page_start": None, "sections": [], "content": []}

    def start_new_chapter(title, page):
        return {"title": title, "page_start": page, "sections": [], "content": []}

    for page in pages:
        for span in page:
            t = span["text"]
            if not t:
                continue
            is_heading = (span["size"] >= p80) or span["bold"] or re.match(r"^(Chapitre|Chapter)\s+\d+", t, re.I)
            if is_heading:
                if current_chapter["title"] is None:
                    current_chapter = start_new_chapter(t, span["page"])
                    doc_struct.append(current_chapter)
                elif re.match(r"^(Chapitre|Chapter)\s+\d+", t, re.I):
                    current_chapter = start_new_chapter(t, span["page"])
                    doc_struct.append(current_chapter)
                else:
                    current_chapter["sections"].append({"title": t, "content": []})
            else:
                if current_chapter["sections"]:
                    current_chapter["sections"][-1]["content"].append(t)
                else:
                    current_chapter["content"].append(t)
    return doc_struct

# === Extraction des définitions ===
def extract_definitions(paragraphs):
    defs = []
    pat = re.compile(r"(Définition|On appelle|Est défini\s+comme)\s*[:\-]?\s*(.+)", re.I)
    for p in paragraphs:
        m = pat.search(p)
        if m:
            defs.append({"text": p})
    return defs

# === Création du JSON structuré ===
def build_dataset(doc_structure):
    dataset = []
    for ch in doc_structure:
        paragraphs = ch.get("content", [])
        for s in ch.get("sections", []):
            paragraphs += s.get("content", [])

        defs = extract_definitions(paragraphs)

        dataset.append({
            "chapter": ch["title"],
            "page_start": ch["page_start"],
            "definitions": defs,
            "sections": ch.get("sections", []),
            "raw": paragraphs
        })
    return dataset

# === Fonction principale ===
def process_all_pdfs():
    data_folder = Path("data")
    pdf_files = list(data_folder.glob("*.pdf"))
    if not pdf_files:
        print("❌ Aucun fichier PDF trouvé dans le dossier data/")
        return

    all_courses = []

    for pdf_path in pdf_files:
        print(f"📘 Extraction en cours pour {pdf_path.name} ...")
        pages = extract_blocks_with_styles(pdf_path)
        doc_structure = segment_headings(pages)
        dataset = build_dataset(doc_structure)

        output = {
            "course_title": pdf_path.stem,
            "chapters": dataset
        }

        output_file = data_folder / f"{pdf_path.stem}_structured.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        all_courses.append(output)
        print(f"✅ Extraction terminée pour {pdf_path.name} -> {output_file.name}")

    # Sauvegarde globale regroupant tous les cours
    global_output = data_folder / "all_courses.json"
    with open(global_output, "w", encoding="utf-8") as f:
        json.dump(all_courses, f, ensure_ascii=False, indent=2)
    print(f"📚 Tous les cours extraits ont été enregistrés dans {global_output}")

if __name__ == "__main__":
    process_all_pdfs()
