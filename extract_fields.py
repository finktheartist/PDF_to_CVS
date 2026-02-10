import re

OFFICIAL_FIELDS = [
    "Name",
    "Columbia Email",
    "MyColumbia ID",
    "Major",
    "Company/Studio",
    "Name of Supervisor at Company",
    "Contact information for Supervisor (Email required)",
]

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def normalize_label(s: str) -> str:
    s = s.replace("\u00a0", " ")          # non-breaking space -> space
    s = s.strip().lower()
    s = re.sub(r"[\t ]+", " ", s)         # collapse tabs/spaces
    s = s.rstrip(" :")                    # strip trailing colon/spaces
    return s

TARGET_MAP = {normalize_label(lbl): lbl for lbl in OFFICIAL_FIELDS}

# Try longer labels first so "Name of Supervisor..." beats "Name"
NORM_LABELS_BY_LENGTH = sorted(TARGET_MAP.keys(), key=len, reverse=True)


KEY_VALUE_RE = re.compile(r"^\s*([^:\n]+?)\s*:\s*(.*)\s*$")

def try_match_wrapped_label(lines, i, max_label_lines=4):
    """
    Join up to max_label_lines consecutive lines to reconstruct a label that got wrapped in the PDF.
    Returns (official_label, next_index_after_label) or (None, i).
    """
    chunks = []
    for j in range(i, min(i + max_label_lines, len(lines))):
        if not lines[j].strip():
            break
        chunks.append(lines[j].strip())

        candidate = " ".join(chunks)
        norm = normalize_label(candidate)
        if norm in TARGET_MAP:
            return TARGET_MAP[norm], j + 1

    return None, i

    return None, i

def extract_fields_pdfaware(raw_text: str) -> dict:
    """
    Supports:
      (1) Label: Value
      (2) Label on one line, value on next
      (3) Label Value on same line (common in PDFs like your upload)
    """
    fields = {lbl: "" for lbl in OFFICIAL_FIELDS}
    raw_lines = [ln.strip() for ln in raw_text.splitlines()]
    raw_lines = [ln for ln in raw_lines if ln]  # drop empty lines

    i = 0
    while i < len(raw_lines):
        line = raw_lines[i]

        # (1) Label: Value
        m = KEY_VALUE_RE.match(line)
        if m:
            raw_label = m.group(1)
            raw_value = m.group(2)
            norm = normalize_label(raw_label)
            if norm in TARGET_MAP:
                fields[TARGET_MAP[norm]] = raw_value.strip()
            i += 1
            continue

        norm_line = normalize_label(line)

        # (2b) Wrapped label across multiple lines (common in PDFs)
        official_label, next_i = try_match_wrapped_label(raw_lines, i)
        if official_label:
            j = next_i
            while j < len(raw_lines) and not raw_lines[j].strip():
                j += 1
            fields[official_label] = raw_lines[j].strip() if j < len(raw_lines) else ""
            i = j + 1
            continue

        matched_same_line = False
        for norm_label in NORM_LABELS_BY_LENGTH:
            official_label = TARGET_MAP[norm_label]
            prefix = norm_label + " "

            if norm_line.startswith(prefix):
                label_words = norm_label.split(" ")
                parts = line.split()

                # remove exactly the label's word-count from the front
                if len(parts) >= len(label_words) + 1:
                    value = " ".join(parts[len(label_words):]).strip()
                    fields[official_label] = value
                    matched_same_line = True
                    break

        if matched_same_line:
            i += 1
            continue

        # (2) Label on one line, Value on next
        if norm_line in TARGET_MAP:
            official_label = TARGET_MAP[norm_line]
            value = raw_lines[i + 1].strip() if i + 1 < len(raw_lines) else ""
            fields[official_label] = value
            i += 2
            continue

        i += 1

    # Fallback: If supervisor email is still blank, infer it from all emails in the document
    contact_key = "Contact information for Supervisor (Email required)"
    if not fields[contact_key]:
        all_emails = EMAIL_RE.findall(raw_text)
        all_emails = [e.strip() for e in all_emails]

        columbia_email = fields.get("Columbia Email", "").strip()
        candidates = [e for e in all_emails if e.lower() != columbia_email.lower()]

        # If there's exactly one non-Columbia email, it's almost certainly the supervisor email
        if len(candidates) == 1:
            fields[contact_key] = candidates[0]
        elif len(candidates) > 1:
            # If multiple, pick the first one (or you can print/log for review)
            fields[contact_key] = candidates[0]

    return fields
