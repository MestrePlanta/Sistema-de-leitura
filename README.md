# Sistema de Leitura - Scanner OCR

Ferramenta automática para converter fotos de scanner de livros em PDFs pesquisáveis com OCR (Reconhecimento Óptico de Caracteres).

## Recursos

✅ Converte múltiplas imagens (JPG, PNG) em PDF pesquisável
✅ OCR em português brasileiro e inglês
✅ Pré-processamento de imagens (correção de skew, limpeza)
✅ Interface de linha de comando simples
✅ Processamento em lote
✅ Suporte a diferentes idiomas

## Requisitos

- Python 3.8+
- Ubuntu/Linux

## Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/MestrePlanta/Sistema-de-leitura.git
cd Sistema-de-leitura
```

### 2. Instale as dependências

```bash
# Instale as ferramentas do sistema
sudo apt-get update
sudo apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-por \
    tesseract-ocr-eng \
    libtesseract-dev \
    ghostscript \
    imagemagick

# Instale as dependências Python
pip install -r requirements.txt
```

## Uso

### Converter uma pasta de imagens

```bash
python book_scanner.py -i /caminho/para/imagens -o /caminho/saida/livro.pdf -l por
```

### Opções

- `-i, --input` - Pasta contendo as imagens do scanner (obrigatório)
- `-o, --output` - Caminho do arquivo PDF de saída (obrigatório)
- `-l, --language` - Idioma do OCR: `por` (português), `eng` (inglês) ou `por+eng` (ambos) - padrão: `por`
- `-p, --preprocess` - Aplicar pré-processamento de imagens (padrão: True)
- `-q, --quality` - Qualidade de imagem: `low`, `medium`, `high` - padrão: `high`
- `-v, --verbose` - Modo verbose (mais informações)

### Exemplos

```bash
# Converter livro em português
python book_scanner.py -i ./scans -o ./livro_saida.pdf -l por -v

# Converter livro em inglês
python book_scanner.py -i ./scans -o ./book_output.pdf -l eng

# Converter livro com português e inglês
python book_scanner.py -i ./scans -o ./livro_bilingue.pdf -l por+eng

# Sem pré-processamento (mais rápido)
python book_scanner.py -i ./scans -o ./livro.pdf -l por --preprocess False
```

## Estrutura de Pastas

```
Sistema-de-leitura/
├── README.md
├── requirements.txt
├── book_scanner.py           # Script principal
├── config.yaml               # Arquivo de configuração
├── example_input/            # Pasta de exemplo com imagens
└── example_output/           # Pasta de saída (criada automaticamente)
```

## Configuração Avançada

Edite `config.yaml` para personalizar:

```yaml
ocr:
  languages:
    - por      # português
    - eng      # inglês
  confidence_threshold: 0.5

preprocessing:
  deskew: true
  denoise: true
  contrast_enhancement: true

output:
  pdf_quality: high
  compression: true
```

## Troubleshooting

### Erro: "tesseract not found"

```bash
sudo apt-get install tesseract-ocr
```

### Erro: "Portuguese language data not found"

```bash
sudo apt-get install tesseract-ocr-por
```

### OCR com qualidade baixa

- Use `-q high` para melhor qualidade
- Certifique-se que as imagens estão bem iluminadas e nítidas
- Use `-p True` para ativar pré-processamento

## Performance

- Imagens de 300 DPI: ~5-10 segundos por página
- Livro de 100 páginas: ~10-20 minutos
- Use `-q low` para processar mais rapidamente (sacrificando qualidade)

## Licença

MIT

## Contribuições

Pull requests são bem-vindos!
