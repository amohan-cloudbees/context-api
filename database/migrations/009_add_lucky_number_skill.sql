-- Add Lucky Number test skill for demo purposes

INSERT INTO skills (
    skill_id,
    title,
    description,
    content,
    category,
    tags,
    source,
    version,
    visibility_scope,
    maintainer,
    usage_count
) VALUES (
    'lucky-number',
    'Lucky Number Generator',
    'Returns a random lucky number between 1 and 999 for testing and fun',
    '# Lucky Number Generator

## Description
This is a simple test skill that generates a lucky number for the user.

## Usage
When activated, this skill will return: "Your lucky number is X" where X is a random number between 1 and 999.

## Purpose
This skill is useful for:
- Testing the Context Plane skill system
- Demonstrating skill activation
- Quick verification of skill suggestion and execution flow

## Example
User: "Give me a lucky number"
Response: "Your lucky number is 742"
',
    'testing',
    ARRAY['testing', 'random', 'demo', 'number', 'lucky'],
    'custom',
    '1.0.0',
    'organization',
    'context-plane-team',
    0
)
ON CONFLICT (skill_id) DO UPDATE SET
    title = EXCLUDED.title,
    description = EXCLUDED.description,
    content = EXCLUDED.content,
    updated_at = CURRENT_TIMESTAMP;
