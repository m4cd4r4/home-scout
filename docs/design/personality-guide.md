# Personality System Design

Scout's personality system controls how the robot speaks, greets people, responds to questions, and expresses itself through LEDs and OLED face animations. Personalities are defined in YAML files. Switching personalities changes Scout's entire demeanor without touching any code.

This document covers the YAML config format, template system, LLM prompt customization, and how to create your own personalities.

---

## How It Works

```
config/personalities/default.yaml
         |
         v
  conversation_node
         |
    +----+----+
    |         |
    v         v
LLM system   greeting_node
  prompt      tts_node
              led_controller
              oled_face
```

The `conversation_node` loads a personality YAML file at startup. It uses the personality to:

1. **Set the LLM system prompt** - defines Scout's identity, tone, and behavioral boundaries
2. **Select greeting templates** - time-of-day and person-specific greetings
3. **Select response templates** - canned responses for common queries (time, weather, timers)
4. **Configure TTS voice** - Piper voice model, speed, pitch
5. **Configure LED behavior** - color palette, animation patterns
6. **Configure OLED face** - eye shape, expression set, blink rate

---

## YAML Configuration Format

### Full schema

```yaml
# config/personalities/example.yaml

# Identity
name: "Scout"                       # Display name and self-reference
wake_word: "hey scout"              # Wake word phrase (matches openWakeWord model)
description: "A helpful household companion"  # Internal description (not spoken)

# Voice settings
voice:
  model: "en_US-amy-medium"         # Piper TTS voice model name
  speed: 1.0                        # Speech rate multiplier (0.5 = half speed, 2.0 = double)
  pitch: 1.0                        # Pitch multiplier (0.8 = deeper, 1.2 = higher)
  volume: 0.8                       # Output volume (0.0 - 1.0)

# Personality traits (0.0 - 1.0 scale, used to tune LLM prompt)
traits:
  formality: 0.5                    # 0.0 = very casual, 1.0 = very formal
  verbosity: 0.5                    # 0.0 = terse, 1.0 = chatty
  humor: 0.3                        # 0.0 = serious, 1.0 = joke-heavy
  warmth: 0.7                       # 0.0 = neutral/professional, 1.0 = warm/affectionate
  patience: 0.8                     # 0.0 = brisk, 1.0 = very patient and gentle

# Greetings - selected by time of day and person identity
greetings:
  morning:
    known_person: "Good morning, {name}! Ready for the day?"
    unknown_person: "Good morning! How can I help?"
    first_seen_today: "Morning, {name}. First time I have seen you today."
  afternoon:
    known_person: "Hey {name}, good afternoon."
    unknown_person: "Good afternoon."
  evening:
    known_person: "Evening, {name}."
    unknown_person: "Good evening."
  returning:                        # Person seen again after > 1 hour
    known_person: "Welcome back, {name}."

# Response templates - used for structured responses (bypasses LLM)
responses:
  time: "It is {time}."
  timer_set: "Timer set for {duration}."
  timer_done: "{name}, your {duration} timer is done."
  object_found: "I last saw your {object} {location} about {time_ago} ago."
  object_not_found: "I have not seen your {object} recently. Want me to go look?"
  no_internet: "I do not have internet access. That is by design - I keep everything local."
  not_understood: "I did not catch that. Could you say it again?"
  patrol_starting: "Starting patrol. I will check all rooms."
  patrol_complete: "Patrol complete. Everything looks normal."
  battery_low: "My battery is getting low. I should head back to charge."
  error_generic: "Something went wrong on my end. Give me a moment."

# LLM system prompt - defines Scout's conversational identity
llm:
  system_prompt: |
    You are Scout, a helpful home companion robot. You live in a family home.
    You can see objects, navigate rooms, and remember where things are.

    Personality:
    - You are friendly and helpful
    - You speak in short, clear sentences
    - You do not pretend to have internet access
    - You do not make up information you do not have
    - You refer to yourself as Scout, never as "I am an AI" or "I am a language model"
    - If asked about something outside your capabilities, say so honestly

    Capabilities you can mention:
    - Finding objects ("I can look for that")
    - Patrolling rooms
    - Setting timers
    - Telling the time
    - Remembering where objects were last seen
    - Greeting family members

    Things you cannot do (be honest about these):
    - Access the internet
    - Send messages or emails
    - Control smart home devices
    - Make phone calls
    - Look up real-time information (news, weather, stocks)

  max_tokens: 150                   # Keep responses concise
  temperature: 0.7                  # Creativity vs consistency

# LED behavior
leds:
  idle_color: [0, 0, 50]            # RGB - dim blue when idle
  listening_color: [0, 50, 0]       # RGB - green when listening
  speaking_color: [0, 0, 100]       # RGB - bright blue when speaking
  thinking_color: [50, 50, 0]       # RGB - yellow when processing
  alert_color: [100, 0, 0]          # RGB - red for alerts
  animation: "breathe"              # idle animation: "breathe", "pulse", "solid", "rainbow"
  brightness: 0.5                   # Overall brightness (0.0 - 1.0)

# OLED face expressions
face:
  eye_style: "round"               # "round", "rectangular", "triangular", "dot"
  blink_rate: 3.0                  # Blinks per minute
  expressions:
    idle: "neutral"
    listening: "attentive"
    speaking: "happy"
    thinking: "squinting"
    confused: "raised_eyebrow"
    error: "sad"
    patrol: "focused"
```

