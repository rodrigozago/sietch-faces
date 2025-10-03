# 🚀 Quick Testing Guide

## Overview

Este guia mostra como testar rapidamente a nova arquitetura de microserviços.

---

## 📋 Pre-requisitos

### 1. Instalar dependências do Core API
```bash
cd c:/PersonalWorkspace/sietch-faces
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente (Core)
Crie `.env` na raiz:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/sietch_core
UPLOAD_DIR=uploads
MAX_UPLOAD_SIZE=10485760
```

### 3. Configurar database do Core
```bash
# Criar database
createdb sietch_core

# Aplicar schema (será criado automaticamente no startup)
```

### 4. Instalar dependências do BFF
```bash
cd frontend
npm install
```

### 5. Configurar variáveis de ambiente (BFF)
Crie `frontend/.env`:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/sietch_bff
NEXTAUTH_SECRET=your-secret-key-here
NEXTAUTH_URL=http://localhost:3000
CORE_API_URL=http://localhost:8000
```

### 6. Aplicar schema do BFF
```bash
cd frontend
npx prisma db push
```

---

## 🧪 Fase 1: Testar Core API (Isoladamente)

### 1.1. Iniciar Core API
```bash
cd c:/PersonalWorkspace/sietch-faces
python -m uvicorn app.main_core:app --reload --port 8000
```

Você deve ver:
```
=====================================
🚀 Sietch Faces Core API v2.0.0
=====================================
📍 Pure Facial Recognition Microservice
🔓 No Authentication Required
📡 Ready for integration with any application
=====================================

INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 1.2. Verificar Health
```bash
curl http://localhost:8000/health
```

Resposta esperada:
```json
{
  "status": "healthy",
  "version": "2.0.0-core",
  "database": "connected",
  "models_loaded": true
}
```

### 1.3. Testar Face Detection
```bash
curl -X POST http://localhost:8000/detect \
  -F "file=@test-image.jpg" \
  -F "min_confidence=0.9" \
  -F "auto_save=true"
```

Resposta esperada:
```json
{
  "faces": [
    {
      "bbox": {"x": 100, "y": 50, "width": 200, "height": 250},
      "confidence": 0.99,
      "embedding": [0.123, 0.456, ..., 0.789]
    }
  ],
  "image_path": "uploads/abc123.jpg",
  "processing_time_ms": 1234.56
}
```

### 1.4. Testar Person Management
```bash
# Listar persons
curl http://localhost:8000/persons

# Criar person
curl -X POST http://localhost:8000/persons \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Person",
    "metadata": {"source": "test"}
  }'

# Ver person com faces
curl http://localhost:8000/persons/1
```

### 1.5. Testar Similarity Search
```bash
# Primeiro, pegue um embedding do /detect
# Depois, busque faces similares
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "embedding": [0.123, 0.456, ...],
    "threshold": 0.6,
    "limit": 10
  }'
```

### 1.6. Verificar Stats
```bash
curl http://localhost:8000/stats
```

Resposta esperada:
```json
{
  "total_persons": 5,
  "total_faces": 23,
  "total_unclustered_faces": 2,
  "avg_faces_per_person": 4.6,
  "largest_person_id": 3,
  "largest_person_face_count": 12
}
```

✅ **Core API está funcionando se todos os testes acima passarem!**

---

## 🧪 Fase 2: Testar BFF API (Com Core)

### 2.1. Manter Core API rodando (Terminal 1)
```bash
# Terminal 1 - Core API
python -m uvicorn app.main_core:app --reload --port 8000
```

### 2.2. Iniciar BFF (Terminal 2)
```bash
# Terminal 2 - BFF
cd frontend
npm run dev
```

Você deve ver:
```
▲ Next.js 15.x.x
- Local:   http://localhost:3000
- Ready in 2.5s
```

### 2.3. Testar Registration Flow

**Opção A: Via Postman**
1. Importar `Sietch_Faces_BFF_API.postman_collection.json`
2. Executar "Authentication → Register"
3. Verificar que retornou `user.id`, `autoAlbumId`, `corePersonId`

**Opção B: Via cURL**
```bash
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "SecurePassword123!",
    "faceImageBase64": "data:image/jpeg;base64,/9j/4AAQ..."
  }'
```

Resposta esperada:
```json
{
  "message": "Registration successful",
  "user": {
    "id": "uuid-123",
    "email": "test@example.com",
    "username": "testuser",
    "corePersonId": 1,
    "autoAlbumId": "uuid-456"
  }
}
```

**Verificações:**
1. ✅ Usuário criado no BFF database
2. ✅ Person criado no Core API (check `http://localhost:8000/persons/1`)
3. ✅ Auto-album criado: "Photos of testuser"
4. ✅ Face detectada e salva no Core

