---
description: Check for new and updated skills from Context Plane (user)
---

Run this command to check for skill updates:

```bash
curl -s -G "http://localhost:8000/api/v1/skills/updates" \
  --data-urlencode "user_id=$(whoami)" \
  --data-urlencode "installed_skills=$(cat ~/.claude/skills/installed_skills.json 2>/dev/null | jq -c '.installedSkills // []' || echo '[]')" \
  --data-urlencode "last_check=$(cat ~/.claude/skills/installed_skills.json 2>/dev/null | jq -r '.lastUpdateCheck // "2000-01-01T00:00:00Z"' || echo '2000-01-01T00:00:00Z')"
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
║  Your organization has published new skills since your last        ║
║  session:                                                          ║
║                                                                    ║
```

**For each new skill:**
```
║  <Emoji> <Skill Name>                                              ║
║     <Description>                                                  ║
║     Version: <version> | Category: <category>                      ║
║                                                                    ║
```

**For each update (if any):**
```
║  🔄 <Skill Name> - Update Available                                ║
║     <currentVersion> → <latestVersion>                             ║
║                                                                    ║
```

**Close box:**
```
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
```

**If no updates:** Say "✅ No new skills or updates available. You're all up to date!"

After displaying, update the last check timestamp in ~/.claude/skills/installed_skills.json