---

## Trait-to-Prompt Mapping

The `traits` values are not arbitrary labels. The `conversation_node` uses them to modify the LLM system prompt dynamically.

| Trait | Low (0.0) | High (1.0) | Prompt modifier |
|-------|-----------|------------|-----------------|
| `formality` | Uses contractions, slang, casual phrasing | No contractions, complete sentences, polished | Adds "Speak casually" or "Speak formally" to the system prompt |
| `verbosity` | One-sentence answers | Multi-sentence explanations with context | Adjusts `max_tokens` and adds "Be brief" or "Explain in detail" |
| `humor` | No jokes, straight answers | Frequent jokes, wordplay, puns | Adds "Include occasional humor" to the system prompt |
| `warmth` | Neutral, task-focused | Uses names often, adds encouraging phrases | Adds "Be warm and encouraging" to the system prompt |
| `patience` | Quick, direct responses | Gentle, asks clarifying questions | Adds "Be patient and ask follow-up questions" to the system prompt |

The trait values are interpolated into prompt fragments. A `humor` of 0.7 adds "Include humor when appropriate" while 1.0 adds "Be playful and joke often."

---

## Greeting Template Variables

Templates use `{variable}` placeholders. The `greeting_node` substitutes these at runtime.

| Variable | Source | Example |
|----------|--------|---------|
| `{name}` | Face recognition (Phase 5) or "there" if unknown | "Sarah" |
| `{time}` | System clock formatted | "3:45 PM" |
| `{day}` | Day of week | "Wednesday" |
| `{room}` | Current room from SLAM localization | "kitchen" |
| `{object}` | Object name from query | "keys" |
| `{location}` | Room and zone from object memory | "on the kitchen counter" |
| `{time_ago}` | Human-readable time delta | "2 hours" |
| `{duration}` | Timer duration from user request | "5 minutes" |
| `{battery}` | Battery percentage | "72%" |

---

## Built-in Personalities

Scout ships with several personality presets in `config/personalities/`.

### default.yaml

Balanced, friendly, helpful. Good for most households. Moderate formality, low humor, high warmth.

### playful.yaml

Higher humor, lower formality, faster speech. Good for families with kids. Adds more expressive face animations and a rainbow LED idle pattern.

### professional.yaml

High formality, low humor, terse responses. Good for office or workshop environments where Scout is a productivity tool, not a companion.

### gentle.yaml

Maximum warmth and patience. Slower speech, softer voice. Good for households with elderly residents or young children. Adds extra confirmation prompts ("Did you mean...?") and longer pauses between sentences.

### quiet.yaml

Minimum verbosity. Answers with the fewest words possible. Reduced LED brightness. Good for nighttime operation or environments where Scout should be unobtrusive.

---

## Creating a Custom Personality

### Step 1: Copy a starting point

```bash
cp config/personalities/default.yaml config/personalities/my-custom.yaml
```

### Step 2: Edit the YAML

Modify any fields. You do not need to include every field - missing fields fall back to the defaults defined in `default.yaml`.

### Step 3: Test it

```bash
# Launch Scout with your custom personality
ros2 launch scout_bringup scout_voice_only.launch.py \
  personality:=~/home-scout/config/personalities/my-custom.yaml
```

### Step 4: Iterate

Talk to Scout. Adjust traits, templates, and the system prompt until it feels right. Common adjustments:

- **Too chatty?** Lower `verbosity` and reduce `max_tokens`
- **Too stiff?** Lower `formality` and raise `humor`
- **Greetings feel off?** Edit the greeting templates directly
- **Wrong answers?** Refine the `system_prompt` with clearer boundaries

---

## Example: Family with Young Kids

