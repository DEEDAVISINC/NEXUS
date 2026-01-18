# NEXUS QUICK REFERENCE CARD

## 🔑 CRITICAL INFO

### **Airtable Base**
- **ID:** `appaJZqKVUn3yJ7ma`
- **Name:** NEXUS Command Center
- **Tables:** 57 (all ALL CAPS with SPACES)
- **URL:** https://airtable.com/appaJZqKVUn3yJ7ma

### **Table Naming Convention**
✅ `VERTEX INVOICES` (ALL CAPS, SPACES)  
✅ `GRANT OPPORTUNITIES` (ALL CAPS, SPACES)  
✅ `ATLAS PROJECTS` (ALL CAPS, SPACES)  
❌ `Vertex Invoices` (Wrong - mixed case)  
❌ `VERTEX_INVOICES` (Wrong - underscores)

### **Start Backend**
```bash
cd "/Users/deedavis/NEXUS BACKEND"
PORT=8000 python3 api_server.py
```

### **Start Frontend**
```bash
cd "/Users/deedavis/NEXUS BACKEND/nexus-frontend"
npm start
```

### **Health Check**
```bash
curl http://127.0.0.1:8000/health
```

### **Video Demo**
Watch the NEXUS platform demonstration:
- **Local:** `http://127.0.0.1:8000/media/videos/nexus-2.mp4`
- **Showcase Page:** Open `NEXUS_DEMO_SHOWCASE.html` in browser
- **API Endpoint:** `GET /media/videos/nexus-2.mp4`

List all available videos:
```bash
curl http://127.0.0.1:8000/media/videos
```

### **Legal Documents**
Access Terms of Use and Privacy Policy:
- **Terms of Use:** `http://127.0.0.1:8000/legal/terms`
- **Privacy Policy:** `http://127.0.0.1:8000/legal/privacy`
- **List all:** `http://127.0.0.1:8000/legal`

---

## 📊 SYSTEM MAP

| System | Tables | Status | Purpose |
|--------|--------|--------|---------|
| **VERTEX** | 7 | ✅ Ready | Financial hub (invoices, expenses, revenue) |
| **GBIS** | 6 | ✅ Ready | Grant acquisition & tracking |
| **GPSS** | 13 | ✅ Ready | Government contract sales |
| **ATLAS PM** | 6 | ✅ Ready | Project management |
| **DDCSS/COMPASS** | 6 | ✅ Ready | Corporate sales system |
| **LBPC** | Various | ✅ Ready | Surplus recovery |

---

## 🎯 NEXT WEEK CHECKLIST

### Day 1: Setup
- [ ] Upgrade Airtable to Team ($20/month)
- [ ] Set up 10 GBIS automations
- [ ] Set up cross-system automations

### Day 2-3: Testing
- [ ] Test full automation workflow
- [ ] Test frontend dashboards
- [ ] Verify AI agents working

---

## 🤖 AI PERSONA: ALEXIS

All automated calls, emails, and voicemails come from "Alexis"

---

## 📁 KEY FILES

- `NEXUS_SYSTEM_STATUS_JAN_2026.md` - Complete system documentation
- `VERTEX_FINANCIAL_SYSTEM_ARCHITECTURE.md` - VERTEX design
- `VERTEX_AIRTABLE_SCHEMA.md` - VERTEX table specs
- `api_server.py` - Backend API server
- `nexus_backend.py` - AI agents & Airtable client
- `.env` - API keys and secrets

---

## 💰 COSTS

**Current:** ~$5/month (Anthropic API only)  
**Next Week:** ~$35-40/month (+ Airtable Team)  
**Production:** ~$50-100/month (+ Render + Bland.ai)

---

## 🔐 CREDENTIALS LOCATION

All API keys in `.env` file:
- `ANTHROPIC_API_KEY`
- `AIRTABLE_API_KEY`
- `AIRTABLE_BASE_ID`

---

## 🏆 DEE DAVIS INC

**Positioning:** "The Professionals' Professionals"  
**Certifications:** EDWOSB/WOSB/WBE/MBE  
**CAGE Code:** 8UMX3  
**Divisions:** 9 official + multiple sub-brands

---

**Current Status:** 🟢 READY FOR AUTOMATION SETUP  
**Last Updated:** January 18, 2026
