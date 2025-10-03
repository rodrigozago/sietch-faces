# 🚀 QUICK START - Testing Complete Application

**Last Updated**: October 3, 2025  
**Status**: Ready for Testing!

---

## ⚡ Super Quick Start (5 minutes)

```bash
# 1. Start Core API (Terminal 1)
cd /mnt/c/PersonalWorkspace/sietch-faces
python -m uvicorn app.main_core:app --reload --port 8000

# 2. Start Frontend (Terminal 2)
cd /mnt/c/PersonalWorkspace/sietch-faces/frontend
npm run dev

# 3. Open Browser
open http://localhost:3000

# 4. Register & Test
# → Sign up with photo
# → Create album
# → Upload photos
# → Watch auto-association magic! ✨
```

---

## 🧪 3-User Test Scenario (Complete Flow)

### Part 1: Setup (5 min)

```bash
# Register 3 users via UI:
1. alice@example.com / Alice123!
2. bob@example.com / Bob123!
3. charlie@example.com / Charlie123!

# Each user uploads solo photo during registration
```

### Part 2: Test Auto-Association (2 min)

```bash
# Login as Alice
# Create album "Party Photos"
# Upload group photo with Alice + Bob + Charlie

# Expected Result:
✓ Photo appears in Alice's "Party Photos"
✓ Photo auto-added to Bob's "My Faces"
✓ Photo auto-added to Charlie's "My Faces"
```

### Part 3: Verify (1 min)

```bash
# Logout, login as Bob
# Go to "My Faces" album
# See 2 photos:
  1. Bob's solo (uploaded during registration)
  2. Group photo (auto-added) ← THE MAGIC!
```

---

## ✅ Health Checks

```bash
# Core API
curl http://localhost:8000/health
# → {"status":"ok"}

# Stats
curl http://localhost:8000/stats
# → Shows persons and faces count

# Frontend
curl -I http://localhost:3000
# → HTTP 200 OK
```

---

## 🎯 Key Features to Test

| Feature | How to Test | Expected |
|---------|-------------|----------|
| **Registration** | Sign up with photo | User created + auto-album exists |
| **Face Detection** | Upload photo | Shows "X faces detected" |
| **Auto-Association** | Upload group photo | Appears in all users' auto-albums |
| **Album Management** | Create/delete albums | Works smoothly |
| **Navigation** | Click all nav links | No errors |
| **Responsive** | Resize browser | Layout adapts |

---

## 🐛 Quick Troubleshooting

```bash
# Prisma errors?
cd frontend && npx prisma generate

# Module not found?
cd frontend && npm install

# Port in use?
lsof -i :3000 && kill -9 <PID>
lsof -i :8000 && kill -9 <PID>

# Database issues?
psql -U postgres
CREATE DATABASE sietch_core;
CREATE DATABASE sietch_bff;
```

---

## 📊 Check Results in Database

```bash
# BFF Database
psql -U sietch_user -d sietch_bff -c "
SELECT u.username, 
       COUNT(DISTINCT a.id) as albums,
       COUNT(DISTINCT ap.\"photoId\") as photos_in_albums
FROM \"User\" u
LEFT JOIN \"Album\" a ON a.\"ownerId\" = u.id
LEFT JOIN \"AlbumPhoto\" ap ON ap.\"albumId\" = a.id
GROUP BY u.id;"

# Core Database
psql -U sietch_user -d sietch_core -c "
SELECT p.name, COUNT(f.id) as faces
FROM persons p
LEFT JOIN faces f ON f.person_id = p.id
GROUP BY p.id;"
```

---

## 🎉 Success Checklist

```
[ ] Registered 3 users with photos
[ ] Each user has auto-album
[ ] Created personal albums
[ ] Uploaded solo photos
[ ] Uploaded group photo
[ ] Group photo auto-added to all users
[ ] Stats show correct numbers
[ ] Navigation works
[ ] No console errors
```

---

## 🚀 If Everything Works...

**Congratulations! You have a working:**
- ✅ Face detection system (RetinaFace)
- ✅ Face recognition system (ArcFace embeddings)
- ✅ Automatic photo organization
- ✅ Multi-user social features
- ✅ Beautiful responsive UI
- ✅ Microservices architecture

**Next Steps:**
1. Test with real photos
2. Test with many users
3. Performance testing
4. Deploy to production!

---

## 📸 Need Test Photos?

```bash
# Use during testing:
- Webcam capture (easiest)
- Phone camera photos
- Download from unsplash.com
- Use your own photos!

# Best practices:
✓ Clear frontal faces
✓ Good lighting
✓ Face > 100px size
✓ 1-5 people per photo
```

---

## 🎊 You're All Set!

**Start Testing Now:**
```bash
python -m uvicorn app.main_core:app --reload  # Terminal 1
cd frontend && npm run dev                      # Terminal 2
open http://localhost:3000                      # Browser
```

**Have fun! 🚀✨**