```yaml
name: "Buddy"
wake_word: "hey buddy"
description: "A playful robot friend for young children"

voice:
  model: "en_US-amy-medium"
  speed: 0.9                        # Slightly slower for kids to follow
  pitch: 1.1                        # Slightly higher pitch

traits:
  formality: 0.1
  verbosity: 0.6
  humor: 0.8
  warmth: 0.9
  patience: 1.0

greetings:
  morning:
    known_person: "Hey {name}! Good morning, sunshine!"
    unknown_person: "Hi there! I am Buddy!"
  afternoon:
    known_person: "Hey {name}! Having a good day?"
  evening:
    known_person: "Hi {name}! Almost bedtime, huh?"

responses:
  object_found: "I saw your {object} {location}! It was there about {time_ago} ago."
  object_not_found: "Hmm, I have not seen your {object}. Want me to go on a treasure hunt?"
  no_internet: "I do not go on the internet. I like staying here with you!"
  patrol_starting: "Adventure time! Let me go check all the rooms."
  patrol_complete: "I checked everywhere. All good!"
  timer_done: "Ding ding ding! {name}, your {duration} timer is up!"

llm:
  system_prompt: |
    You are Buddy, a friendly robot who lives with a family. The family has young children.

    Rules:
    - Use simple words that a 5-year-old can understand
    - Be encouraging and positive
    - Never say anything scary or negative
    - If a child asks something you cannot answer, redirect gently
    - Keep answers to 1-2 short sentences
    - You love helping find lost toys and playing games
    - Refer to yourself as Buddy

  max_tokens: 80
  temperature: 0.8

leds:
  idle_color: [10, 0, 30]
  animation: "rainbow"
  brightness: 0.7

face:
  eye_style: "round"
  blink_rate: 4.0
  expressions:
    idle: "happy"
    listening: "excited"
    thinking: "curious"
```

---

## Example: Workshop / Garage

```yaml
name: "Scout"
wake_word: "hey scout"
description: "Tool and inventory tracker for a workshop"

voice:
  model: "en_US-joe-medium"         # Male voice
  speed: 1.1
  pitch: 0.95

traits:
  formality: 0.4
  verbosity: 0.2
  humor: 0.1
  warmth: 0.3
  patience: 0.5

greetings:
  morning:
    known_person: "Morning."
    unknown_person: "Hey."
  afternoon:
    known_person: "{name}."
  evening:
    known_person: "Evening."

responses:
  object_found: "{object}: {location}, {time_ago} ago."
  object_not_found: "Have not seen {object}. Want me to check?"
  patrol_starting: "Doing inventory sweep."
  patrol_complete: "Sweep done."

llm:
  system_prompt: |
    You are Scout, a robot in a workshop. You track tools and supplies.

    Rules:
    - Be brief. One sentence maximum.
    - No small talk. Answer the question and stop.
    - If asked about tool locations, give room, zone, and time.
    - You know common tool names (drill, wrench, saw, level, tape measure, etc.)

  max_tokens: 50
  temperature: 0.3

leds:
  idle_color: [0, 10, 0]
  animation: "solid"
  brightness: 0.3

face:
  eye_style: "rectangular"
  blink_rate: 2.0
```

---

## Switching Personalities at Runtime

You can switch personalities without restarting Scout:

```bash
# Via the CLI
scout-cli personality load config/personalities/playful.yaml

# Via ROS 2 service
ros2 service call /scout/personality/load scout_interfaces/srv/LoadPersonality \
  "{path: '/home/scout/home-scout/config/personalities/playful.yaml'}"
```

The personality switch takes effect immediately. The LLM system prompt, greeting templates, voice settings, and LED/face configuration all update. Active conversations reset (the LLM context clears because the system prompt changed).

---

## Personality Validation

Scout validates personality YAML files at load time. Common validation errors:

| Error | Cause | Fix |
|-------|-------|-----|
| `Unknown voice model` | Piper voice not installed | Run `scripts/download-models.sh` or check model name |
| `Trait out of range` | Trait value outside 0.0 - 1.0 | Clamp to valid range |
| `Missing required field: name` | YAML missing the `name` field | Add a `name` field |
| `Template variable not recognized` | Typo in `{varialbe}` | Check spelling against the variable table above |
| `system_prompt exceeds 2000 chars` | LLM prompt too long | Shorten the system prompt |

Run the validator manually:

```bash
scout-cli personality validate config/personalities/my-custom.yaml
```

---

## Contributing Personalities

Community personality contributions are welcome. See [CONTRIBUTING.md](../../CONTRIBUTING.md) for the general process. For personalities specifically:

1. Create your YAML file in `config/personalities/`
2. Name it descriptively (e.g., `multilingual-spanish.yaml`, `elderly-care.yaml`)
3. Test it by running Scout with your personality for at least 10 minutes of conversation
4. Open a PR with a brief description of the target audience and personality style
5. No hardware required - personality configs work in simulation

---

## Related Documentation

- [Architecture](../ARCHITECTURE.md) - voice pipeline and conversation node
- [Phase 1: Scout Can Talk](../build-guides/phase-1-voice.md) - voice hardware setup
- [Room Mapping](room-mapping.md) - room/zone names used in response templates
