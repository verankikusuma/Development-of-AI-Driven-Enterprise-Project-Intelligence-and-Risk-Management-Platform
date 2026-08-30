from pathlib import Path


def extract_text(uploaded_file):
    suffix = Path(uploaded_file.name).suffix.lower()
    data = uploaded_file.getvalue()
    if suffix == ".txt":
        return data.decode("utf-8", errors="ignore")
    if suffix == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(uploaded_file)
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    if suffix == ".docx":
        import docx2txt
        return docx2txt.process(uploaded_file)
    if suffix == ".csv":
        import pandas as pd
        return pd.read_csv(uploaded_file).to_csv(index=False)
    return ""
