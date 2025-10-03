# Sietch Faces - API de Reconhecimento Facial

API para reconhecimento facial e agrupamento automático de fotos da mesma pessoa.

## Características

### 1. Detecção e Extração de Faces
- **RetinaFace** como detector (mais robusto que MTCNN)
- Extrai múltiplas faces de uma única imagem
- Gera bounding boxes e confidence scores

### 2. Geração de Embeddings
- Modelo **ArcFace** para máxima precisão
- Embeddings de 512 dimensões
- Métrica de distância: cosine similarity

### 3. Busca e Agrupamento
- Busca por similaridade em tempo real
- **DBSCAN** para clustering automático
- Threshold ajustável (padrão: 0.4)

### 4. Sistema de Identificação
- Ao nomear uma face, identifica automaticamente faces similares
- Sistema de `person_id` para agrupar múltiplas fotos
- Propagação inteligente de identidades

## Endpoints da API

- `POST /upload` - Upload de imagem e detecção de faces
- `POST /identify` - Identifica uma face por nome
- `GET /person/{person_id}` - Lista todas as fotos de uma pessoa
- `GET /clusters` - Agrupa faces similares automaticamente
- `GET /stats` - Estatísticas do banco
- `DELETE /face/{face_id}` - Remove uma face

## Instalação

1. Clone o repositório
2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure o banco de dados:
```bash
python -m app.database
```

5. Execute a API:
```bash
uvicorn app.main:app --reload
```

A API estará disponível em `http://localhost:8000`

## Documentação

Acesse `http://localhost:8000/docs` para a documentação interativa (Swagger UI).

## Estrutura do Projeto

```
sietch-faces/
├── app/
│   ├── main.py              # FastAPI app principal
│   ├── config.py            # Configurações
│   ├── database.py          # Configuração do banco
│   ├── models.py            # Modelos SQLAlchemy
│   ├── schemas.py           # Schemas Pydantic
│   ├── face_detection.py    # RetinaFace detector
│   ├── face_recognition.py  # ArcFace embeddings
│   ├── clustering.py        # DBSCAN clustering
│   └── routes/
│       ├── upload.py
│       ├── identify.py
│       ├── person.py
│       ├── clusters.py
│       └── stats.py
├── uploads/                 # Imagens uploaded
├── models/                  # Modelos pré-treinados
├── tests/                   # Testes
├── requirements.txt
└── README.md
```

## Tecnologias

- **FastAPI** - Framework web
- **RetinaFace** - Detecção de faces
- **ArcFace** - Geração de embeddings
- **SQLAlchemy** - ORM
- **PostgreSQL/SQLite** - Banco de dados
- **scikit-learn** - DBSCAN clustering
- **NumPy** - Operações matemáticas
