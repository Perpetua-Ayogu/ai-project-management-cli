# AI Project Management CLI

Module 8 summative lab. A local Python tracker for users, projects, tasks, and contributors.

## Setup

Use Python 3.10 or newer:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py --help
```
On Windows, activate with `.venv\\Scripts\\activate`.

## Commands

```bash
python main.py add-user --name Alex --email alex@example.com
python main.py add-user --name Sam --email sam@example.com
python main.py list-users
python main.py add-project --user Alex --title "CLI Tool" --description "Build tracker" --due-date 2026-12-01
python main.py add-contributor --project "CLI Tool" --user Sam
python main.py add-task --project "CLI Tool" --title "Write help" --assigned-to Sam
python main.py list-projects --user Alex
python main.py list-tasks --project "CLI Tool"
python main.py update-task --project "CLI Tool" --task "Write help" --title "Write CLI help"
python main.py complete-task --project "CLI Tool" --task "Write CLI help"
python main.py update-project --project "CLI Tool" --description "Tracker with help"
python main.py update-user --name Alex --email alex.new@example.com
python main.py summarize-project --project "CLI Tool"
```

Each successful change is saved to `data/project_data.json`. Use `--data /path/to/file.json` before the command for a separate dataset. Missing files start empty. Invalid JSON or invalid records produce an error and are not overwritten.

## Organization and OOP

- `models.py`: Person → User inheritance, Project and Task classes, properties for email/date/status validation, task ID counter, class method to rebuild saved collections, readable string output.
- Users own projects; projects contain tasks. Users can contribute to multiple projects, and projects have multiple contributors. Tasks can be assigned to contributors.
- `main.py`: argparse commands and user messages.
- `services/storage_service.py`: JSON loading and saving through a temporary file.
- `services/ai_client.py`: configurable, reusable Ollama communication with a timeout and readable failures.
- `services/project_summary.py`: sends structured project/task data with a request for progress, risks, and next steps.
- `data/project_data.json`: empty starting dataset; the examples use fictional people.

## AI setup

Install Ollama from its official distribution, start the local service, and run `ollama pull llama3.2`.
The Python dependency is installed above. Choose another installed model with `--model` or `OLLAMA_MODEL`; configure the endpoint with `--host` or `OLLAMA_HOST`.

The AI command sends project descriptions, task details, and contributor names to the configured endpoint. The default endpoint is local. Failed AI calls print a readable error and do not change saved data. AI output is a suggestion and may be inaccurate.

## Limitations

This is a single-user local prototype, not authentication or a concurrent database. Names and project titles are unique; task titles are unique within a project. No deletion command is provided. AI generation needs a running service and installed model; automated service checks can use a fake client.

