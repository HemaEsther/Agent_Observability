# Agent Observability with OpenTelemetry

A simple Python AI agent instrumented with **OpenTelemetry** to understand how observability and traceability work in AI agents.

The agent uses the Google Gemini API and has two tools:

* Calculator
* Current date/time

The project is intentionally small and focuses on understanding the fundamentals of **AI agent observability**.

---

## Project Overview

The agent follows this basic flow:

```text
User Query
    ↓
Agent Run
    ↓
Gemini LLM
    ↓
Tool Selection
    ↓
Tool Execution
    ↓
Tool Result
    ↓
Gemini LLM
    ↓
Final Response
```

OpenTelemetry records the important operations as **traces and spans**.

---

## Technologies Used

* Python
* Google Gemini API
* Google GenAI SDK
* OpenTelemetry
* OpenTelemetry SDK
* python-dotenv

---

## Project Structure

```text
agent-observability/
│
├── agent.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env
│
└── .venv/
```

> `.env` and `.venv` should not be pushed to GitHub.

---

# Features

## 1. Calculator Tool

The agent can perform mathematical calculations.

Example:

```text
User:
What is 25% of 840?

Tool requested:
calculator

Arguments:
{'expression': '0.25 * 840'}

Tool result:
210
```

The final response can be:

```text
25% of 840 is 210.

Calculation:
840 × 0.25 = 210
```

---

## 2. Current Date/Time Tool

The agent can return the current local date and time.

Example:

```text
User:
What is the current time?

Tool:
get_time
```

---

# OpenTelemetry

OpenTelemetry is used to observe what happens inside the agent.

The current trace structure is:

```text
agent_run
│
├── gemini_call
│
└── tool_execution
```

When the agent needs a tool, the flow can look like:

```text
agent_run
│
├── gemini_call
│
├── tool_execution
│
└── gemini_call
```

The first Gemini call decides that a tool is required.

The tool executes.

The second Gemini call uses the tool result to generate the final response.

---

# OpenTelemetry Concepts

## Trace

A **trace** represents the complete journey of one user request.

Example:

```text
"What is 25% of 840?"
        ↓
    agent_run
        ↓
    Gemini
        ↓
   Calculator
        ↓
    Gemini
        ↓
 Final Response
```

All of these operations can belong to the same trace.

---

## Span

A **span** represents one individual operation.

This project contains spans such as:

```text
agent_run
gemini_call
tool_execution
```

For example:

```text
agent_run
    └── gemini_call
```

The `gemini_call` span is a child of the `agent_run` span.

---

## Trace ID

The **Trace ID** identifies the complete request.

Example:

```text
trace_id:
0x1a75d0467c08274680d14df018591204
```

Multiple spans with the same Trace ID belong to the same request.

---

## Span ID

The **Span ID** identifies one specific operation.

Example:

```text
span_id:
0x750e9d874007e9a2
```

---

## Parent ID

The Parent ID tells us which span contains the current operation.

Example:

```text
agent_run
    │
    └── gemini_call
```

The `gemini_call` span has the `agent_run` span as its parent.

---

# Attributes

Attributes are additional information attached to a span.

### Agent attributes

```text
user.query
agent.duration_ms
```

Example:

```text
user.query:
"What is 25% of 840?"
```

### Gemini attributes

```text
llm.model
llm.duration_ms
```

Example:

```text
llm.model:
gemini-3.8-flash
```

### Tool attributes

```text
tool.name
tool.arguments
tool.result
tool.duration_ms
calculator.expression
```

These attributes help us understand what happened during each operation.

---

# Latency Tracking

The project measures how long different operations take.

## Agent latency

```text
agent.duration_ms
```

This represents the total time taken by the agent request.

## Gemini latency

```text
llm.duration_ms
```

This represents the time taken by a Gemini API call.

## Tool latency

```text
tool.duration_ms
```

This represents the time taken by a tool such as the calculator.

Example:

```text
agent_run
    agent.duration_ms = 5882 ms

gemini_call
    llm.duration_ms = 5851 ms

tool_execution
    tool.duration_ms = 0.2 ms
```

This helps identify which part of the agent is taking the most time.

---

# Events

OpenTelemetry can also record events that happen during a span.

For example, an exception can be recorded as an event.

The project can therefore help identify where an API or tool failure occurred.

---

# Error Observability

The Gemini API can sometimes return errors such as:

```text
503 UNAVAILABLE
```

When this happens, OpenTelemetry can show the failure inside the Gemini span.

Example:

```text
agent_run
    │
    └── gemini_call
           │
           ├── status: ERROR
           ├── llm.model
           ├── llm.duration_ms
           └── exception
```

This is useful because the trace shows **where the failure occurred**.

For example, in one run Gemini returned a 503 error after approximately 5.85 seconds, and the trace captured the error and exception information.

---

