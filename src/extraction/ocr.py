import PyPDF2
import pytesseract
from PIL import Image
import cv2
import numpy as np
import os


class DocumentExtractor:
    def __init__(self):
        self.tesseract_config = '--oem 3 --psm 6'

    def extract_text_from_pdf(self, pdf_path: str) -> tuple[str, str]:
        """Extract text from PDF, return (text, quality)"""
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()

            # Determine quality based on text extracted
            if len(text.strip()) > 100:
                return text, "excellent"
            else:
                return text, "poor"
        except Exception as e:
            print(f"PDF extraction error: {e}")
            return "", "poor"

    def extract_text_from_image(self, image_path: str) -> tuple[str, str]:
        """Extract text from image using OCR"""
        try:
            # Load and preprocess image
            image = cv2.imread(image_path)

            # Rotate if needed
            image = self.deskew_image(image)

            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Apply thresholding
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # OCR
            text = pytesseract.image_to_string(thresh, config=self.tesseract_config)

            # Determine quality
            if len(text.strip()) > 100:
                quality = "acceptable"
            else:
                quality = "poor"

            return text, quality
        except Exception as e:
            print(f"Image OCR error: {e}")
            return "", "poor"

    def deskew_image(self, image):
        """Deskew image if rotated"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            gray = cv2.bitwise_not(gray)
            coords = np.column_stack(np.where(gray > 0))
            angle = cv2.minAreaRect(coords)[-1]

            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle

            # Only rotate if angle is significant
            if abs(angle) > 1:
                (h, w) = image.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                rotated = cv2.warpAffine(image, M, (w, h),
                                         flags=cv2.INTER_CUBIC,
                                         borderMode=cv2.BORDER_REPLICATE)
                return rotated
            return image
        except:
            return image

    def extract_text(self, file_path: str) -> tuple[str, str]:
        """Main extraction method - handles PDF, images, and text files"""
        ext = os.path.splitext(file_path)[1].lower()

        if ext == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif ext in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
            return self.extract_text_from_image(file_path)
        elif ext == '.txt':
            # Plain text files (for testing)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                return text, "excellent"
            except Exception as e:
                print(f"Text file error: {e}")
                return "", "poor"
        else:
            return "", "poor"
