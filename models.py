from datetime import date


def required_text(value, label):
    """Validate a required text value."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} cannot be empty.")
    return value.strip()


class Person:
    def __init__(self, name, email):
        self.name = required_text(name, "Name")
        self.email = email

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        if not isinstance(value, str) or "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("Enter a valid email address.")
        self._email = value.strip()


class User(Person):
    def __init__(self, name, email):
        super().__init__(name, email)
        self.projects = []

    def __str__(self):
        return f"{self.name} <{self.email}>"


class Task:
    next_id = 1

    def __init__(self, title, assigned_to=None, status="pending", task_id=None):
        self.title = required_text(title, "Task title")
        self.assigned_to = assigned_to
        self.status = status
        self.id = Task.next_id if task_id is None else task_id
        Task.next_id = max(Task.next_id, self.id + 1)

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        if value not in ("pending", "complete"):
            raise ValueError("Status must be pending or complete.")
        self._status = value

    def complete(self):
        self.status = "complete"

    def __str__(self):
        assigned = self.assigned_to.name if self.assigned_to else "Unassigned"
        return f"{self.id}: {self.title} [{self.status}] - {assigned}"


class Project:
    def __init__(self, title, description="", due_date=""):
        self.title = required_text(title, "Project title")
        self.description = description
        self.due_date = due_date
        self.tasks = []
        self.contributors = []

    @property
    def due_date(self):
        return self._due_date

    @due_date.setter
    def due_date(self, value):
        if value:
            date.fromisoformat(value)
        self._due_date = value

    def add_contributor(self, user):
        if user not in self.contributors:
            self.contributors.append(user)

    def __str__(self):
        completed = sum(task.status == "complete" for task in self.tasks)
        return f"{self.title}: {completed}/{len(self.tasks)} complete; due {self.due_date or 'not set'}"


class Tracker:
    def __init__(self):
        self.users = []

    @classmethod
    def from_data(cls, data):
        """Rebuild object relationships from saved JSON."""
        tracker = cls()
        for record in data["users"]:
            tracker.add_user(record["name"], record["email"])
        for record in data["users"]:
            owner = tracker.find_user(record["name"])
            for saved in record["projects"]:
                project = tracker.add_project(owner.name, saved["title"], saved["description"], saved["due_date"])
                for name in saved.get("contributors", []):
                    project.add_contributor(tracker.find_user(name))
                for task in saved["tasks"]:
                    assigned = tracker.find_user(task["assigned_to"]) if task["assigned_to"] else None
                    project.tasks.append(Task(task["title"], assigned, task["status"], task["id"]))
        return tracker

    def to_data(self):
        return {"users": [
            {"name": user.name, "email": user.email, "projects": [
                {"title": project.title, "description": project.description,
                 "due_date": project.due_date,
                 "contributors": [person.name for person in project.contributors],
                 "tasks": [{"id": task.id, "title": task.title, "status": task.status,
                            "assigned_to": task.assigned_to.name if task.assigned_to else None}
                           for task in project.tasks]}
                for project in user.projects]}
            for user in self.users]}

    def find_user(self, name):
        for user in self.users:
            if user.name == name:
                return user
        raise ValueError(f"User '{name}' not found.")

    def find_project(self, title):
        for user in self.users:
            for project in user.projects:
                if project.title == title:
                    return project
        raise ValueError(f"Project '{title}' not found.")

    def find_task(self, project_title, title):
        for task in self.find_project(project_title).tasks:
            if task.title == title:
                return task
        raise ValueError(f"Task '{title}' not found.")

    def add_user(self, name, email):
        user = User(name, email)
        if any(existing.name == user.name for existing in self.users):
            raise ValueError("User name already exists.")
        self.users.append(user)
        return user

    def add_project(self, user_name, title, description="", due_date=""):
        owner = self.find_user(user_name)
        project = Project(title, description, due_date)
        if any(existing.title == project.title for user in self.users for existing in user.projects):
            raise ValueError("Project title already exists.")
        owner.projects.append(project)
        project.add_contributor(owner)
        return project

    def add_task(self, project_title, title, assigned_to=None):
        project = self.find_project(project_title)
        person = self.find_user(assigned_to) if assigned_to else None
        task = Task(title, person)
        if any(existing.title == task.title for existing in project.tasks):
            raise ValueError("Task title already exists in this project.")
        project.tasks.append(task)
        if person:
            project.add_contributor(person)
        return task

