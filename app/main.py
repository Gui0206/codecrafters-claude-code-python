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

    if not API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    messages=[{"role": "user", "content": args.p}]


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

    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)

    print("hellooooo")

    print(client)

    for tc in chat.choices[0].message.tool_calls or []:
        if tc.function.name == "Read":
            arguments = json.loads(tc.function.arguments)

            file_path = arguments.get("file_path")

            if file_path:
                with open(file_path) as f:
                    print(f.read())

if __name__ == "__main__":
    main()


# {
#   "choices": [
#     {
#       "index": 0,
#       "message": {
#         "role": "assistant",
#         "content": null,
#         "tool_calls": [
#           {
#             "id": "call_abc123",
#             "type": "function",
#             "function": {
#               "name": "Read",
#               "arguments": "{\"file_path\": \"/path/to/file.txt\"}"
#             }
#           }
#         ]
#       },
#       "finish_reason": "tool_calls"
#     }
#   ]
# }