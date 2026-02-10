# PDF_to_CVS

A Python utility for extracting structured data from internship application forms.
Supports both pasted form text and uploaded PDFs with inconsistent formatting.

This tool was built to handle real-world, messy inputs (especially PDFs) and
produce clean, repeatable outputs suitable for CSV or Excel workflows.

---

## Features

- Extracts key student and supervisor fields:
  - Name
  - Columbia Email
  - MyColumbia ID
  - Major
  - Company / Studio
  - Supervisor Name
  - Supervisor Email
- Supports:
  - Pasted form responses
  - Text-based PDFs
- Handles:
  - Labels split across multiple lines
  - Labels and values on the same line
  - Inconsistent spacing and formatting
- Designed for repeated use and batch processing
- Safe for handling sensitive data (PDFs and outputs excluded via `.gitignore`)

---

## Project Structure

