# 🚧 Progresso da Implementação - Next.js BFF

## ✅ Concluído

### Backend (FastAPI)

#### 1. Models Atualizados
- ✅ `User` model criado (com autenticação)
- ✅ `Person` model atualizado (com is_claimed, user_id)
- ✅ `Photo` model criado (para organizar uploads)
- ✅ `Face` model atualizado (com photo_id)

#### 2. Schemas Criados
- ✅ `app/schemas_v2.py` com todos os novos schemas:
  - UserCreate, UserLogin, UserResponse
  - PhotoCreate, PhotoResponse, PhotoWithFaces
  - UnclaimedMatch, ClaimPersonRequest
  - EmailInvitationRequest
  - InternalAuthValidate, InternalPhotoProcess

#### 3. Autenticação e Segurança
- ✅ `app/auth/security.py` - JWT, password hashing
- ✅ `app/auth/dependencies.py` - Auth dependencies
  - get_internal_api_key
  - get_current_user
  - get_current_user_optional
  - get_current_verified_user

#### 4. Serviços de Negócio
- ✅ `app/services/face_matching.py` - Matching inteligente
  - find_similar_faces
  - auto_associate_to_user
  - find_unclaimed_matches
  - suggest_person_merges
  
- ✅ `app/services/claim_service.py` - Gerenciamento de claims
  - claim_persons
  - merge_persons
  - transfer_person_to_user
  - get_user_photos_with_person

#### 5. Configurações
- ✅ `app/config.py` atualizado com:
  - internal_api_key
  - jwt_secret_key
  - smtp settings
  - frontend_url

#### 6. Dependências
- ✅ `requirements.txt` atualizado:
  - passlib[bcrypt]
  - email-validator

---

#### 7. Endpoints Internos (/internal/*)
- ✅ `app/routes/internal.py` - Endpoints para Next.js BFF
  - POST /internal/auth/register (com validação facial)
  - POST /internal/auth/validate (com verificação facial opcional)
  - POST /internal/photos/process (upload e detecção)
  - GET /internal/users/{user_id}/photos
  - GET /internal/users/{user_id}/faces
  - GET /internal/users/{user_id}/unclaimed-matches
  - POST /internal/users/{user_id}/claim
  - GET /internal/users/{user_id}/stats

#### 8. Testes e Documentação
- ✅ `test_internal_api.py` - Script de testes Python
- ✅ `INTERNAL_API_GUIDE.md` - Documentação completa dos endpoints

---

## 🔄 Em Progresso

### Backend (FastAPI)

#### Serviços Adicionais
- ⏳ `app/services/email_service.py`
  - send_welcome_email
  - send_unclaimed_notification
  - send_invitation_email
  
- ⏳ `app/services/photo_service.py`
  - process_photo_upload
  - auto_associate_faces
  - generate_thumbnails

#### Atualizar Endpoints Existentes
- ⏳ `app/routes/upload.py` - Adicionar auto-associação
- ⏳ `app/routes/identify.py` - Integrar com User
- ⏳ `app/routes/person.py` - Adicionar verificação de ownership
- ⏳ `app/routes/stats.py` - Adicionar estatísticas de usuários

#### Main App
- ⏳ `app/main.py` - Incluir novos routers internos

---

## 📋 TODO - Backend

### High Priority
- [ ] Criar migrations do Alembic para novos models
- [ ] Implementar endpoints internos completos
- [ ] Serviço de email (welcome, notifications)
- [ ] Background tasks para processamento pesado
- [ ] Testes unitários dos novos serviços

### Medium Priority
- [ ] Rate limiting middleware
- [ ] Logging estruturado
- [ ] Métricas e monitoring
- [ ] Geração de thumbnails
- [ ] Webhook system para notificações

### Low Priority
- [ ] Caching com Redis
- [ ] Celery para jobs assíncronos
- [ ] Admin dashboard
- [ ] Exportação de dados (GDPR)

---

## 📋 TODO - Frontend (Next.js)

### Estrutura Base
- [ ] Criar projeto Next.js 14+ (App Router)
- [ ] Configurar TypeScript
- [ ] Configurar Tailwind CSS
- [ ] Estrutura de pastas

### Autenticação
- [ ] Instalar e configurar NextAuth.js
- [ ] Credentials Provider com FastAPI
- [ ] Session management
- [ ] Protected routes middleware

