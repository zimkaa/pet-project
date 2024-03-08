import sys
from datetime import datetime
from datetime import timezone
from pathlib import Path

from src.config import settings
from src.config.constants import README_PATH


class Build:
    def __init__(self, *, production: bool) -> None:
        self.production = production
        self.version = settings.VERSION

    def _get_created_date(self) -> datetime:
        timestamp = Path(README_PATH).stat().st_ctime
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)

    def _generate_version_code(self) -> int:
        start_dev = self._get_created_date()
        current_date = datetime.now(tz=timezone.utc)
        difference = current_date - start_dev
        return difference.seconds

    def change_version(self) -> None:
        if not self.production:
            version_code = self._generate_version_code()
            build_number = f"-{version_code}"
            self.version = f"{self.version}{build_number}"

    def get_version(self) -> str:
        self.change_version()
        return self.version


def main(*, production: bool = False) -> None:
    build = Build(production=production)
    sys.stdout.write(f"{build.get_version()}\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-production", action="store_true", help="Creates a build version for production")
    args = parser.parse_args()
    main(production=args.production)
