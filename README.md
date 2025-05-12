## Installation

1. Clone the repository:
```bash
git clone https://github.com/OGrocketa/gradioChat
cd gradiochat
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Activate the virtual environment:
```bash
poetry shell
```

## Usage

1. Start the application:
```bash
poetry run python main.py
```

2. Open your web browser and navigate to the URL shown in the terminal (typically http://localhost:7860)

## Adding Custom Crews

To add a new crew, create a new directory in the `crews` folder with the following structure:

```
crews/
└── your_crew_name/
    ├── __init__.py
    ├── crew.py
    ├── config/
    │   ├── agents.yaml
    │   └── tasks.yaml
    └── tools/
        └── your_tool.py
```

### Crew Template Example

Here's a template for creating a new crew:

1. Create `your_crew_name.py`:
```python

@CrewBase
class YourCrewName():
    """Your crew description"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def your_agent_name(self) -> Agent:
        return Agent(
            config=self.agents_config['your_agent_name'],
            max_iter=5,
            tools=[]
        )

    @task
    def your_task_name(self) -> Task:
        return Task(
            config=self.tasks_config['your_task_name'],
            max_iter=5
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
```

2. Create `config/agents.yaml`:
```yaml
your_agent_name:
  role: >
    Your agent's role description
  goal: >
    Your agent's goal description
  backstory: >
    Your agent's backstory
```

3. Create `config/tasks.yaml`:
```yaml
your_task_name:
  description: >
    Your task description, to include user input use "{query}"
  expected_output: >
    Expected output description
  agent: your_agent_name    
```

4. Create `tools/your_tool.py`:
```python

@tool("Your Tool")
def your_tool(params):
    """
    Description of the tool
    """
    return "Your tool return"
```

The crew will automatically appear in the UI's agent selection dropdown once added to the `crews` directory.
