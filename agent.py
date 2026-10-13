import os
import time
from datetime import datetime

from dotenv import load_dotenv

from google import genai
from google.genai import types

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)


# ============================================================
# Load environment variables
# ============================================================

load_dotenv()


# ============================================================
# OpenTelemetry setup
# ============================================================

provider = TracerProvider()

provider.add_span_processor(
    SimpleSpanProcessor(
        ConsoleSpanExporter()
    )
)

trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)


# ============================================================
# Gemini client
# ============================================================

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)


# ============================================================
# Tools
# ============================================================

def calculator(expression: str) -> float:
    """Perform a mathematical calculation."""
    return eval(expression)


def get_time() -> str:
    """Get the current local date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ============================================================
# Tool declarations
# ============================================================

calculator_declaration = types.FunctionDeclaration(
    name="calculator",
    description="Performs mathematical calculations.",
    parameters=types.Schema(
        type="OBJECT",
        properties={
            "expression": types.Schema(
                type="STRING",
                description="Mathematical expression to calculate.",
            )
        },
        required=["expression"],
    ),
)


get_time_declaration = types.FunctionDeclaration(
    name="get_time",
    description="Returns the current local date and time.",
    parameters=types.Schema(
        type="OBJECT",
        properties={},
    ),
)


tools = [
    types.Tool(
        function_declarations=[
            calculator_declaration,
            get_time_declaration,
        ]
    )
]


# ============================================================
# Tool execution
# ============================================================

def execute_tool(function_call):

    tool_name = function_call.name
    arguments = function_call.args or {}

    with tracer.start_as_current_span(
        "tool_execution"
    ) as span:

        # Start timer
        start_time = time.perf_counter()

        span.set_attribute(
            "tool.name",
            tool_name
        )

        span.set_attribute(
            "tool.arguments",
            str(arguments)
        )

        print(f"\n🔧 Tool requested: {tool_name}")
        print(f"📥 Arguments: {arguments}")

        if tool_name.lower() == "calculator":

            expression = arguments["expression"]

            span.set_attribute(
                "calculator.expression",
                expression
            )

            result = calculator(expression)

        elif tool_name.lower() == "get_time":

            result = get_time()

        else:

            span.set_attribute(
                "tool.error",
                True
            )

            result = f"Unknown tool: {tool_name}"

        span.set_attribute(
            "tool.result",
            str(result)
        )

        # Calculate tool latency
        duration_ms = (
            time.perf_counter() - start_time
        ) * 1000

        span.set_attribute(
            "tool.duration_ms",
            duration_ms
        )

        print(f"📤 Tool result: {result}")
        print(f"⏱️ Tool duration: {duration_ms:.2f} ms")

        return result


# ============================================================
# Agent
# ============================================================

def run_agent(user_query):

    with tracer.start_as_current_span(
        "agent_run"
    ) as agent_span:

        # Start agent timer
        agent_start_time = time.perf_counter()

        agent_span.set_attribute(
            "user.query",
            user_query
        )

        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part(text=user_query)
                ],
            )
        ]

        while True:

            # ------------------------------------------------
            # Gemini call
            # ------------------------------------------------

            with tracer.start_as_current_span(
                "gemini_call"
            ) as llm_span:

                # Start Gemini timer
                llm_start_time = time.perf_counter()

                llm_span.set_attribute(
                    "llm.model",
                    "gemini-3.8-flash"
                )

                response = client.models.generate_content(

                    model="gemini-3.8-flash",

                    contents=contents,

                    config=types.GenerateContentConfig(

                        system_instruction=(
                            "You are a helpful assistant. "
                            "Use the available tools whenever "
                            "they are needed to answer the "
                            "user's question."
                        ),

                        tools=tools,

                        automatic_function_calling=(
                            types.AutomaticFunctionCallingConfig(
                                disable=True
                            )
                        ),
                    ),
                )

                # Calculate Gemini latency
                llm_duration_ms = (
                    time.perf_counter() - llm_start_time
                ) * 1000

                llm_span.set_attribute(
                    "llm.duration_ms",
                    llm_duration_ms
                )

                print(
                    f"⏱️ Gemini duration: "
                    f"{llm_duration_ms:.2f} ms"
                )

            # ------------------------------------------------
            # Process Gemini response
            # ------------------------------------------------

            candidate = response.candidates[0]

            contents.append(candidate.content)

            function_call = None

            for part in candidate.content.parts:

                if part.function_call:

                    function_call = part.function_call

                    break

            # ------------------------------------------------
            # Final answer
            # ------------------------------------------------

            if function_call is None:

                print("\n🤖 Agent:")
                print(response.text)

                # Calculate total agent latency
                agent_duration_ms = (
                    time.perf_counter() - agent_start_time
                ) * 1000

                agent_span.set_attribute(
                    "agent.duration_ms",
                    agent_duration_ms
                )

                print(
                    f"⏱️ Total agent duration: "
                    f"{agent_duration_ms:.2f} ms"
                )

                return response.text

            # ------------------------------------------------
            # Execute tool
            # ------------------------------------------------

            result = execute_tool(function_call)

            # ------------------------------------------------
            # Send tool result back to Gemini
            # ------------------------------------------------

            tool_response_part = (
                types.Part.from_function_response(
                    name=function_call.name,
                    response={
                        "result": result
                    },
                )
            )

            contents.append(
                types.Content(
                    role="user",
                    parts=[
                        tool_response_part
                    ],
                )
            )


# ============================================================
# Run agent
# ============================================================

if __name__ == "__main__":

    query = input("Enter your question: ")

    run_agent(query)
