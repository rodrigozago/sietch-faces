# 🚀 Quick Start com Docker + PostgreSQL

## Passo a Passo Rápido

### 1️⃣ Iniciar PostgreSQL

```bash
# Iniciar containers (PostgreSQL + pgAdmin)
docker-compose up -d

# Verificar se estão rodando
docker-compose ps
```

**Resultado esperado:**
```
NAME                    STATUS    PORTS
sietch_faces_db         Up        0.0.0.0:5432->5432/tcp
sietch_faces_pgadmin    Up        0.0.0.0:5050->80/tcp
```

### 2️⃣ Configurar .env

```bash
# Se não tiver .env, criar:
cp .env.example .env

# Editar .env e garantir:
DATABASE_URL=postgresql://sietch_user:sietch_password@localhost:5432/sietch_faces
```

### 3️⃣ Instalar psycopg2

```bash
# Ativar venv
source venv/bin/activate  # Linux/Mac/WSL
# ou
venv\Scripts\activate     # Windows

# Instalar driver PostgreSQL
pip install psycopg2-binary
```

### 4️⃣ Criar Tabelas

```bash
# Inicializar banco de dados
python -m app.database
```

**Resultado esperado:**
```
Database initialized successfully!
```

### 5️⃣ Iniciar API

```bash
uvicorn app.main:app --reload
```

### 6️⃣ Testar

Abra no navegador:
- **API Docs**: http://localhost:8000/docs
- **pgAdmin**: http://localhost:5050

---

## 🎯 Comandos Essenciais

```bash
# Ver logs do PostgreSQL
docker-compose logs -f postgres

# Parar containers
docker-compose stop

# Iniciar containers
docker-compose start

# Remover tudo (⚠️ deleta dados!)
docker-compose down -v

# Backup do banco
docker-compose exec -T postgres pg_dump -U sietch_user sietch_faces > backup.sql

# Restore do backup
docker-compose exec -T postgres psql -U sietch_user -d sietch_faces < backup.sql
```

---

## 📊 Acessar pgAdmin

1. Acesse: http://localhost:5050
2. Login: `admin@sietch.local` / `admin`
3. Add Server:
   - **Name**: Sietch Faces
   - **Host**: `postgres`
   - **Port**: `5432`
   - **Database**: `sietch_faces`
   - **User**: `sietch_user`
   - **Password**: `sietch_password`

---

## ✅ Checklist

- [ ] Docker e Docker Compose instalados
- [ ] `docker-compose up -d` executado com sucesso
- [ ] `.env` configurado com PostgreSQL URL
- [ ] `psycopg2-binary` instalado
- [ ] Tabelas criadas com `python -m app.database`
- [ ] API rodando em http://localhost:8000
- [ ] Upload de teste funcionando

---

## 🐛 Problemas Comuns

### Erro: "port 5432 already in use"

**Solução 1**: Parar PostgreSQL local
```bash
# Linux
sudo systemctl stop postgresql

# Windows
net stop postgresql-x64-15

# Mac
brew services stop postgresql
```

**Solução 2**: Mudar porta no docker-compose.yml
```yaml
ports:
  - "5433:5432"  # Usar 5433
```
E atualizar .env:
```
DATABASE_URL=postgresql://sietch_user:sietch_password@localhost:5433/sietch_faces
```

### Erro: "could not connect to server"

```bash
# Verificar se container está rodando
docker-compose ps

# Ver logs
docker-compose logs postgres

# Reiniciar
docker-compose restart postgres
```

### Erro: "ModuleNotFoundError: No module named 'psycopg2'"

```bash
pip install psycopg2-binary
```

---

📖 **Documentação completa**: [DOCKER_GUIDE.md](DOCKER_GUIDE.md)
