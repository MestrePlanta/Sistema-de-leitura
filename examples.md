# Exemplos de Uso - Sistema de Leitura

## Exemplo 1: Converter livro em português simples

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Converter pasta de imagens em PDF
python book_scanner.py -i ./meus_scans -o ./livro_final.pdf -l por
```

**Resultado:** PDF pesquisável em português do arquivo `livro_final.pdf`

---

## Exemplo 2: Converter livro em inglês com modo verbose

```bash
python book_scanner.py \
  -i ./english_book_scans \
  -o ./english_book.pdf \
  -l eng \
  -v
```

**Resultado:** Mostra detalhes do processamento e cria `english_book.pdf`

---

## Exemplo 3: Converter livro bilíngue (português + inglês)

```bash
python book_scanner.py \
  -i ./bilingual_book \
  -o ./livro_bilingue.pdf \
  -l por+eng
```

**Resultado:** OCR em ambos os idiomas simultaneamente

---

## Exemplo 4: Processamento rápido com qualidade baixa

```bash
python book_scanner.py \
  -i ./scans \
  -o ./livro_rapido.pdf \
  -l por \
  -q low \
  --preprocess False
```

**Resultado:** Processamento mais rápido, porém com qualidade menor de OCR

---

## Exemplo 5: Alta qualidade com pré-processamento

```bash
python book_scanner.py \
  -i ./high_quality_scans \
  -o ./livro_qualidade.pdf \
  -l por \
  -q high \
  --preprocess True \
  -v
```

**Resultado:** Melhor qualidade de OCR com correção de inclinação, denoise e contraste

---

## Preparando imagens do scanner

### Dicas para melhor OCR:

1. **Iluminação:** Certifique-se que o livro está bem iluminado
2. **Foco:** Use alta resolução (300+ DPI)
3. **Alinhamento:** Tente deixar as páginas o mais reto possível
4. **Limpeza:** Remova sombras de dedos ou objetos

### Redimensionar imagens em lote:

```bash
# Redimensionar todas as imagens JPG para 50% do tamanho
for img in *.jpg; do
  convert "$img" -resize 50% "resized_$img"
done
```

---

## Solucionando problemas

### OCR com qualidade baixa:

```bash
# 1. Tente com pré-processamento
python book_scanner.py -i ./scans -o ./livro.pdf -l por --preprocess True

# 2. Use qualidade alta
python book_scanner.py -i ./scans -o ./livro.pdf -l por -q high

# 3. Verifique a qualidade das imagens
```

### Processo muito lento:

```bash
# Use qualidade baixa e desative pré-processamento
python book_scanner.py -i ./scans -o ./livro.pdf -l por -q low --preprocess False
```

### Erro "tesseract not found":

```bash
# Reinstale Tesseract
sudo apt-get install tesseract-ocr tesseract-ocr-por tesseract-ocr-eng
```

---

## Estrutura esperada de pastas

```
meu_projeto/
├── scans/                  # Pasta com suas imagens
│   ├── page_001.jpg
│   ├── page_002.jpg
│   ├── page_003.jpg
│   └── page_004.jpg
├── output/                 # Pasta para PDFs gerados
└── book_scanner.py
```

---

## Performance esperada

| Qualidade | Tempo/página | 100 páginas |
|-----------|-------------|-------------|
| low       | 3-5s        | 5-8 min     |
| medium    | 5-8s        | 8-13 min    |
| high      | 8-15s       | 13-25 min   |

*Estimativas em máquina com processador médio (Intel i5)*

---

## Próximas melhorias

- [ ] Processamento paralelo de imagens
- [ ] Interface gráfica (Tkinter)
- [ ] Suporte a mais idiomas
- [ ] Compressão inteligente de PDFs
- [ ] Webhook para processamento em background