### 2.4. Testar Album Creation
```bash
# Usar token do registro
curl -X POST http://localhost:3000/api/albums \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "Summer 2024",
    "description": "Beach photos",
    "albumType": "personal",
    "isPrivate": true
  }'
```

### 2.5. Testar Photo Upload com Auto-Association
```bash
# Upload para o album criado
curl -X POST http://localhost:3000/api/photos/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@group-photo.jpg" \
  -F "albumId=ALBUM_UUID"
```

Resposta esperada:
```json
{
  "message": "Photo uploaded and processed successfully",
  "photo": {
    "id": "photo-uuid",
    "imagePath": "uploads/xyz.jpg",
    "uploadedAt": "2025-01-03T20:00:00",
    "coreFaceIds": [10, 11, 12],
    "facesDetected": 3,
    "autoAddedToAlbums": ["auto-album-uuid-1", "auto-album-uuid-2"]
  }
}
```

**Verificações:**
1. ✅ Foto salva em `uploads/`
2. ✅ BFF chamou Core `/detect`
3. ✅ Faces detectadas e salvas no Core
4. ✅ Foto adicionada ao album especificado
5. ✅ Foto **automaticamente adicionada** aos auto-albums dos usuários detectados

### 2.6. Verificar Auto-Albums
```bash
# Listar albums
curl http://localhost:3000/api/albums \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Você deve ver:
- ✅ Album pessoal "Summer 2024"
- ✅ Auto-album "Photos of testuser" (com fotos onde testuser aparece)

```bash
# Ver fotos do auto-album
curl http://localhost:3000/api/albums/AUTO_ALBUM_UUID/photos \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2.7. Testar Claim Flow
```bash
# Ver unclaimed matches
curl http://localhost:3000/api/users/me/unclaimed \
  -H "Authorization: Bearer YOUR_TOKEN"

# Claim person clusters
curl -X POST http://localhost:3000/api/users/me/claim \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "corePersonIds": [10, 15]
  }'
```

Resposta esperada:
```json
{
  "message": "Successfully claimed 2 person clusters",
  "facesTransferred": 18,
  "photosAddedToAutoAlbum": 15,
  "newCorePersonId": 1
}
```

**Verificações:**
1. ✅ Persons no Core foram merged
2. ✅ Fotos antigas foram adicionadas ao auto-album do usuário
3. ✅ User.corePersonId atualizado

---

## 🧪 Fase 3: Testar Integração End-to-End

### Cenário: Upload com múltiplas pessoas

1. **Usuário A registra**
   - Creates Person 1 in Core
   - Creates auto-album "Photos of UserA"

2. **Usuário B registra**
   - Creates Person 2 in Core
   - Creates auto-album "Photos of UserB"

3. **Usuário A faz upload de foto com A e B**
   - Photo uploaded
   - Core detects 2 faces
   - Face 1 matches Person 1 (UserA)
   - Face 2 matches Person 2 (UserB)
   - Photo added to UserA's personal album
   - Photo **automatically added** to UserA's auto-album
   - Photo **automatically added** to UserB's auto-album

4. **Verificação**
   - UserA sees photo in personal album + auto-album
   - UserB sees photo in auto-album (mesmo sem fazer upload)

