import json
from pathlib import Path
from models import Tracker


class StorageService:
    def __init__(self, filename):
        self.path = Path(filename)

    def load(self):
        """Load data safely; a missing file starts an empty tracker."""
        if not self.path.exists():
            return Tracker()
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return Tracker.from_data(data)
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
            raise ValueError(f"Cannot load {self.path}: {error}. Existing data was not overwritten.") from error

    def save(self, tracker):
        """Replace the saved file only after writing the complete JSON."""
        temporary = self.path.with_suffix(".tmp")
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporary.write_text(json.dumps(tracker.to_data(), indent=2), encoding="utf-8")
            temporary.replace(self.path)
        except OSError as error:
            raise ValueError(f"Cannot save {self.path}: {error}") from error