# Observability vs Traceability

## Observability

Observability helps us understand the **overall behavior of a system**.

Examples:

```text
Latency
Errors
Tool execution
LLM calls
Request information
```

## Traceability

Traceability helps us follow **one specific request** through the system.

Example:

```text
Trace ID
   ↓
agent_run
   ↓
gemini_call
   ↓
tool_execution
   ↓
gemini_call
   ↓
final response
```

Simple way to remember:

> **Observability = What is happening in my system?**

> **Traceability = What happened to this particular request?**

---

# Environment Variables

The Gemini API key is stored in a `.env` file.

Example:

```text
GEMINI_API_KEY=your_api_key_here
```

The application loads it using:

```python
from dotenv import load_dotenv

load_dotenv()
```

The API key should **never be committed to GitHub**.

---

# `.gitignore`

The project uses `.gitignore` to prevent sensitive and unnecessary files from being committed.

```text
.env
.venv/
__pycache__/
.ipynb_checkpoints/
```

---

# Running the Project

## 1. Create virtual environment

```bash
python -m venv .venv
```

## 2. Activate it on Windows

```bash
.venv\Scripts\activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Create `.env`

```text
GEMINI_API_KEY=your_api_key_here
```

## 5. Run the agent

```bash
python agent.py
```

Example:

```text
Enter your question: What is 25% of 840?
```

---

# Example Output

A successful calculator run:

```text
Tool requested: Calculator
Arguments: {'expression': '0.25 * 840'}
Tool result: Calculator

Agent:
25% of 840 is **210**.

(Calculation: $840 \times 0.25 = 210$, or $840 \div 4 = 210$)
```

The OpenTelemetry `agent_run` span for this request:

```json
{
    "name": "agent_run",
    "context": {
        "trace_id": "0xc91f08c36421d45bbafea8616b8797a1",
        "span_id": "0x3a07dc2f1575ebe5",
        "trace_state": "[]"
    },
    "kind": "SpanKind.INTERNAL",
    "parent_id": null,
    "start_time": "2026-09-30T07:06:11.389423Z",
    "end_time": "2026-09-30T07:06:24.036912Z",
    "status": {
        "status_code": "UNSET"
    },
    "attributes": {
        "user.query": "What is 25% of 840?"
    },
    "events": [],
    "links": [],
    "resource": {
        "attributes": {
            "telemetry.sdk.language": "python",
            "telemetry.sdk.name": "opentelemetry",
            "telemetry.sdk.version": "1.42.1",
            "service.name": "unknown_service"
        },
        "schema_url": ""
    }
}
```

Final response returned by the agent:

```text
25% of 840 is **210**.

(Calculation: $840 \times 0.25 = 210$, or $840 \div 4 = 210$)
```

This example represents the initial OpenTelemetry trace output before the later latency and service-name improvements were added.


---

# Current Architecture

```text
                 ┌─────────────────┐
                 │   User Query    │
                 └────────┬────────┘
                          ↓
                 ┌─────────────────┐
                 │   agent_run     │
                 └────────┬────────┘
                          ↓
                 ┌─────────────────┐
                 │  gemini_call    │
                 └────────┬────────┘
                          ↓
                  Tool required?
                    /          \
                  No            Yes
                  ↓              ↓
             Final answer   tool_execution
                                  ↓
                             Tool result
                                  ↓
                           gemini_call
                                  ↓
                            Final answer
```

---

# Current Learning Scope

This project currently demonstrates:

* AI agent basics
* Tool calling
* OpenTelemetry setup
* Traces
* Spans
* Parent-child spans
* Trace IDs
* Span IDs
* Attributes
* Events
* Error visibility
* Agent latency
* LLM latency
* Tool latency
* Environment variable management

---

# Future Improvements

The following are intentionally left for future learning:

1. **Export traces to an observability UI**

   * Jaeger
   * Arize Phoenix
   * Other OpenTelemetry-compatible platforms

2. **Visualize traces**

   * View the complete agent execution visually
   * Inspect individual spans

3. **LLM token usage**

   * Track input tokens
   * Track output tokens
   * Track total tokens

---

# Learning Goal

The main goal of this project is to understand how to observe an AI agent.

The learning path is:

```text
Python Agent
     ↓
Tool Calling
     ↓
OpenTelemetry
     ↓
Traces
     ↓
Spans
     ↓
Attributes
     ↓
Errors
     ↓
Latency
     ↓
Observability UI
     ↓
Advanced AI Observability
```

The project starts with a small calculator/time agent so that the OpenTelemetry concepts can be understood before applying them to larger systems such as RAG and multi-agent applications.

---

# Security Note

For this learning project, the calculator uses Python's `eval()` function.

This is acceptable only as a simple learning demonstration.

Do **not** use unrestricted `eval()` with arbitrary user input in a production application because it can execute unsafe Python expressions.
