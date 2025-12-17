---
description: Get skill suggestions from Context Plane based on your task
---

Ask the user what task they want to accomplish if they haven't already specified it.

Once you have the task description, run this command to get skill suggestions:

```bash
curl -s -X POST "http://localhost:8000/api/v1/skills/suggest" \
  -H "Content-Type: application/json" \
  -d "{\"userPrompt\":\"<TASK_DESCRIPTION>\",\"context\":{}}"
```

Replace `<TASK_DESCRIPTION>` with the user's actual task description.

Then present the suggestions to the user showing:
- Skill name and description
- Confidence score (as a percentage)
- Why this skill was suggested (the reasoning)
- Installation status (✅ Installed / ⚠️ Not installed)

If there are multiple suggestions, rank them by confidence score.

**For skills that are NOT installed (`installed: false`):**
- Inform the user the skill is not installed yet
- Ask if they'd like to use it using the AskUserQuestion tool
- If user confirms:
  1. **Install for future sessions:**
     ```bash
     curl -s -X POST "http://localhost:8000/api/v1/skills/<SKILL_ID>/install?user_id=$(whoami)"
     ```
  2. **Fetch and use in current session:**
     ```bash
     curl -s "http://localhost:8000/api/skills/<SKILL_ID>"
     ```
  3. Read the `content` field from the response
  4. Follow the skill instructions to complete the user's task immediately
  5. No session restart needed - execute the skill in the current session

**Important:** When a skill is not installed, always fetch it inline and execute it immediately. Don't tell the user to restart their session.

Make the output helpful and encouraging. Explain what each skill does and how it could help with their task.
