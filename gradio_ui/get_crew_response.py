import os
import importlib

def get_crew_response(userInput, agentSelection, processLogs, agentConfig):
    """
    Handle the crew's response to a user query.
    
    Args:
        userInput (str): The user's query
        agentSelection (str): The selected agent type
        processLogs (str): Current process logs
        agentConfig (list): List of selected agent configurations
        
    Yields:
        tuple: (response, logs) containing the crew's response and updated logs
    """
    if not userInput:
        yield (None, "Please enter a query.")
        return
        
    if agentSelection == 'Select an agent':
        yield (None, "Please select an agent.")
        return
        
    try:
        accumulated_logs = processLogs

        try:
            crew_module = importlib.import_module(f"crews.{agentSelection}.crew")
            # (exmaple) pdf_crew -> PdfCrew
            crew_class_name = ''.join(word.capitalize() for word in agentSelection.split('_'))
            crew_class = getattr(crew_module, crew_class_name)
            crew = crew_class().crew()
        except (ImportError, AttributeError) as e:
            yield (None, f"Error loading crew {agentSelection}: {str(e)}")
            return

        # by default all tools are added to the first agent
        if crew.agents:
            first_agent = crew.agents[0]
            
            if agentConfig:
                tools_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "crews", agentSelection, "tools")
                if os.path.exists(tools_dir):
                    for tool_name in agentConfig:
                        # (exmaple) Doc To Summary Tool -> doc_to_summary_tool.py
                        tool_file = tool_name.lower().replace(' ', '_') + '.py'
                        tool_path = os.path.join(tools_dir, tool_file)
                        
                        if os.path.exists(tool_path):
                            try:
                                tool_module = importlib.import_module(f"crews.{agentSelection}.tools.{tool_file[:-3]}")
                                tool_func_name = tool_file[:-3]  # (exmaple) doc_to_summary_tool.py -> doc_to_summary_tool
                                tool_func = getattr(tool_module, tool_func_name)
                            
                                first_agent.tools.append(tool_func)
                                accumulated_logs += f'\n- Added {tool_name} to {agentSelection}'
                            except Exception as e:
                                accumulated_logs += f'\n- Error adding {tool_name}: {str(e)}'
                
                yield (None, accumulated_logs)

        accumulated_logs += '\n- Thinking on the answer...'
        yield (None, accumulated_logs)

        response = crew.kickoff(inputs={"query": userInput})
        if response:
            accumulated_logs += '\n- Answer is ready'
            yield (response, accumulated_logs)
        else:
            yield (None, "No response from crew")
            
    except Exception as e:
        yield (None, f"Error processing query: {str(e)}")