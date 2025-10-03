# 🐳 Docker Setup Guide

## 📦 O que está incluído

### Serviços Docker Compose:

1. **PostgreSQL 15** (Alpine)
   - Porta: 5432
   - Usuário: `sietch_user`
   - Senha: `sietch_password`
   - Database: `sietch_faces`

2. **pgAdmin 4** (Interface Web)
   - Porta: 5050
   - Email: `admin@sietch.local`
   - Senha: `admin`

## 🚀 Como Usar

### 1. Iniciar os containers

```bash
# Iniciar PostgreSQL e pgAdmin
docker-compose up -d

# Ver logs
docker-compose logs -f

# Verificar status
docker-compose ps
```

### 2. Atualizar o arquivo .env

```bash
# Copie o exemplo se ainda não tiver
cp .env.example .env

# Edite o .env e certifique-se que está assim:
DATABASE_URL=postgresql://sietch_user:sietch_password@localhost:5432/sietch_faces
```

### 3. Instalar driver PostgreSQL

```bash
# Ativar venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instalar psycopg2
pip install psycopg2-binary
```

### 4. Inicializar o banco de dados

```bash
# Criar tabelas
python -m app.database

# Ou usar o script de reset
python reset_database.py
```

### 5. Iniciar a API

```bash
uvicorn app.main:app --reload
```

## 🎯 Acessar os Serviços

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| API | http://localhost:8000 | - |
| API Docs | http://localhost:8000/docs | - |
| PostgreSQL | localhost:5432 | user: sietch_user<br>pass: sietch_password |
| pgAdmin | http://localhost:5050 | email: admin@sietch.local<br>pass: admin |

## 🔧 Comandos Úteis

### Gerenciar Containers

```bash
# Parar containers
docker-compose stop

# Iniciar containers parados
docker-compose start

# Reiniciar containers
docker-compose restart

# Parar e remover containers
docker-compose down

# Parar e remover containers + volumes (⚠️ DELETA DADOS)
docker-compose down -v
```

### Ver Logs

```bash
# Todos os serviços
docker-compose logs -f

# Apenas PostgreSQL
docker-compose logs -f postgres

# Últimas 100 linhas
docker-compose logs --tail=100
```

### Acessar o Container

```bash
# Shell do PostgreSQL
docker-compose exec postgres psql -U sietch_user -d sietch_faces

# Shell bash
docker-compose exec postgres bash
```

## 📊 Configurar pgAdmin

1. Acesse http://localhost:5050
2. Login com `admin@sietch.local` / `admin`
3. Clique em **Add New Server**
4. Configure:

**General Tab:**
- Name: `Sietch Faces Local`

**Connection Tab:**
- Host: `postgres` (nome do serviço no Docker)
- Port: `5432`
- Database: `sietch_faces`
- Username: `sietch_user`
- Password: `sietch_password`
- Save Password: ✅ Yes

5. Clique em **Save**

## 🔍 Consultas Úteis no PostgreSQL

```sql
-- Ver todas as tabelas
\dt

-- Ver estrutura da tabela faces
\d faces

-- Contar faces
SELECT COUNT(*) FROM faces;

-- Contar pessoas
SELECT COUNT(*) FROM persons;

-- Ver pessoas com número de faces
SELECT 
    p.id, 
    p.name, 
    COUNT(f.id) as face_count 
FROM persons p 
LEFT JOIN faces f ON f.person_id = p.id 
GROUP BY p.id, p.name;

-- Ver faces não identificadas
SELECT COUNT(*) FROM faces WHERE person_id IS NULL;
```

## 🔄 Backup e Restore

### Backup

```bash
# Backup do banco completo
docker-compose exec -T postgres pg_dump -U sietch_user sietch_faces > backup.sql

# Backup com data
docker-compose exec -T postgres pg_dump -U sietch_user sietch_faces > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restore

```bash
# Restore do backup
docker-compose exec -T postgres psql -U sietch_user -d sietch_faces < backup.sql
```

## 🐛 Troubleshooting

### Porta 5432 já em uso

Se você já tem PostgreSQL instalado localmente:

**Opção 1:** Mudar a porta no docker-compose.yml:
```yaml
ports:
  - "5433:5432"  # Usar porta 5433 externamente
```

Então atualizar o .env:
```
DATABASE_URL=postgresql://sietch_user:sietch_password@localhost:5433/sietch_faces
```

**Opção 2:** Parar o PostgreSQL local:
```bash
# Windows
net stop postgresql-x64-15

# Linux
sudo systemctl stop postgresql

# Mac
brew services stop postgresql
```

### Container não inicia

```bash
# Ver logs de erro
docker-compose logs postgres

# Remover volumes e recriar
docker-compose down -v
docker-compose up -d
```

### Erro de conexão da API

Verifique:
1. ✅ Container está rodando: `docker-compose ps`
2. ✅ DATABASE_URL no .env está correto
3. ✅ psycopg2-binary está instalado: `pip list | grep psycopg2`
4. ✅ Tabelas foram criadas: `python -m app.database`

## 📈 Performance

### Configurações recomendadas para produção

Edite o `docker-compose.yml` e adicione ao serviço postgres:

```yaml
command:
  - "postgres"
  - "-c"
  - "max_connections=200"
  - "-c"
  - "shared_buffers=256MB"
  - "-c"
  - "effective_cache_size=1GB"
  - "-c"
  - "maintenance_work_mem=64MB"
  - "-c"
  - "checkpoint_completion_target=0.9"
  - "-c"
  - "wal_buffers=16MB"
  - "-c"
  - "default_statistics_target=100"
```

## 🔐 Segurança

### Para Produção:

1. **Mudar senhas padrão**
   ```yaml
   environment:
     POSTGRES_PASSWORD: senha_forte_aqui
     PGADMIN_DEFAULT_PASSWORD: outra_senha_forte
   ```

2. **Não expor portas desnecessárias**
   ```yaml
   # Comentar se não precisar acessar externamente
   # ports:
   #   - "5432:5432"
   ```

3. **Usar secrets do Docker**
   ```yaml
   secrets:
     - db_password
   ```

## 📝 Variáveis de Ambiente

Você pode sobrescrever as configurações criando um `.env.docker`:

```env
POSTGRES_USER=seu_usuario
POSTGRES_PASSWORD=sua_senha
POSTGRES_DB=seu_banco
PGADMIN_EMAIL=seu@email.com
PGADMIN_PASSWORD=sua_senha_admin
```

Então usar:
```bash
docker-compose --env-file .env.docker up -d
```

---

## ✅ Checklist Rápido

- [ ] `docker-compose up -d` executado
- [ ] `.env` atualizado com DATABASE_URL do PostgreSQL
- [ ] `pip install psycopg2-binary` executado
- [ ] `python -m app.database` executado
- [ ] API iniciada com `uvicorn app.main:app --reload`
- [ ] http://localhost:8000/docs acessível
- [ ] Upload de teste funcionando

🎉 **Tudo pronto para usar PostgreSQL com Docker!**
