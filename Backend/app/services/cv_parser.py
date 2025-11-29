import pdfplumber
from fastapi import UploadFile, HTTPException, status
from typing import Tuple, List
import tempfile
import os
import re


class CVParserService:
    """Servicio para parsear CVs (sin embeddings reales por ahora)"""

    async def parse_cv_file(self, file: UploadFile) -> Tuple[str, List[float]]:
        """
        Parsear archivo PDF del CV
        
        Returns:
            (texto_extraído, embedding_stub)
        
        NOTA: Groq NO tiene API de embeddings. Usamos un stub por ahora.
        Para producción, usa OpenAI embeddings o sentence-transformers local.
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
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(content)
                tmp_path = tmp.name
            
            # Extraer texto con pdfplumber
            cv_text = ""
            try:
                with pdfplumber.open(tmp_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            cv_text += page_text + "\n"
            finally:
                # Limpiar archivo temporal
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            
            if not cv_text or len(cv_text.strip()) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No text could be extracted from PDF"
                )
            
            # Limpiar texto
            cv_text = await self.clean_cv_text(cv_text)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error parsing PDF: {str(e)}"
            )
        
        # 3. Generar embedding STUB (Groq no tiene embeddings API)
        # Para producción: usa OpenAI, Cohere, o sentence-transformers local
        embedding = []
        
        return cv_text, embedding

    def _generate_stub_embedding(self, text: str) -> List[float]:
        """
        Genera un embedding stub basado en el hash del texto.
        
        Para producción, reemplaza esto con:
        - OpenAI: openai.Embedding.create(model="text-embedding-3-small", input=text)
        - Cohere: co.embed(texts=[text])
        - Local: sentence_transformers.SentenceTransformer("all-MiniLM-L6-v2").encode(text)
        """
        # Generar un vector de 768 dimensiones (estándar para embeddings)
        # Basado en el hash del texto para que sea determinístico
        import hashlib
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        
        # Convertir hash a números entre -1 y 1
        embedding = []
        for i in range(0, len(text_hash), 2):
            byte_val = int(text_hash[i:i+2], 16)
            normalized = (byte_val / 255.0) * 2 - 1  # Escalar a [-1, 1]
            embedding.append(normalized)
        
        # Rellenar o truncar a 768 dimensiones
        while len(embedding) < 768:
            embedding.extend(embedding[:min(len(embedding), 768 - len(embedding))])
        
        return embedding[:768]

    def extract_cv_summary(self, cv_text: str) -> str:
        """
        Extraer resumen del CV (nombres, emails, experiencia clave)
        Útil para búsquedas rápidas
        """
        return cv_text[:1000] if cv_text else ""

    async def clean_cv_text(self, cv_text: str) -> str:
        """
        Limpiar y normalizar texto del CV
        """
        # Remover espacios múltiples
        cv_text = re.sub(r'\s+', ' ', cv_text)
        
        # Remover caracteres especiales problemáticos (mantener alfanuméricos y puntuación básica)
        cv_text = re.sub(r'[^\w\s\n\-.,:/()@+áéíóúÁÉÍÓÚñÑ]', '', cv_text)
        
        return cv_text.strip()
