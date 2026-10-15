import os
import requests
from typing import List, Dict, Any, Optional

from octotools.tools.base import BaseTool

from dotenv import load_dotenv
load_dotenv()


class Serply_Search_Tool(BaseTool):
    TIME_RANGES = {"day": "qdr:d", "week": "qdr:w", "month": "qdr:m", "year": "qdr:y"}

    def __init__(self):
        super().__init__(
            tool_name="Serply_Search_Tool",
            tool_description="A tool that performs Google searches through the Serply API and returns the title, link, and snippet of each result. Supports country targeting and recency filtering.",
            tool_version="1.0.0",
            input_types={
                "query": "str - The search query to be used for the Google search.",
                "num_results": "int - The number of search results to return (default: 10, max: 10).",
                "gl": "str - Optional two-letter country code for localized results, e.g. 'us', 'gb', 'de' (default: None).",
                "time_range": "str - Optional recency filter: 'day', 'week', 'month', or 'year' (default: None).",
            },
            output_type="list - A list of dictionaries containing search result information.",
            demo_commands=[
                {
                    "command": 'execution = tool.execute(query="Python programming")',
                    "description": "Perform a Google search for 'Python programming' and return the default number of results."
                },
                {
                    "command": 'execution = tool.execute(query="AI regulation news", num_results=5, time_range="week")',
                    "description": "Search for 'AI regulation news' published in the past week and return 5 results."
                },
            ],
        )
        self.api_key = os.getenv("SERPLY_API_KEY")  # Ref: https://serply.io
        self.base_url = "https://api.serply.io/v1/search"

    def execute(
        self,
        query: str,
        num_results: int = 10,
        gl: Optional[str] = None,
        time_range: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Executes a Google search through Serply based on the provided query.

        Parameters:
            query (str): The search query.
            num_results (int): The number of search results to return (default: 10, max: 10).
            gl (str): Optional two-letter country code for localized results.
            time_range (str): Optional recency filter: 'day', 'week', 'month', or 'year'.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing search result information.
        """
        if not self.api_key:
            return [{"error": "Serply API key is not set. Please set the SERPLY_API_KEY environment variable."}]
        if time_range is not None and time_range not in self.TIME_RANGES:
            return [{"error": f"Invalid time_range '{time_range}'. Use one of: {', '.join(self.TIME_RANGES)}."}]

        num_results = max(1, min(int(num_results), 10))
        params = {"q": query, "num": num_results}
        if gl:
            params["gl"] = gl
        if time_range:
            params["tbs"] = self.TIME_RANGES[time_range]
        headers = {"X-Api-Key": self.api_key, "User-Agent": "octotools"}

        try:
            response = requests.get(self.base_url, params=params, headers=headers, timeout=30)
            data = response.json()
            if response.status_code != 200:
                detail = data.get("detail") if isinstance(data, dict) else None
                return [{"error": f"Serply API error (HTTP {response.status_code}): {detail or response.reason}"}]

            output = []
            for item in data.get("results") or []:
                link = item.get("link") or ""
                if not link.startswith(("http://", "https://")):
                    continue
                output.append({
                    "title": item.get("title", ""),
                    "link": link,
                    "snippet": item.get("description", ""),
                })
                if len(output) >= num_results:
                    break

            if not output:
                return [{"error": "No results found."}]
            return output

        except Exception as e:
            return [{"error": f"An error occurred: {str(e)}"}]

    def get_metadata(self):
        """
        Returns the metadata for the Serply_Search_Tool.

        Returns:
            dict: A dictionary containing the tool's metadata.
        """
        metadata = super().get_metadata()
        return metadata


if __name__ == "__main__":
    # Test command:
    """
    Run the following commands in the terminal to test the script:

    export SERPLY_API_KEY=your_api_key_here
    cd octotools/tools/serply_search
    python tool.py
    """

    # Example usage of the Serply_Search_Tool
    tool = Serply_Search_Tool()

    # Get tool metadata
    metadata = tool.get_metadata()
    print(metadata)

    # Execute the tool to perform a Google search
    query = "nobel prize winners in chemistry 2024"
    try:
        execution = tool.execute(query=query, num_results=5)
        print("\nExecution Result:")
        print(f"Search query: {query}")
        print(f"Number of results: {len(execution)}")
        print("\nSearch Results:")
        if "error" in execution[0]:
            print(f"Error: {execution[0]['error']}")
        else:
            for i, item in enumerate(execution, 1):
                print(f"\n{i}. Title: {item['title']}")
                print(f"   URL: {item['link']}")
                print(f"   Snippet: {item['snippet']}")
    except Exception as e:
        print(f"Execution failed: {e}")

    print("Done!")
