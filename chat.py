from anthropic import AnthropicVertex
import tempfile
from dotenv import load_dotenv
import click
import os
import os.path
import re
import subprocess
import click
import shlex

load_dotenv()

client = AnthropicVertex(region="europe-west1", project_id="YOUR_PROJECT_ID")
current_chat = []
last_pending_shell_output = ""
current_directory = os.getcwd()


def execute_code(code, verbose=False):
    global current_directory
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

    click.echo(click.style(f"Currently on: {current_directory}", fg="yellow"))
    user_input = click.prompt("Do you want to execute this command? (y/n)").lower()
    if user_input == "y":
        try:
            with tempfile.NamedTemporaryFile(mode="w+") as temp:
                temp.write(f"cd {current_directory} && {code} && pwd")
                temp.flush()
                result = subprocess.run(
                    f"bash {temp.name}",
                    shell=True,
                    check=True,
                    capture_output=True,
                    text=True,
                )
            output_lines = result.stdout.strip().split("\n")
            current_directory = (
                output_lines[-1]
                if output_lines[-1] is not None and output_lines[-1].strip()
                else current_directory
            )

            output = "\n".join(output_lines[:-1])
            if verbose:
                click.echo(click.style(f"Shell command output: {output}", fg="yellow"))
            return output
        except subprocess.CalledProcessError as e:
            if verbose:
                click.echo(
                    click.style(f"Error running shell command: {e.stderr}", fg="red")
                )
            return f"Command failed with error: {e.stderr}"
    else:
        return "Command execution cancelled by user."


def get_shell():
    return execute_code("uname -a && $SHELL --version")


SYSTEM_PROMPT = f"""You are ChatSH, an AI language model that specializes in assisting users with tasks on their system using shell commands.

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
"""


def extract_code(text):
    match = re.search("```sh([\s\S]*?)```", text)
    return match[1].strip() if (match is not None and match.lastindex > 0) else None


def send_message(message, verbose):
    global last_pending_shell_output, current_directory
    current_chat.append(
        {
            "role": "user",
            "content": last_pending_shell_output
            + "\n"
            + f"Current directory: {current_directory} \n"
            + "New message from user:"
            + message,
        }
    )
    last_pending_shell_output = ""

    response = client.messages.create(
        max_tokens=4096,  # 200k max token
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
@click.option(
    "-v", "--verbose", is_flag=True, help="Show output of executed shell commands"
)
def execute_loop(verbose):
    while True:
        message = click.prompt("Send a message", type=str)
        send_message(message, verbose)


# import ipdb; ipdb.set_trace()
if __name__ == "__main__":
    execute_loop()
    pass
