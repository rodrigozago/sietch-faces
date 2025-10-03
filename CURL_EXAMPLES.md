# 🧪 Exemplos de Testes Rápidos (curl)

Para quem prefere testar via linha de comando.

## 🏥 Health Check

```bash
curl http://localhost:8000/health
```

**Resposta esperada:**
```json
{"status": "healthy"}
```

## 📤 Upload de Imagem

```bash
curl -X POST "http://localhost:8000/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/caminho/para/sua/imagem.jpg"
```

**Exemplo Windows (PowerShell):**
```powershell
curl.exe -X POST "http://localhost:8000/upload" `
  -H "Content-Type: multipart/form-data" `
  -F "file=@C:\Users\SeuUsuario\Pictures\foto.jpg"
```

## 🆔 Identificar uma Face

```bash
curl -X POST "http://localhost:8000/identify" \
  -H "Content-Type: application/json" \
  -d '{
    "face_id": 1,
    "name": "João Silva",
    "auto_identify_similar": true
  }'
```

## 👤 Buscar Pessoa por ID

```bash
curl http://localhost:8000/person/1
```

## 📋 Listar Todas as Pessoas

```bash
curl "http://localhost:8000/person?skip=0&limit=10"
```

## 🔗 Ver Clusters

```bash
curl "http://localhost:8000/clusters?only_unidentified=true"
```

## 📊 Estatísticas

```bash
curl http://localhost:8000/stats
```

## 🗑️ Deletar uma Face

```bash
curl -X DELETE "http://localhost:8000/stats/face/1"
```

## ❌ Deletar uma Pessoa

```bash
curl -X DELETE "http://localhost:8000/person/1"
```

## 🎯 Script Completo de Teste

```bash
#!/bin/bash

echo "🔍 1. Health Check..."
curl http://localhost:8000/health
echo -e "\n"

echo "📊 2. Verificando estatísticas iniciais..."
curl http://localhost:8000/stats
echo -e "\n"

echo "📤 3. Fazendo upload de imagem..."
# Substitua o caminho pela sua imagem
UPLOAD_RESPONSE=$(curl -s -X POST "http://localhost:8000/upload" \
  -F "file=@./test_image.jpg")
echo $UPLOAD_RESPONSE
echo -e "\n"

# Extrai o face_id da resposta (requer jq)
FACE_ID=$(echo $UPLOAD_RESPONSE | jq -r '.faces[0].id')
echo "Face ID detectado: $FACE_ID"
echo -e "\n"

echo "🆔 4. Identificando a face..."
curl -X POST "http://localhost:8000/identify" \
  -H "Content-Type: application/json" \
  -d "{
    \"face_id\": $FACE_ID,
    \"name\": \"Pessoa Teste\",
    \"auto_identify_similar\": true
  }"
echo -e "\n"

echo "📊 5. Estatísticas finais..."
curl http://localhost:8000/stats
echo -e "\n"

echo "✅ Teste completo!"
```

## 💡 Dicas

### Salvar resposta em arquivo
```bash
curl http://localhost:8000/stats > stats.json
```

### Ver headers da resposta
```bash
curl -i http://localhost:8000/health
```

### Modo verbose (debug)
```bash
curl -v http://localhost:8000/health
```

### Pretty print JSON (com jq)
```bash
curl http://localhost:8000/stats | jq
```

## 🪟 Windows PowerShell

No Windows, use `curl.exe` ou `Invoke-WebRequest`:

```powershell
# Com curl.exe
curl.exe http://localhost:8000/health

# Com Invoke-WebRequest
Invoke-WebRequest -Uri "http://localhost:8000/health" | Select-Object -Expand Content

# Upload de arquivo
$form = @{
    file = Get-Item -Path "C:\caminho\imagem.jpg"
}
Invoke-WebRequest -Uri "http://localhost:8000/upload" -Method Post -Form $form
```

---

✅ **Dica**: Para testes mais complexos, use o Postman (veja POSTMAN_GUIDE.md)
