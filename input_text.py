import pdfplumber

END_MARKER = "<<<END>>>"

def read_paste_block() -> str:
    print("\nPaste the full form response.")
    print(f"When finished, type {END_MARKER} on its own line and press Enter.\n")

    lines = []
    while True:
        line = input()
        if line.strip() == END_MARKER:
            break
        lines.append(line)

    return "\n".join(lines)

def pdf_to_text(pdf_path: str) -> str:
    parts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            parts.append(text)
    return "\n".join(parts)