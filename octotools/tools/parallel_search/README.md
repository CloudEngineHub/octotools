# Parallel Search Tool

Search the web and fetch page excerpts with [Parallel Search MCP](https://docs.parallel.ai/integrations/mcp/search-mcp).
The anonymous endpoint uses Fast mode for search and requires no account or API key.
Free access has lower rate limits; it is intended for exploration and light use.

For an existing OctoTools installation, install the optional dependency from the
repository root:

```sh
python -m pip install '.[parallel-search]'
```

To try only this tool in a fresh environment, install its minimal dependencies
and the local package without the unrelated model and vision dependencies:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r octotools/tools/parallel_search/requirements.txt
python -m pip install --no-deps -e .
python examples/parallel_search.py
```

The example loads `Parallel_Search_Tool` through `Initializer`, then executes
search and fetch directly. It does not invoke an LLM. To use the tool in a Solver,
include `"Parallel_Search_Tool"` in your existing `enabled_tools` list and keep your
chosen model configuration. Other tools and Solver models need their own dependencies.

```python
from octotools.tools.parallel_search.tool import Parallel_Search_Tool

tool = Parallel_Search_Tool(timeout=60)
result = tool.execute(
    objective="Find the official Python documentation",
    search_queries=["Python official documentation"],
)
page = tool.execute(
    urls=["https://docs.python.org/3/"],
    objective="Python documentation",
)
```

Supply either `search_queries` (with a required `objective`) or `urls` (up to 20
HTTP(S) URLs). Fetch objectives are optional and limited to 200 characters.
Results retain the MCP `content`, optional `structuredContent`, and `isError` fields.
Connection, input and timeout failures return an `error` field. The tool uses
Streamable HTTP with a 60-second total timeout by default and sends no authentication.
Calls are synchronous, matching OctoTools' Executor; run them outside an active
async event loop.

Each tool instance generates a conversation ID and reuses it across calls. When
using the Executor, which instantiates tools per command, pass the same optional
`session_id` across related calls (1-100 characters). Model identifiers are omitted
because this tool does not have a verified model configuration.

Run the offline transport and loader tests from the repository root:

```sh
python -m unittest discover -s tests -p 'test_parallel_search.py'
```
