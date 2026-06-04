#!/usr/bin/env python3
"""
Sistema de Leitura - Converte fotos de scanner em PDF pesquisável
Autor: MestrePlanta
Licença: MIT
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import List, Tuple
import cv2
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
from PyPDF2 import PdfMerger
from tqdm import tqdm
import yaml
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BookScannerOCR:
    """Classe principal para conversão de imagens scanner em PDF pesquisável"""

    def __init__(self, language: str = 'por', preprocess: bool = True, quality: str = 'high', verbose: bool = False):
        """
        Inicializa o conversor
        
        Args:
            language: Idioma do OCR ('por', 'eng', 'por+eng')
            preprocess: Aplicar pré-processamento de imagens
            quality: Qualidade ('low', 'medium', 'high')
            verbose: Modo verbose
        """
        self.language = language
        self.preprocess = preprocess
        self.quality = quality
        self.verbose = verbose
        
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        logger.info(f"Sistema de Leitura inicializado com idioma: {language}")

    def _get_supported_languages(self) -> Tuple[str, List[str]]:
        """
        Retorna a string de idiomas e lista de idiomas suportados
        
        Returns:
            Tuple com (string de idiomas, lista de idiomas)
        """
        lang_map = {
            'por': ('por', ['por']),
            'eng': ('eng', ['eng']),
            'pt-br': ('por', ['por']),
            'pt-br+eng': ('por+eng', ['por', 'eng']),
            'por+eng': ('por+eng', ['por', 'eng']),
        }
        
        if self.language.lower() in lang_map:
            return lang_map[self.language.lower()]
        
        # Se não encontrar, tenta usar o valor como está
        return (self.language, self.language.split('+'))

    def _preprocess_image(self, image_path: str) -> Image.Image:
        """
        Pré-processa a imagem para melhorar OCR
        
        Args:
            image_path: Caminho da imagem
            
        Returns:
            Imagem pré-processada
        """
        img = Image.open(image_path).convert('RGB')
        
        if not self.preprocess:
            return img
        
        logger.debug(f"Pré-processando: {image_path}")
        
        # Converter para OpenCV para operações mais avançadas
        cv_img = cv2.imread(image_path)
        
        # Deskew (corrigir rotação)
        cv_img = self._deskew_image(cv_img)
        
        # Converter de volta para PIL
        cv_img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv_img_rgb)
        
        # Denoise
        img = img.filter(ImageFilter.MedianFilter(size=3))
        
        # Melhorar contraste
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.5)
        
        # Melhorar nitidez
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(2.0)
        
        # Melhorar brilho
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.1)
        
        return img

    def _deskew_image(self, image) -> np.ndarray:
        """
        Corrige a inclinação da imagem
        
        Args:
            image: Imagem OpenCV
            
        Returns:
            Imagem corrigida
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Binarizar
        _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        
        # Encontrar contornos e ângulo
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return image
        
        # Encontrar maior contorno
        largest_contour = max(contours, key=cv2.contourArea)
        rect = cv2.minAreaRect(largest_contour)
        angle = rect[2]
        
        # Corrigir ângulo
        if angle < -45:
            angle = 90 + angle
        
        if abs(angle) < 1:  # Se a inclinação é mínima, não faz nada
            return image
        
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, rotation_matrix, (w, h), borderMode=cv2.BORDER_REFLECT)
        
        return rotated

    def _extract_text_with_ocr(self, image: Image.Image, lang_string: str) -> str:
        """
        Extrai texto da imagem usando Tesseract OCR
        
        Args:
            image: Imagem PIL
            lang_string: String de idiomas para Tesseract
            
        Returns:
            Texto extraído
        """
        try:
            # Configurar Tesseract
            custom_config = r'--oem 3 --psm 1'
            text = pytesseract.image_to_string(image, lang=lang_string, config=custom_config)
            return text
        except Exception as e:
            logger.error(f"Erro ao extrair texto: {e}")
            return ""

    def _create_searchable_pdf(self, image: Image.Image, text: str, output_path: str):
        """
        Cria um PDF pesquisável com a imagem e texto OCR
        
        Args:
            image: Imagem PIL
            text: Texto extraído
            output_path: Caminho do arquivo PDF
        """
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            from reportlab.lib.utils import ImageReader
            
            # Redimensionar imagem para caber em uma página
            width, height = image.size
            page_width, page_height = letter
            
            # Calcular novo tamanho mantendo proporção
            ratio = min(page_width / width, page_height / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            
            image.thumbnail((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Criar PDF
            c = canvas.Canvas(output_path, pagesize=letter)
            
            # Desenhar imagem
            img_reader = ImageReader(image)
            x = (page_width - new_width) / 2
            y = (page_height - new_height) / 2
            c.drawImage(img_reader, x, y, width=new_width, height=new_height)
            
            # Adicionar texto invisível para pesquisa
            c.setFont("Helvetica", 10)
            c.setFillAlpha(0)  # Texto invisível
            c.drawString(50, 50, text)
            
            c.save()
            
        except ImportError:
            # Se reportlab não estiver disponível, usar outro método
            logger.warning("reportlab não instalado, usando método alternativo")
            image.save(output_path, 'PDF')

    def process_folder(self, input_folder: str, output_pdf: str) -> bool:
        """
        Processa uma pasta de imagens e cria um PDF pesquisável
        
        Args:
            input_folder: Caminho da pasta com imagens
            output_pdf: Caminho do arquivo PDF de saída
            
        Returns:
            True se bem-sucedido, False caso contrário
        """
        input_path = Path(input_folder)
        
        if not input_path.exists():
            logger.error(f"Pasta não encontrada: {input_folder}")
            return False
        
        # Encontrar todas as imagens
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        images = sorted([
            f for f in input_path.iterdir()
            if f.suffix.lower() in image_extensions
        ])
        
        if not images:
            logger.error(f"Nenhuma imagem encontrada em: {input_folder}")
            return False
        
        logger.info(f"Encontradas {len(images)} imagens")
        
        # Obter configuração de idioma
        lang_string, lang_list = self._get_supported_languages()
        logger.info(f"Usando idiomas: {lang_list}")
        
        # Processar imagens
        temp_pdfs = []
        
        try:
            for idx, image_path in enumerate(tqdm(images, desc="Processando imagens")):
                logger.debug(f"Processando {idx + 1}/{len(images)}: {image_path.name}")
                
                # Pré-processar imagem
                processed_img = self._preprocess_image(str(image_path))
                
                # Extrair texto
                text = self._extract_text_with_ocr(processed_img, lang_string)
                
                # Criar PDF temporário
                temp_pdf = Path(output_pdf).parent / f"temp_{idx:04d}.pdf"
                self._create_searchable_pdf(processed_img, text, str(temp_pdf))
                temp_pdfs.append(str(temp_pdf))
                
                if self.verbose:
                    logger.debug(f"Texto extraído: {text[:100]}...")
            
            # Mesclar PDFs
            logger.info("Mesclando PDFs...")
            self._merge_pdfs(temp_pdfs, output_pdf)
            
            # Limpar arquivos temporários
            for temp_pdf in temp_pdfs:
                Path(temp_pdf).unlink()
            
            logger.info(f"PDF pesquisável criado com sucesso: {output_pdf}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao processar pasta: {e}")
            # Limpar arquivos temporários
            for temp_pdf in temp_pdfs:
                try:
                    Path(temp_pdf).unlink()
                except:
                    pass
            return False

    def _merge_pdfs(self, pdf_list: List[str], output_pdf: str):
        """
        Mescla múltiplos PDFs em um único arquivo
        
        Args:
            pdf_list: Lista com caminhos dos PDFs
            output_pdf: Caminho do PDF de saída
        """
        try:
            merger = PdfMerger()
            
            for pdf in pdf_list:
                merger.append(pdf)
            
            merger.write(output_pdf)
            merger.close()
            
        except Exception as e:
            logger.error(f"Erro ao mesclar PDFs: {e}")
            raise


def main():
    """
    Função principal
    """
    parser = argparse.ArgumentParser(
        description='Converte fotos de scanner em PDF pesquisável com OCR',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python book_scanner.py -i ./scans -o ./livro.pdf -l por
  python book_scanner.py -i ./fotos -o ./livro.pdf -l por -v
  python book_scanner.py -i ./scans -o ./livro.pdf -l por+eng -q high
        """
    )
    
    parser.add_argument('-i', '--input', required=True, help='Pasta com imagens do scanner')
    parser.add_argument('-o', '--output', required=True, help='Caminho do PDF de saída')
    parser.add_argument('-l', '--language', default='por', 
                       help='Idioma: por (português), eng (inglês), por+eng (ambos). Padrão: por')
    parser.add_argument('-p', '--preprocess', default=True, type=bool,
                       help='Aplicar pré-processamento (padrão: True)')
    parser.add_argument('-q', '--quality', default='high', choices=['low', 'medium', 'high'],
                       help='Qualidade: low, medium, high. Padrão: high')
    parser.add_argument('-v', '--verbose', action='store_true', help='Modo verbose')
    
    args = parser.parse_args()
    
    # Criar instância e processar
    scanner = BookScannerOCR(
        language=args.language,
        preprocess=args.preprocess,
        quality=args.quality,
        verbose=args.verbose
    )
    
    success = scanner.process_folder(args.input, args.output)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
