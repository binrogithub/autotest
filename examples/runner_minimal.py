"""Minimal example for the tool runner."""
from core.tools.registry import ToolRegistry
from core.tools.runner import run


def mock_handler(name: str) -> dict[str, str]:
    return {"message": f"hello, {name}"}


def main() -> None:
    registry = ToolRegistry()
    registry.register("mock", mock_handler)

    envelope = run("mock", registry, "world")
    print(envelope)


if __name__ == "__main__":
    main()
