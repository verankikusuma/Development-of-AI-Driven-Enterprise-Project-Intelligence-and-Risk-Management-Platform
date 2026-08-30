import io
import os
import streamlit as st
from PIL import Image
from google import genai
import fitz  # PyMuPDF

def extract_images_from_pdf(file_bytes: bytes) -> list[Image.Image]:
    """Extracts all embedded images from a PDF."""
    images = []
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            image_list = page.get_images(full=True)
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                try:
                    image = Image.open(io.BytesIO(image_bytes))
                    # Convert to RGB to avoid issues with some image formats
                    if image.mode != "RGB":
                        image = image.convert("RGB")
                    images.append(image)
                except Exception as e:
                    print(f"Error loading extracted image: {e}")
    except Exception as e:
        print(f"Error parsing PDF with PyMuPDF: {e}")
    return images


def llm_read_image(image: Image.Image) -> str:
    """Uses Gemini Vision to extract data points, charts, and information from an image."""
    api_key = os.environ.get("GEMINI_API_KEY", "")
    use_cloud = os.environ.get("USE_CLOUD_AI", "true").lower() in ("true", "1", "yes")
    
    if not use_cloud or not api_key:
        return ""
    
    prompt = (
        "Read this chart, graph, table or diagram. Extract the exact data points, "
        "axis labels, categories, and any numbers shown. Return the underlying data "
        "in a structured format (e.g. Markdown tables or lists), not just a visual description. "
        "If it is a plain image with no data/text, return nothing."
    )
    
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=[image, prompt]
        )
        return response.text if response.text else ""
    except Exception as e:
        print(f"Vision API error: {e}")
        return ""

def process_document_images(file_name: str, file_bytes: bytes) -> str:
    """Extracts images and gets their textual data representation."""
    if not file_name.lower().endswith(".pdf"):
        return ""
        
    extracted_text_blocks = []
    images = extract_images_from_pdf(file_bytes)
    
    for i, img in enumerate(images):
        extracted = llm_read_image(img)
        if extracted and extracted.strip():
            block = f"\n\n--- [Image/Chart Data Extracted (Image {i+1})] ---\n{extracted.strip()}\n----------------------------------------------------\n"
            extracted_text_blocks.append(block)
            
    return "".join(extracted_text_blocks)