### Test Script
```bash
#!/bin/bash

echo "=== Testing Multi-User Photo Sharing ==="

# Register User A
echo "1. Registering User A..."
RESPONSE_A=$(curl -s -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usera@test.com",
    "username": "usera",
    "password": "Password123!",
    "faceImageBase64": "..."
  }')

TOKEN_A=$(echo $RESPONSE_A | jq -r '.token')
AUTO_ALBUM_A=$(echo $RESPONSE_A | jq -r '.user.autoAlbumId')

echo "✓ User A created with auto-album: $AUTO_ALBUM_A"

# Register User B
echo "2. Registering User B..."
RESPONSE_B=$(curl -s -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "userb@test.com",
    "username": "userb",
    "password": "Password123!",
    "faceImageBase64": "..."
  }')

TOKEN_B=$(echo $RESPONSE_B | jq -r '.token')
AUTO_ALBUM_B=$(echo $RESPONSE_B | jq -r '.user.autoAlbumId')

echo "✓ User B created with auto-album: $AUTO_ALBUM_B"

# Create personal album for User A
echo "3. Creating personal album for User A..."
ALBUM_RESPONSE=$(curl -s -X POST http://localhost:3000/api/albums \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN_A" \
  -d '{
    "name": "Our Photos",
    "albumType": "personal"
  }')

ALBUM_ID=$(echo $ALBUM_RESPONSE | jq -r '.id')
echo "✓ Personal album created: $ALBUM_ID"

# Upload photo with both users
echo "4. Uploading photo with User A and User B..."
PHOTO_RESPONSE=$(curl -s -X POST http://localhost:3000/api/photos/upload \
  -H "Authorization: Bearer $TOKEN_A" \
  -F "file=@group-photo.jpg" \
  -F "albumId=$ALBUM_ID")

PHOTO_ID=$(echo $PHOTO_RESPONSE | jq -r '.photo.id')
AUTO_ADDED=$(echo $PHOTO_RESPONSE | jq -r '.photo.autoAddedToAlbums')

echo "✓ Photo uploaded: $PHOTO_ID"
echo "✓ Auto-added to albums: $AUTO_ADDED"

# Check User A's auto-album
echo "5. Checking User A's auto-album..."
PHOTOS_A=$(curl -s http://localhost:3000/api/albums/$AUTO_ALBUM_A/photos \
  -H "Authorization: Bearer $TOKEN_A")

COUNT_A=$(echo $PHOTOS_A | jq '.photos | length')
echo "✓ User A has $COUNT_A photos in auto-album"

# Check User B's auto-album
echo "6. Checking User B's auto-album..."
PHOTOS_B=$(curl -s http://localhost:3000/api/albums/$AUTO_ALBUM_B/photos \
  -H "Authorization: Bearer $TOKEN_B")

COUNT_B=$(echo $PHOTOS_B | jq '.photos | length')
echo "✓ User B has $COUNT_B photos in auto-album"

# Verify photo appears in both
if echo $PHOTOS_A | jq -e ".photos[] | select(.id == \"$PHOTO_ID\")" > /dev/null; then
  echo "✓ Photo appears in User A's auto-album"
else
  echo "✗ Photo NOT in User A's auto-album"
fi

if echo $PHOTOS_B | jq -e ".photos[] | select(.id == \"$PHOTO_ID\")" > /dev/null; then
  echo "✓ Photo appears in User B's auto-album"
else
  echo "✗ Photo NOT in User B's auto-album"
fi

echo "=== Test Complete ==="
```

---

## ✅ Checklist de Validação

### Core API
- [ ] Health check retorna `healthy`
- [ ] Face detection funciona com imagem real
- [ ] Embeddings têm 512 dimensões
- [ ] Similarity search retorna matches
- [ ] Person CRUD funciona
- [ ] Face management funciona
- [ ] Clustering funciona
- [ ] Stats são corretos

### BFF API
- [ ] Registration cria usuário + person + auto-album
- [ ] Login funciona (NextAuth)
- [ ] Album creation funciona
- [ ] Photo upload chama Core `/detect`
- [ ] Faces são detectadas e salvas no Core
- [ ] Photo é adicionada ao album especificado

### Integração
- [ ] Photo upload com 1 face → adicionada ao auto-album do usuário
- [ ] Photo upload com 2+ faces → adicionada aos auto-albums de todos
- [ ] Unclaimed matches são detectados
- [ ] Claim merge funciona corretamente
- [ ] Fotos antigas são adicionadas após claim

### Many-to-Many
- [ ] Mesma foto aparece em múltiplos albums
- [ ] AlbumPhoto junction impede duplicatas
- [ ] Delete photo remove de todos os albums
- [ ] User pode ver fotos em auto-album mesmo sem ter feito upload

---

## 🐛 Troubleshooting

### Core API não inicia
```bash
# Verificar dependências
pip list | grep -E "(fastapi|uvicorn|deepface|retinaface)"

# Verificar database
psql -d sietch_core -c "\dt"

# Ver logs detalhados
python -m uvicorn app.main_core:app --reload --log-level debug
```

### BFF não conecta ao Core
```bash
# Verificar env var
echo $CORE_API_URL

# Testar conexão
curl http://localhost:8000/health

# Ver logs do BFF
npm run dev -- --debug
```

### Faces não são detectadas
```bash
# Verificar formato da imagem
file image.jpg  # Deve ser JPEG ou PNG

# Verificar tamanho
ls -lh image.jpg  # Deve ser < 10MB

# Testar diretamente no Core
curl -X POST http://localhost:8000/detect \
  -F "file=@image.jpg" \
  -F "min_confidence=0.5"  # Lower threshold
```

### Auto-albums não são populados
```bash
# Verificar faces foram detectadas
curl http://localhost:8000/faces

# Verificar similarity search funciona
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"embedding": [...], "threshold": 0.6}'

# Ver logs do BFF durante upload
# Deve mostrar: "Found X matching persons for photo"
```

---

**Próximo passo:** Teste a Core API primeiro, depois o BFF, depois a integração end-to-end!
