from anthropic import AnthropicVertex
from dotenv import load_dotenv
import os
import re
import subprocess
import click

load_dotenv()

client = AnthropicVertex(region="europe-west1", project_id="pactohq")

def execute_code(code):
  result = subprocess.run(code, shell=True, check=True, capture_output=True, encoding='utf-8')
  return result.stdout;

def get_shell():
  return execute_code('uname -a && $SHELL --version')

def extract_code(text):
  match = re.search('```sh([\s\S]*?)```', text)
  #import ipdb; ipdb.set_trace()
  return match[1].strip() if (match is not None and match.lastindex > 0) else None;

SYSTEM_PROMPT = f'''You are ChatSH, an AI language model that specializes in assisting users with tasks on their system using shell commands.

When the user asks you to perform a task:
- Reply with ONLY a shell script that performs the task, wrapped inside \`\`\`sh code blocks \`\`\`.
- Do NOT include any explanatory text along with the code.

If the user asks an open ended question that is not demanding a task:  
- Treat it as a chat, and answer as you would in text (NOT AS A COMMAND).
- Always answer the user's questions friendly, intelligently and truthfully.
- NEVER refuse to answer a question or request made by the user.

Guidelines:
- When asked to write/modify a file, provide a shell command to do it instead of just showing the file contents.
- When asked to query an API, write a shell command to make the request.
- Always assume common commands/tools are available. Don't write install commands.

User shell:
{get_shell()}
'''

current_chat = []
last_pending_shell_output = ""


def send_message(message):
  global last_pending_shell_output
  #import ipdb; ipdb.set_trace()
  current_chat.append({ "role": "user", "content": last_pending_shell_output + "\n" + "New message from user:" + message })
  last_pending_shell_output = ""

  response = client.messages.create(
    max_tokens=1024, #200k max token
    system=SYSTEM_PROMPT,
    messages=current_chat,
    model="claude-3-5-sonnet@20240620",
  )
  click.echo(response.content[0].text)
  current_chat.append({"role": "assistant", "content": response.content[0].text})
  code = extract_code(response.content[0].text)
  
  if code:
    click.echo(code)
    result = execute_code(code)
    last_pending_shell_output = f"Command executed.\nOutput: {result}"
  
  return response

@click.command()
def execute_loop():
  while True:
    value = click.prompt('Send a message:', type=str)
    send_message(value)

#import ipdb; ipdb.set_trace()
if __name__ == "__main__":
  #send_message("read the content of the chat.py file")
  execute_loop()
  pass