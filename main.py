# main.py
from input_text import read_paste_block, pdf_to_text
from extract_fields import extract_fields_pdfaware, OFFICIAL_FIELDS

def main():
    print("Choose input method:")
    print("1) Paste form response")
    print("2) PDF file")

    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        raw_text = read_paste_block()
    elif choice == "2":
        import os

        pdf_path = input("Enter path to PDF: ").strip().strip('"')
        if not os.path.isfile(pdf_path):
            print("Invalid file path. Make sure you include the full PDF filename.")
            return

        raw_text = pdf_to_text(pdf_path)
    else:
        print("Invalid choice.")
        return

    fields = extract_fields_pdfaware(raw_text)

    print("\n--- Extracted Fields ---")
    for k in OFFICIAL_FIELDS:
        print(f"{k}: {fields[k]}")

if __name__ == "__main__":
    main()
