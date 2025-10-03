# Guia de Uso - Postman para Sietch Faces API

## 📥 Importar no Postman

### Opção 1: Importar Collection e Environment

1. Abra o Postman
2. Clique em **Import** (botão no canto superior esquerdo)
3. Arraste os arquivos ou clique em **Upload Files**:
   - `Sietch_Faces_API.postman_collection.json`
   - `Sietch_Faces_Local.postman_environment.json`
4. Clique em **Import**

### Opção 2: Importar da URL do Swagger

1. No Postman, clique em **Import**
2. Selecione a aba **Link**
3. Cole: `http://localhost:8000/openapi.json`
4. Clique em **Continue** e depois **Import**

## ⚙️ Configurar Environment

1. No canto superior direito, selecione **Sietch Faces - Local** no dropdown de environments
2. As variáveis já estão configuradas:
   - `baseUrl`: http://localhost:8000
   - `face_id`: será preenchido automaticamente após upload
   - `person_id`: você pode preencher manualmente

## 🚀 Fluxo de Uso Completo

### 1. Health Check
- **Endpoint**: `GET /health`
- **Objetivo**: Verificar se a API está funcionando
- ✅ Deve retornar: `{"status": "healthy"}`

### 2. Upload de Imagem
- **Endpoint**: `POST /upload`
- **Como usar**:
  1. Clique na requisição "Upload Image"
  2. Vá na aba **Body**
  3. Em **file**, clique em **Select Files**
  4. Escolha uma imagem com faces
  5. Clique em **Send**
- **Resposta**: Lista de faces detectadas
- ⭐ **Importante**: O `face_id` é salvo automaticamente!

**Exemplo de resposta**:
```json
{
  "filename": "abc123.jpg",
  "faces_detected": 2,
  "faces": [
    {
      "id": 1,
      "image_path": "uploads/abc123.jpg",
      "x": 100,
      "y": 150,
      "width": 200,
      "height": 250,
      "confidence": 0.998,
      "person_id": null,
      "created_at": "2025-10-02T21:00:00"
    }
  ]
}
```

### 3. Identificar uma Face
- **Endpoint**: `POST /identify`
- **Como usar**:
  1. O `face_id` já está preenchido automaticamente
  2. Edite o campo `name` no body com o nome da pessoa
  3. `auto_identify_similar`: true para identificar faces similares automaticamente
  4. Clique em **Send**
- **Resposta**: Pessoa criada + faces similares identificadas

**Body de exemplo**:
```json
{
  "face_id": 1,
  "name": "João Silva",
  "auto_identify_similar": true
}
```

### 4. Ver Todas as Faces de uma Pessoa
- **Endpoint**: `GET /person/{person_id}`
- **Como usar**:
  1. Pegue o `person_id` da resposta anterior
  2. Substitua `{{person_id}}` ou edite a variável
  3. Clique em **Send**
- **Resposta**: Informações da pessoa + todas as suas faces

### 5. Ver Clusters (Agrupamento Automático)
- **Endpoint**: `GET /clusters`
- **Como usar**:
  1. Simplesmente clique em **Send**
  2. O parâmetro `only_unidentified=true` mostra apenas faces não identificadas
- **Resposta**: Grupos de faces similares
- 💡 **Útil para**: Encontrar pessoas que ainda não foram identificadas

### 6. Ver Estatísticas
- **Endpoint**: `GET /stats`
- **Como usar**:
  1. Clique em **Send**
- **Resposta**: Estatísticas gerais do banco
```json
{
  "total_faces": 50,
  "identified_faces": 30,
  "unidentified_faces": 20,
  "total_persons": 8,
  "total_images": 25
}
```

### 7. Listar Todas as Pessoas
- **Endpoint**: `GET /person`
- **Parâmetros**:
  - `skip`: Paginação (padrão: 0)
  - `limit`: Máximo de resultados (padrão: 100)
- **Resposta**: Lista de todas as pessoas identificadas

### 8. Deletar uma Face
- **Endpoint**: `DELETE /stats/face/{face_id}`
- **Como usar**:
  1. Substitua `{{face_id}}` pelo ID da face
  2. Clique em **Send**
- **Resposta**: Confirmação de deleção

### 9. Deletar uma Pessoa
- **Endpoint**: `DELETE /person/{person_id}`
- **Como usar**:
  1. Substitua `{{person_id}}` pelo ID da pessoa
  2. Clique em **Send**
- ⚠️ **Atenção**: As faces são desvinculadas, mas não deletadas

## 📝 Variáveis Disponíveis

| Variável | Descrição | Preenchimento |
|----------|-----------|---------------|
| `{{baseUrl}}` | URL base da API | Automático |
| `{{face_id}}` | ID da face | Automático após upload |
| `{{person_id}}` | ID da pessoa | Manual |

## 🎯 Cenários de Teste

### Cenário 1: Identificar Pessoa em Múltiplas Fotos

1. ✅ Upload foto 1 → Pega `face_id`: 1
2. ✅ Upload foto 2 → Pega `face_id`: 2
3. ✅ Upload foto 3 → Pega `face_id`: 3
4. ✅ Identify face 1 como "João Silva" com `auto_identify_similar: true`
5. ✅ Resultado: Sistema identifica automaticamente faces 2 e 3 se forem similares!

### Cenário 2: Usar Clusters para Identificação em Lote

1. ✅ Upload múltiplas fotos
2. ✅ GET /clusters → Ver grupos de faces similares
3. ✅ Identify uma face de cada cluster
4. ✅ Sistema identifica todas as faces do cluster automaticamente

### Cenário 3: Gerenciar Pessoas

1. ✅ GET /person → Ver todas as pessoas
2. ✅ GET /person/1 → Ver detalhes de uma pessoa específica
3. ✅ DELETE /person/1 → Remover pessoa (faces ficam desvinculadas)

## 🔧 Dicas

### Configurar Timeout
Se uploads grandes demorarem:
1. Vá em Settings (⚙️)
2. Aumente o **Request timeout** para 60000ms (60 segundos)

### Salvar Respostas
Use a aba **Tests** para salvar dados automaticamente:
```javascript
// Exemplo: Salvar person_id da resposta
if (pm.response.code === 200) {
    var jsonData = pm.response.json();
    pm.environment.set('person_id', jsonData.person_id);
}
```

### Testar em Lote
Use o **Collection Runner** para executar múltiplas requisições em sequência.

## ❓ Troubleshooting

### Erro: "Could not get response"
- ✅ Verifique se a API está rodando: `http://localhost:8000/health`
- ✅ Confirme o environment está selecionado
- ✅ Verifique se a porta 8000 está livre

### Erro 400: "No faces detected"
- ✅ Use imagens com faces claras e visíveis
- ✅ Mínimo 20x20 pixels por face
- ✅ Boa iluminação

### Erro 404: "Face not found"
- ✅ Verifique se o `face_id` existe
- ✅ Use GET /stats para ver quantas faces existem

## 📚 Recursos Adicionais

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🎨 Organização da Collection

A collection está organizada por funcionalidade:

```
📁 Sietch Faces API
  ├── 🔍 Health Check
  ├── 🏠 Root
  ├── 📤 Upload Image
  ├── 🆔 Identify Face
  ├── 👤 Get Person by ID
  ├── 📋 List All Persons
  ├── ❌ Delete Person
  ├── 🔗 Get Clusters
  ├── 📊 Get Statistics
  └── 🗑️ Delete Face
```

---

**✅ Pronto para usar!** Comece pelo Health Check e depois faça upload de uma imagem com faces.
