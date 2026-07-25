# AIDA — Artificial Intelligence Droid Assistant

A personal AI assistant for daily support and journaling, designed to prompt back when something needs attention rather than only responding when asked.

AIDA holds conversations, calls tools, retrieves personal knowledge, stores memories, and queries structured data.

## Features

- Conversational interface — completed
- Tool calling — completed
- Personal memory retrieval — completed
- Database querying and record creation — in progress
- Scheduling, reminders, and calendar tasks — in progress
- Layered L1–L4 memory system — in progress
- Voice interface — planned

## Architecture

Multi-agent:

- **AIDA** — the conversation agent. Handles input and output, and runs a tool loop for retrieval, database access, and scheduling. *Completed.*
- **Memory Agent** — runs in the background. Writes memory entries from completed interactions and consolidates raw material into higher memory layers, independently of the conversation. *In progress.*
- **Perspective Agent** — a perception layer. Takes continuous input from screen and camera, and writes only what matters into L4. Most of what it sees is discarded; the point is to decide what is worth keeping, not to record everything. *Planned.*

The perspective agent is the subconscious counterpart to the conversation agent: it runs whether or not anyone is talking to AIDA, and surfaces only the salient.

## Memory

| Layer | Content |
|---|---|
| L1 | Manually verified personal knowledge |
| L2 | Consolidated patterns and inferred knowledge |
| L3 | Structured events and facts |
| L4 | Raw conversations, observations, documents |

L2 and L3 are produced by the memory agent, reading downward — L3 extracts discrete events from L4, L2 infers patterns from L3.

## Stack

- **Language:** Python
- **Database:** SQLite
- **AI API:** OpenAI
- **Validation:** Pydantic
- **Configuration:** python-dotenv

## Status

Experimental personal project under active development.
