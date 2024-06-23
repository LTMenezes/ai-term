from anthropic import AnthropicVertex
from dotenv import load_dotenv
import click
import os
import os.path
import re
import subprocess
import click
import shlex

load_dotenv()

client = AnthropicVertex(region="europe-west1", project_id="pactohq")

def execute_code(code, verbose=False):
  click.echo(click.style("Shell command:", fg="yellow"))
  try:
    tokens = shlex.split(code)
    if tokens:
        click.echo(click.style(tokens[0], fg="cyan") + " ", nl=False)
        for token in tokens[1:]:
            if token.startswith("-"):
                click.echo(click.style(token, fg="green") + " ", nl=False)
            elif "/" in token:
                click.echo(click.style(token, fg="blue") + " ", nl=False)
            else:
                click.echo(click.style(token, fg="white") + " ", nl=False)
    click.echo()
  except Exception as e:
    click.echo(click.style(f"Shell command: {code}", fg="yellow"))

  user_input = click.prompt("Do you want to execute this command? (y/n)").lower()
  if user_input == "y":
    try:
        result = subprocess.run(code, shell=True, check=True, capture_output=True, encoding="utf-8")
        if verbose:
          click.echo(click.style(f"Shell command output: {result.stdout}", fg="yellow"))
        return result.stdout
    except subprocess.CalledProcessError as e:
        if verbose:
           click.echo(click.style(f"Error running shell command: {e.stderr}", fg="red"))
        return f"Command failed with error: {e.stderr}"
  else:
    return "Command execution cancelled by user."

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


def get_current_directory():
    return os.getcwd()

def send_message(message, verbose):
  global last_pending_shell_output
  current_chat.append({ "role": "user", "content": last_pending_shell_output + "\n" 
                       + f"Current directory: {get_current_directory()} \n"
                       + "New message from user:" + message })
  last_pending_shell_output = ""

  response = client.messages.create(
    max_tokens=4096, #200k max token
    system=SYSTEM_PROMPT,
    messages=current_chat,
    model="claude-3-5-sonnet@20240620",
  )
  click.echo(click.style(response.content[0].text, fg="cyan"))
  current_chat.append({"role": "assistant", "content": response.content[0].text})
  code = extract_code(response.content[0].text)
  
  if code:
    result = execute_code(code, verbose)
    last_pending_shell_output = f"Command executed.\nOutput: {result}"
  
  return response

@click.command()
@click.option("-v", "--verbose", is_flag=True, help="Show output of executed shell commands")
def execute_loop(verbose):
    while True:
        message = click.prompt('Send a message', type=str)
        send_message(message, verbose)

#import ipdb; ipdb.set_trace()
if __name__ == "__main__":
  #send_message("read the content of the chat.py file")
  execute_loop()
  pass
