import argparse
import os
from pathlib import Path
from services.storage_service import StorageService
from services.ai_client import AIClient
from services.project_summary import summarize_project


def build_parser():
    """Define commands and explain their required arguments."""
    parser = argparse.ArgumentParser(description="Project Management CLI")
    parser.add_argument("--data", default=str(Path(__file__).parent / "data/project_data.json"))
    subparsers = parser.add_subparsers(dest="command", required=True)
    definitions = {
        "add-user": ("Create a user", ["name", "email"]),
        "list-users": ("List all users", []),
        "update-user": ("Update a user's email", ["name", "email"]),
        "add-project": ("Create a user's project", ["user", "title"]),
        "list-projects": ("List a user's projects", ["user"]),
        "update-project": ("Edit project details", ["project"]),
        "add-contributor": ("Add a user to a project", ["project", "user"]),
        "add-task": ("Add a project task", ["project", "title"]),
        "list-tasks": ("List project tasks", ["project"]),
        "update-task": ("Edit a task", ["project", "task"]),
        "complete-task": ("Mark a task complete", ["project", "task"]),
        "summarize-project": ("Ask the local AI for a summary", ["project"]),
    }
    for command, (help_text, required) in definitions.items():
        subparser = subparsers.add_parser(command, help=help_text)
        for name in required:
            subparser.add_argument("--" + name, required=True)
        if command in ("add-project", "update-project"):
            subparser.add_argument("--description", default="" if command == "add-project" else None)
            subparser.add_argument("--due-date", default="" if command == "add-project" else None)
        if command in ("add-task", "update-task"):
            subparser.add_argument("--assigned-to")
        if command == "update-task":
            subparser.add_argument("--title")
            subparser.add_argument("--status", choices=["pending", "complete"])
        if command == "summarize-project":
            subparser.add_argument("--model", default=os.getenv("OLLAMA_MODEL", "llama3.2"))
            subparser.add_argument("--host", default=os.getenv("OLLAMA_HOST", "http://localhost:11434"))
    return parser


def execute(args, tracker):
    """Route a command to the object model or summary service."""
    command = args.command
    if command == "add-user":
        return str(tracker.add_user(args.name, args.email))
    if command == "list-users":
        return "\n".join(str(user) for user in tracker.users) or "No users yet."
    if command == "update-user":
        user = tracker.find_user(args.name)
        user.email = args.email
        return str(user)
    if command == "add-project":
        return str(tracker.add_project(args.user, args.title, args.description, args.due_date))
    if command == "list-projects":
        return "\n".join(str(project) for project in tracker.find_user(args.user).projects) or "No projects yet."
    project = tracker.find_project(args.project)
    if command == "update-project":
        if args.description is not None:
            project.description = args.description
        if args.due_date is not None:
            project.due_date = args.due_date
        return str(project)
    if command == "add-contributor":
        project.add_contributor(tracker.find_user(args.user))
        return f"Added {args.user} to {project.title}."
    if command == "add-task":
        return str(tracker.add_task(args.project, args.title, args.assigned_to))
    if command == "list-tasks":
        return "\n".join(str(task) for task in project.tasks) or "No tasks yet."
    if command == "summarize-project":
        return summarize_project(project, AIClient(args.model, args.host))
    task = tracker.find_task(args.project, args.task)
    if command == "complete-task":
        task.complete()
    elif command == "update-task":
        if args.title is not None:
            from models import required_text
            title = required_text(args.title, "Task title")
            if any(other is not task and other.title == title for other in project.tasks):
                raise ValueError("Task title already exists in this project.")
            task.title = title
        if args.status:
            task.status = args.status
        if args.assigned_to:
            task.assigned_to = tracker.find_user(args.assigned_to)
            project.add_contributor(task.assigned_to)
    return str(task)


def main():
    """Load, execute, and persist successful changes."""
    parser = build_parser()
    args = parser.parse_args()
    storage = StorageService(args.data)
    try:
        tracker = storage.load()
        result = execute(args, tracker)
        if not args.command.startswith("list-") and args.command != "summarize-project":
            storage.save(tracker)
        print(result)
        return 0
    except (ValueError, RuntimeError) as error:
        print(f"Error: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

