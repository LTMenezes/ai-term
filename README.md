# AiTerm

AiTerm is an interactive command-line tool that leverages AI to assist users with shell commands and system tasks. It provides a chat-like interface where users can ask questions or request tasks, and the AI responds with appropriate shell commands or information.

Heavily inspired by Taelin's [ChatSH](https://github.com/VictorTaelin/ChatSH).

## Features

- AI-powered assistance for shell commands and system tasks
- Interactive command-line interface
- Executes shell commands with user confirmation
- Maintains conversation context
- Supports a wide range of shell-related queries and tasks

## Prerequisites

- Python 3.x
- Anthropic API access (Claude model)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/aiterm.git
   cd aiterm
   ```
2. Ensure you have set up Google Cloud authentication.

## Usage

Run the script:

```
python chat.py
```

Follow the prompts to interact with the AI assistant. You can ask questions, request tasks, or ask for shell commands. When the AI suggests a command, you'll be prompted to confirm before execution.

## Security Note

Always review suggested commands before execution, especially when dealing with system-level operations.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
