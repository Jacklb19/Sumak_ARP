import pdfplumber
from fastapi import UploadFile, HTTPException, status
from openai import OpenAI
from app.core.config import settings
from typing import Tuple, Optional


class CVParserService:
    """Servicio para parsear CVs y generar embeddings"""

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    async def parse_cv_file(self, file: UploadFile) -> Tuple[str, list]:
        """
        Parsear archivo PDF del CV
        
        Según PARTE 3.2 del MD:
        1. Extraer texto del PDF
        2. Generar embedding con OpenAI
        3. Retornar (texto_extraído, embedding)
        """
        
        # 1. Validar que sea PDF
        if file.content_type != "application/pdf":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are allowed"
            )
        
        # 2. Leer archivo y extraer texto
        try:
            # Leer contenido del archivo
            content = await file.read()
            
            # Escribir temporalmente para pdfplumber
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(content)
                tmp_path = tmp.name
            
            # Extraer texto con pdfplumber
            cv_text = ""
            with pdfplumber.open(tmp_path) as pdf:
                for page in pdf.pages:
                    cv_text += page.extract_text() or ""
            
            # Limpiar archivo temporal
            import os
            os.remove(tmp_path)
            
            if not cv_text or len(cv_text.strip()) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No text could be extracted from PDF"
                )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error parsing PDF: {str(e)}"
            )
        
        # 3. Generar embedding con OpenAI
        try:
            embedding_response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=cv_text[:8000]  # Limitar a 8000 chars para no exceder tokens
            )
            embedding = embedding_response.data[0].embedding
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error generating embedding: {str(e)}"
            )
        
        return cv_text, embedding

    def extract_cv_summary(self, cv_text: str) -> str:
        """
        Extraer resumen del CV (nombres, emails, experiencia clave)
        Útil para búsquedas rápidas
        """
        # Limitar a primeras 1000 caracteres
        return cv_text[:1000] if cv_text else ""

    async def clean_cv_text(self, cv_text: str) -> str:
        """
        Limpiar y normalizar texto del CV
        """
        import re
        
        # Remover espacios múltiples
        cv_text = re.sub(r'\s+', ' ', cv_text)
        
        # Remover caracteres especiales problemáticos
        cv_text = re.sub(r'[^\w\s\n\-.,:/()@]', '', cv_text)
        
        return cv_text.strip()