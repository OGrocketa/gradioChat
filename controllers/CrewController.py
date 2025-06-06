# controllers/crew_controller.py
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
            crew_module = importlib.import_module(f"crews.{agent_selection}.crew")
            crew_class_name = "".join(word.capitalize() for word in agent_selection.split("_"))
            crew_class = getattr(crew_module, crew_class_name)
            crew_obj = crew_class().crew()
        except (ImportError, AttributeError) as e:
            yield (None, f"Error loading crew {agent_selection}: {e}")
            return

        if crew_obj.agents:
            first_agent = crew_obj.agents[0]

            if crew_tools:
                for tool_name in crew_tools:
                    try:
                        tool_index = crew_model.tools_names.index(tool_name)
                        tool_file_path = crew_model.crew_tools_full_paths[tool_index]
                        tool_module_name = os.path.splitext(os.path.basename(tool_file_path))[0]

                        tool_module = importlib.import_module(
                            f"crews.{agent_selection}.tools.{tool_module_name}"
                        )
                        tool_func = getattr(tool_module, tool_module_name)

                        first_agent.tools.append(tool_func)
                        accumulated_logs += f"\n- Added {tool_name} to {agent_selection}"
                    except ValueError:
                        accumulated_logs += f"\n- Tool {tool_name} not found for {agent_selection}"
                    except Exception as e:
                        accumulated_logs += f"\n- Error adding {tool_name}: {e}"

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
