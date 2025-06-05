import importlib
import os
from models import CrewModel

class CrewController:

    def get_crew_response(self, *args):
        """
        Handle the crew's response to a user query.
        Args:
            user_input (str): The user's query
            crew_selection (str): The selected crew type
            process_logs (str): Current process logs
            agent_config (list): List of selected agent configurations
        Yields:
            tuple: (response, logs) containing the crew's response and updated logs
        """
        user_input = args[:-3]
        crew_selection = args[-3]
        process_logs = args[-2]
        agent_config = args[-1]
    

        inputs = dict()

        if not user_input:
            yield (None, "Please enter a query.")
            return

        if crew_selection == "Select an agent":
            yield (None, "Please select an agent.")
            return
        
        crew_model = CrewModel.get_crew(crew_selection)
        variables = crew_model.tasks_variables
        if variables:
            for count, variable in enumerate(variables):
                inputs.update({variable: user_input[count]})

        try:
            accumulated_logs = process_logs
            try:
                crew_module = importlib.import_module(f"crews.{crew_selection}.crew")
                # (exmaple) pdf_crew -> PdfCrew
                crew_class_name = "".join(word.capitalize() for word in crew_selection.split("_"))
                crew_class = getattr(crew_module, crew_class_name)
                crew = crew_class().crew()
            except (ImportError, AttributeError) as e:
                yield (None, f"Error loading crew {crew_selection}: {str(e)}")
                return

            # by default all tools are added to the first agent
            if crew.agents:
                first_agent = crew.agents[0]
                if agent_config and crew_model.tools_names and crew_model.crew_tools_full_paths:
                    tool_name_to_path = dict(zip(crew_model.tools_names, crew_model.crew_tools_full_paths))
                    for tool_name in agent_config:
                        tool_path = tool_name_to_path.get(tool_name)
                        if tool_path and os.path.exists(tool_path):
                            try:
                                tool_module_name = os.path.splitext(os.path.basename(tool_path))[0]
                                tool_module = importlib.import_module(
                                    f"crews.{crew_selection}.tools.{tool_module_name}"
                                )
                                tool_func = getattr(tool_module, tool_module_name)
                                first_agent.tools.append(tool_func)
                                accumulated_logs += (
                                    f"\n- Added {tool_name} to {crew_selection}"
                                )
                            except Exception as e:
                                accumulated_logs += (
                                    f"\n- Error adding {tool_name}: {str(e)}"
                                )
                    yield (None, accumulated_logs)
            accumulated_logs += "\n- Thinking on the answer..."
            yield (None, accumulated_logs)
            response = crew.kickoff(inputs=inputs)
            if response:
                accumulated_logs += "\n- Answer is ready"
                yield (response, accumulated_logs)
            else:
                yield (None, "No response from crew")
        except Exception as e:
            yield (None, f"Error processing query: {str(e)}")
