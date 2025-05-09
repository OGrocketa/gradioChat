import os

def discover_agent_tools(agent_name):
    """
    Discover available tools for a specific agent.
    
    Args:
        agent_name (str): Name of the agent to discover tools for
        
    Returns:
        list: Sorted list of available tool names
    """
    tools = []
    tools_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "crews", agent_name, "tools")
    
    try:
        if os.path.exists(tools_dir):
            for file in os.listdir(tools_dir):
                if file.endswith("_tool.py") and not file.startswith("__"):
                    # Convert snake_case to Title Case for display
                    tool_name = file.replace('.py', '').replace('_', ' ').title()
                    tools.append(tool_name)
    except Exception as e:
        print(f"Error discovering tools for {agent_name}: {str(e)}")
        
    return sorted(tools)

def discover_available_crews():
    """
    Discover all available crew types in the crews directory.
    
    Returns:
        list: Sorted list of available crew names
    """
    crews = []
    crews_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "crews")
    
    try:
        for file in os.listdir(crews_dir):
            if os.path.isdir(os.path.join(crews_dir, file)) and file != "__pycache__":
                crews.append(file)
    except Exception as e:
        print(f"Error discovering crews: {str(e)}")
        
    return sorted(crews)