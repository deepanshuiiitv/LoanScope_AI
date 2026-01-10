import mimetypes
import pathlib

def load_file_content(file_path: str) -> dict:
    """
    Reads a file and returns the format required by Gemini 1.5.
    Supports Images (JPEG/PNG) and PDFs natively.
    """
    path = pathlib.Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # 1. Auto-detect MIME type (e.g., 'application/pdf', 'image/jpeg')
    mime_type, _ = mimetypes.guess_type(path)
    
    if not mime_type:
        # Fallback if detection fails
        if path.suffix.lower() == '.pdf':
            mime_type = 'application/pdf'
        elif path.suffix.lower() in ['.jpg', '.jpeg', '.png']:
            mime_type = 'image/jpeg'
        else:
            raise ValueError(f"Unsupported file type: {path.suffix}")

    # 2. Read bytes
    with open(path, "rb") as f:
        file_bytes = f.read()

    # 3. Return dict structure for Gemini
    return {
        "mime_type": mime_type,
        "data": file_bytes
    }