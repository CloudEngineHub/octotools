"""Load the native tool, then run anonymous search and page fetching."""

import importlib
import json

from octotools.models.initializer import Initializer


def main():
    initializer = Initializer(
        enabled_tools=["Parallel_Search_Tool"], model_string="gpt-4o"
    )
    name = "Parallel_Search_Tool"
    if name not in initializer.available_tools:
        raise RuntimeError("Parallel_Search_Tool was not loaded")
    directory = initializer.tool_directory_mapping[name]
    module = importlib.import_module(f"tools.{directory}.tool")
    tool = getattr(module, name)()
    for arguments in (
        {
            "objective": "Find the official Python documentation",
            "search_queries": ["Python official documentation"],
        },
        {"urls": ["https://docs.python.org/3/"], "objective": "Python documentation"},
    ):
        result = tool.execute(**arguments)
        if result.get("error") or result.get("isError"):
            raise RuntimeError(json.dumps(result))
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
