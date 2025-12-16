# American Dream

**Author:** Madi Tattybay
**Course:** CS50’s Introduction to Computer Science

---

## Description
**American Dream** is a simple life simulation game about **legal immigration** and adaptation in the U.S.
You start as a new immigrant, learning English, getting your SSN and driver’s license, working small jobs, managing energy and mood, and slowly building a new life.

---

## Goal
Survive and grow through **7 phases** (each representing about 2 months) by balancing your stats:

- 💵 **Money**
- 🗣 **English**
- ⚡ **Energy**
- 🙂 **Mood**

Reach solid progress in all stats to achieve **Success**, or fall into **Pause (burnout)** if your energy or mood drop too low.

---

## Gameplay Logic
Each phase = 2 months of real-life progress.
Choices impact your stats:
- Study English → 🗣 English ↑, ⚡ Energy ↓
- Work → 💵 Money ↑, ⚡ Energy ↓, 🙂 Mood ↓
- Rest → ⚡ Energy ↑, 🙂 Mood ↑
- Community / Partner → 🙂 Mood ↑, 🗣 English ↑

If you burn out → screen “Pause” appears with message:
> "You are exhausted. Rest and come back stronger."

After several days (rest), your energy restores and you can continue your journey.

---

## Video Demo

link:
https://youtu.be/JddTQ0zaDNI


---

## Future Improvements

Add sound effects and animations for better immersion.
Expand storyline to include months or years instead of only 7 steps.
Add difficulty levels (different starting conditions — with/without savings).
Implement multi-user mode to save multiple players’ progress.
Add “Green Card Journey” and “Citizenship Stage” as advanced phases.

---

## Reflection

This project represents the journey of legal immigrants who work hard to build a better life.
As an immigrant myself, I truly understand how challenging it is to start over in a new country — to learn the language, adapt to a new culture, and rebuild everything from zero.
My goal with American Dream was to create something that could inspire and support people who are walking the same path — to remind them that every small step matters: one class, one shift, one new word.
It’s inspired by real experiences — where energy, hope, and persistence matter more than luck.
Every small progress brings you closer to the American Dream.

---

## Tech Stack
- **Flask** (Python backend)
- **SQLite3** (for player stats storage)
- **HTML / CSS / Jinja2** (templating and UI)
- **Bootstrap 5** (styling and layout)

---

## How to Run

```bash

sqlite3 american_dream.db < schema.sql
flask --app app run --debug
