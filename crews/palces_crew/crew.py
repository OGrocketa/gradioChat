from crewai import Agent, Crew, Task, Process
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class PlacesCrew():
    """PlacesCrew crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'


    @agent
    def places_api_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['places_api_agent'],
            tools=[],
            verbose=True,
            max_iter=3,
            
        )

    @task
    def get_coordinates_task(self) -> Task:
        return Task(
            config=self.tasks_config['get_coordinates_task'],
            async_execution=True,
        )

    @task
    def places_api_task(self) -> Task:
        return Task(
            config=self.tasks_config['places_api_task'],
            async_execution=False,
        )
    

    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_task'],
        )
    
    @crew
    def crew(self) -> Crew:
        """Creates the Core crew"""

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential, 
            verbose=True,
        )
