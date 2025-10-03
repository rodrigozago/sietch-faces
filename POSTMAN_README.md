# 📦 Arquivos para Postman

Este diretório contém os arquivos necessários para testar a API no Postman.

## 📥 Arquivos Disponíveis

### 1. `Sietch_Faces_API.postman_collection.json`
**Collection completa da API** com todos os endpoints:
- ✅ Health Check
- ✅ Upload de Imagens
- ✅ Identificação de Faces
- ✅ Gerenciamento de Pessoas
- ✅ Clustering Automático
- ✅ Estatísticas

### 2. `Sietch_Faces_Local.postman_environment.json`
**Environment configurado** para ambiente local:
- `baseUrl`: http://localhost:8000
- `face_id`: Preenchido automaticamente
- `person_id`: Para uso manual

### 3. `POSTMAN_GUIDE.md`
**Guia completo de uso** com:
- Instruções de importação
- Fluxos de teste
- Cenários práticos
- Troubleshooting

## 🚀 Como Usar

### Importar no Postman

1. Abra o Postman
2. Clique em **Import**
3. Arraste os arquivos JSON:
   - `Sietch_Faces_API.postman_collection.json`
   - `Sietch_Faces_Local.postman_environment.json`
4. Selecione o environment "Sietch Faces - Local"
5. Pronto! Comece pelo endpoint "Health Check"

### Fluxo Rápido

```
1. Health Check → Verificar API
2. Upload Image → Detectar faces
3. Identify Face → Nomear pessoa
4. Get Clusters → Ver grupos
5. Get Stats → Ver estatísticas
```

## 📚 Documentação

Para instruções detalhadas, consulte [POSTMAN_GUIDE.md](POSTMAN_GUIDE.md)

## 🔗 Links Úteis

- **API Local**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## ⚡ Importação Rápida via URL

Você também pode importar direto do OpenAPI:
1. No Postman → **Import** → **Link**
2. Cole: `http://localhost:8000/openapi.json`
3. Import!

---

✅ Tudo pronto para testar a API!
