import argparse
import os
import sys
import json

from openai import OpenAI

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL", default="https://openrouter.ai/api/v1")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("-p", required=True)
    args = p.parse_args()

    messages=[{"role": "user", "content": args.p}]

    connection = call_lm(messages)

    while connection.tool_calls:
        messages.append(connection)
        for tool_call in connection.tool_calls:
            messages.append(exec_tool_call(tool_call))
        connection = call_lm(messages)

def call_lm(messages):
    if not API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    chat = client.chat.completions.create(
        model="anthropic/claude-haiku-4.5",
        messages=messages,
        tools= [
            {
                "type": "function",
                "function": {
                    "name": "Read",
                    "description": "Read and returns the content of a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "The path to the file to read"
                            }
                        },
                        "required": ["file_path"]
                    }
                }
            }
            ]
    )

    if not chat.choices or len(chat.choices) == 0:
        raise RuntimeError("no choices in response")
    
    return chat.choices[0].message

def exec_tool_call(tool_call):
    for tc in tool_call.choices[0].message.tool_calls or []:
        if tc.function.name == "Read":
            arguments = json.loads(tc.function.arguments)

            file_path = arguments.get("file_path")

            if file_path:
                with open(file_path) as f:
                    print(f.read())

if __name__ == "__main__":
    main()