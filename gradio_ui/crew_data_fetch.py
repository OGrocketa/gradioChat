import os

def get_agent_tools(agentName):
    tools = []
    tools_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "crews", agentName, "tools")
    if os.path.exists(tools_dir):
        print(tools_dir)
        for file in os.listdir(tools_dir):
            if file.endswith("_tool.py") and not file.startswith("__"):
                tools.append(file.replace('.py', ''))
    return sorted(tools)

def get_crews():
    crews = []
    crews_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "crews")
    for file in os.listdir(crews_dir):
        if os.path.isdir(os.path.join(crews_dir, file)) and file != "__pycache__":
            crews.append(file)
    return sorted(crews)