### API Routes (BFF)
- [ ] `/api/auth/[...nextauth]/route.ts`
- [ ] `/api/auth/register/route.ts`
- [ ] `/api/photos/upload/route.ts`
- [ ] `/api/user/photos/route.ts`
- [ ] `/api/user/claim/route.ts`
- [ ] `/api/user/unclaimed-matches/route.ts`

### Pages
- [ ] Landing page (`/`)
- [ ] Login page (`/login`)
- [ ] Register page (`/register`) - multi-step com foto
- [ ] Dashboard (`/dashboard`)
- [ ] Photos gallery (`/photos`)
- [ ] People management (`/people`)
- [ ] Settings (`/settings`)

### Components
- [ ] Camera component (face capture)
- [ ] Photo uploader
- [ ] Face detection overlay
- [ ] Unclaimed matches modal
- [ ] Person card
- [ ] Photo grid

### Services/Utils
- [ ] API client com auth
- [ ] Image upload utility
- [ ] Face detection client-side preview
- [ ] Toast notifications
- [ ] Error handling

---

## 🗄️ Database Migration

### Passos Necessários:
1. [ ] Criar migrations Alembic
2. [ ] Backup do banco atual
3. [ ] Rodar migrations
4. [ ] Migrar dados existentes (se houver)

### Script de Migração:
```python
# migrations/migrate_to_v2.py
# 1. Criar tabela users
# 2. Criar tabela photos
# 3. Adicionar campos novos em persons
# 4. Adicionar photo_id em faces
# 5. Migrar dados existentes
```

---

## 🔐 Variáveis de Ambiente

### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql://...

# Security
INTERNAL_API_KEY=generate-strong-key-here
JWT_SECRET_KEY=another-strong-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email (SendGrid/AWS SES/SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@sietch.local

# Frontend
FRONTEND_URL=http://localhost:3000

# Face Recognition
SIMILARITY_THRESHOLD=0.4
HIGH_CONFIDENCE_THRESHOLD=0.6
```

### Frontend (.env.local)
```bash
# NextAuth
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=generate-nextauth-secret

# Internal API
INTERNAL_API_KEY=same-as-backend-key
NEXT_PUBLIC_API_URL=http://localhost:8000
FASTAPI_INTERNAL_URL=http://backend:8000
```

---

## 📝 Próximos Passos Imediatos

1. **Criar endpoints internos do FastAPI**
   - Começar com `/internal/auth/register`
   - Depois `/internal/photos/process`

2. **Testar fluxo completo de registro**
   - Upload de face
   - Detecção
   - Busca de unclaimed
   - Criação de usuário

3. **Criar projeto Next.js**
   - Setup básico
   - NextAuth configurado
   - Primeira API route funcionando

4. **Integração**
   - Next.js chama FastAPI via API routes
   - Testar autenticação end-to-end

---

## 🎯 MVP Features (Ordem de Implementação)

### Sprint 1: Autenticação Base (1-2 dias)
- [x] Models e schemas
- [x] Auth security
- [ ] Endpoints internos de auth
- [ ] Next.js com NextAuth
- [ ] Login/Register básico

### Sprint 2: Upload com Reconhecimento (2-3 dias)
- [ ] Endpoint de upload com auto-associação
- [ ] Face matching service funcionando
- [ ] UI de upload no Next.js
- [ ] Preview de faces detectadas

### Sprint 3: Unclaimed Matches (2 dias)
- [ ] Busca de unclaimed no registro
- [ ] UI de claim flow
- [ ] Email notifications
- [ ] Dashboard com fotos do usuário

### Sprint 4: Features Avançadas (3-4 dias)
- [ ] Multi-face detection e tagging
- [ ] Email invitations
- [ ] Person management
- [ ] Photo privacy controls

### Sprint 5: Polish & Deploy (2-3 dias)
- [ ] Error handling
- [ ] Loading states
- [ ] Responsive design
- [ ] Docker setup
- [ ] Deploy pipeline

---

## 📚 Documentação a Criar

- [ ] API documentation (OpenAPI/Swagger)
- [ ] Architecture diagram
- [ ] Database schema diagram
- [ ] Authentication flow diagram
- [ ] Deployment guide
- [ ] Developer setup guide
- [ ] User manual

---

**Status Atual:** Backend 40% completo, Frontend 0%
**Próximo:** Criar endpoints internos do FastAPI

Continuar? 🚀
