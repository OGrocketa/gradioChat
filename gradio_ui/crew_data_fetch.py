import os, re, yaml

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

def extract_variables_from_tasks(crew_name):
    """Extract variables from tasks.yaml files for a given crew."""
    crew_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'crews', crew_name)
    tasks_file = os.path.join(crew_dir, 'config', 'tasks.yaml')
    
    if os.path.exists(tasks_file):
        with open(tasks_file, 'r') as f:
            tasks = yaml.safe_load(f)
            variables = set()
            for task in tasks.values():
                for description in task.values():
                    matches = re.findall(r'\{([^}]+)\}', description)
                    variables.update(matches)
            return sorted(list(variables))
        
def get_preloaded_files(agent_name):
    """
    Get preloaded files for a given agent.
    
    Args:
        agent_name (str): Name of the agent to get preloaded files for
        
    Returns:
        list: List of preloaded files
    """
    files = []
    files_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "crews", agent_name, "knowledge")
    
    if os.path.exists(files_dir):
        for file in os.listdir(files_dir):
            files.append(os.path.join(files_dir, file))
    return files

