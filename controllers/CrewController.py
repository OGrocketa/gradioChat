import importlib
import os

from models.CrewModel import CrewModel


class CrewController:

    def __init__(self) -> None:
        self._model_cache: dict[str, CrewModel] = {}

    def _get_model(self, crew_name: str) -> CrewModel:
        if crew_name not in self._model_cache:
            self._model_cache[crew_name] = CrewModel.get_crew(crew_name)
        return self._model_cache[crew_name]

    def list_crews(self) -> list[str]:
        return [m.crew_name for m in CrewModel.get_available_crews()]

    def list_tools(self, crew_name: str) -> list[str]:
        tools, _, _ = CrewModel.discover_agent_tools(crew_name)
        return tools

    def task_variables(self, crew_name: str) -> list[str]:
        return CrewModel.get_tasks_variables(crew_name)

    def preloaded_files(self, crew_name: str) -> list[str]:
        return CrewModel.get_preloaded_files(crew_name)

    def _import_crew(self, agent_selection: str):
        """Dynamically import crew class and return crew object."""
        try:
            crew_module = importlib.import_module(f"crews.{agent_selection}.crew")
            crew_class_name = "".join(word.capitalize() for word in agent_selection.split("_"))
            crew_class = getattr(crew_module, crew_class_name)
            return crew_class().crew()
        except (ImportError, AttributeError) as e:
            raise RuntimeError(f"Error loading crew {agent_selection}: {e}")

    def _attach_tools_to_agent(self, crew_obj, crew_name: str, crew_tools: list[str], accumulated_logs: str) -> str:
        """Attach selected tools to the first agent and return updated logs."""
        if not crew_obj.agents:
            return accumulated_logs

        first_agent = crew_obj.agents[0]
        if not crew_tools:
            return accumulated_logs

        for tool_name in crew_tools:
            try:
                tools, _, _ = CrewModel.discover_agent_tools(crew_name)
                tool_index = tools.index(tool_name)
                tool_file_path = CrewModel.get_crew_tools_full_paths(crew_name)[tool_index]
                tool_module_name = os.path.splitext(os.path.basename(tool_file_path))[0]

                tool_module = importlib.import_module(
                    f"crews.{crew_name}.tools.{tool_module_name}"
                )
                tool_func = getattr(tool_module, tool_module_name)

                first_agent.tools.append(tool_func)
                accumulated_logs += f"\n- Added {tool_name} to {crew_name}"
            except ValueError:
                accumulated_logs += f"\n- Tool {tool_name} not found for {crew_name}"
            except Exception as e:
                accumulated_logs += f"\n- Error adding {tool_name}: {e}"

        return accumulated_logs

    def get_crew_response(self, *args):
        """
        Handle the crew's response to a user query.

        Args:
            user_input (str):                The user's query               (args[:-3])
            agent_selection (str):           The selected crew/agent type   (args[-3])
            process_logs (str):              Current process logs           (args[-2])
            crew_tools (list[str] | None):   Selected extra tool names      (args[-1])

        Yields:
            tuple(response, logs)
        """

        user_input, agent_selection, process_logs, crew_tools = (
            args[:-3],
            args[-3],
            args[-2],
            args[-1],
        )
        inputs: dict[str, str] = {}


        if not user_input:
            yield (None, "Please enter a query.")
            return

        if agent_selection == "Select an agent":
            yield (None, "Please select an agent.")
            return

        crew_model = self._get_model(agent_selection)

        if crew_model.tasks_variables:
            for count, var in enumerate(crew_model.tasks_variables):
                    inputs[var] = user_input[count]

        accumulated_logs = process_logs

        try:
            crew_obj = self._import_crew(agent_selection)
        except RuntimeError as e:
            yield (None, str(e))
            return

        if crew_obj.agents:
            accumulated_logs = self._attach_tools_to_agent(
                crew_obj, agent_selection, crew_tools, accumulated_logs
            )
            yield (None, accumulated_logs)

        accumulated_logs += "\n- Thinking on the answer..."
        yield (None, accumulated_logs)

        try:
            response = crew_obj.kickoff(inputs=inputs)
        except Exception as e:
            yield (None, f"Error processing query: {e}")
            return

        if response:
            accumulated_logs += "\n- Answer is ready"
            yield (response, accumulated_logs)
        else:
            yield (None, "No response from crew")
