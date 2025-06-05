import os
import re

import yaml


class CrewModel:
    def __init__(
            self,
            crew_name=None,
            full_crew_path=None,
            tools_names=None,
            crew_tools_full_paths=None,
            tasks_variables=None,
            preloaded_files_full_path=None):

        self.crew_name = crew_name
        self.full_crew_path = full_crew_path
        self.tools_names = tools_names
        self.crew_tools_full_paths = crew_tools_full_paths
        self.tasks_variables = tasks_variables
        self.preloaded_files_full_path = preloaded_files_full_path

    @staticmethod
    def get_tasks_variables(crew_name):
        """Extract variables from tasks.yaml files for a given crew."""
        crew_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "crews", crew_name)
        tasks_file = os.path.join(crew_dir, "config", "tasks.yaml")

        if os.path.exists(tasks_file):
            with open(tasks_file) as f:
                tasks = yaml.safe_load(f)
                variables = set()
                for task in tasks.values():
                    for description in task.values():
                        matches = re.findall(r"\{([^}]+)\}", description)
                        variables.update(matches)
                return sorted(list(variables))
        return []

    @staticmethod
    def discover_agent_tools(agent_name):
        """
        Discover available tools for a specific agent.

        Args:
            agent_name (str): Name of the agent to discover tools for

        Returns:
            list: Sorted list of available tool names
        """
        tool_names = []
        tool_full_paths = []
        tools_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "crews", agent_name, "tools")

        try:
            if os.path.exists(tools_dir):
                for file in os.listdir(tools_dir):
                    if file.endswith("_tool.py") and not file.startswith("__"):
                        tool_name = file.replace(".py", "").replace("_", " ").title()
                        tool_names.append(tool_name)
                        tool_full_paths.append(os.path.join(tools_dir, file))
        except Exception as e:
            raise e

        return sorted(tool_names), sorted(tool_full_paths)

    @staticmethod
    def get_preloaded_files(agent_name):
        """
        Get preloaded files for a given agent.

        Args:
            agent_name (str): Name of the agent to get preloaded files for

        Returns:
            list: List of preloaded files
        """
        files = []
        files_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "crews", agent_name, "knowledge"
        )

        if os.path.exists(files_dir):
            for file in os.listdir(files_dir):
                files.append(os.path.join(files_dir, file))
        return files

    @classmethod
    def get_available_crews(cls):
        available_crews = []
        crews_paths = os.path.join(os.path.dirname(os.path.dirname(__file__)), "crews")
        for crew in os.listdir(crews_paths):
            if not os.path.isdir(os.path.join(crews_paths, crew)) or crew == "__pycache__":
                continue

            crew_name = crew
            full_crew_path = os.path.join(crews_paths, crew)
            tasks_variables = cls.get_tasks_variables(crew_name)
            tools_names, tools_full_paths = cls.discover_agent_tools(crew_name)
            preloaded_files_full_path = cls.get_preloaded_files(crew_name)

            new_crew = cls(crew_name,
                           full_crew_path,
                           tools_names,
                           tools_full_paths,
                           tasks_variables,
                           preloaded_files_full_path)

            available_crews.append(new_crew)
        return available_crews
