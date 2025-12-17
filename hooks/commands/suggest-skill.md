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
- How they can use this skill

If there are multiple suggestions, rank them by confidence score.

Make the output helpful and encouraging. Explain what each skill does and how it could help with their task.
