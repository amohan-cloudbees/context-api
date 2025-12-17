---
description: Browse all available skills in Context Plane (user)
---

Run this command to check for new skills you don't have yet:

```bash
curl -s -G "http://localhost:8000/api/v1/skills/updates" \
  --data-urlencode "user_id=$(whoami)" \
  --data-urlencode "installed_skills=$(cat ~/.claude/skills/installed_skills.json 2>/dev/null | jq -c '.installedSkills // []' || echo '[]')" \
  --data-urlencode "last_check=2000-01-01T00:00:00Z"
```

Then display following the Context Plane Pre-Hook specification format:

**Display in formatted box:**
```
╔════════════════════════════════════════════════════════════════════╗
║  Unify AI - Context Plane                                          ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  🎯 New Skills Available (<count>)                                 ║
║                                                                    ║
║  Your organization has published new skills:                       ║
║                                                                    ║
```

**For each new skill:**
```
║  🔒 <Category Emoji> <Skill Name>                                  ║
║     <Description truncated to fit>                                 ║
║     Version: <version> | Category: <category>                      ║
║                                                                    ║
```

**Category emojis:**
- 🔒 Security - security
- 🌐 API - api, documentation
- 📋 Documentation - documentation
- 🧪 Testing - testing
- 🎨 Design - design, frontend
- 📊 Analytics - file-processing, analytics
- 💬 Communication - communication
- ⚙️ General - general

**Close box:**
```
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
```

**If no new skills:** Say "No new skills available. All organizational skills are already known."

If the API returns an error, check if the Context Plane server is running at http://localhost:8000
