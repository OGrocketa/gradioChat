from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.memory import LongTermMemory
from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage
from dotenv import load_dotenv
import os


load_dotenv()

@CrewBase
class Testcrew():
	"""Testcrew crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'
	

	@agent
	def data_extractor(self) -> Agent:
		return Agent(
			config=self.agents_config['data_extractor'],
			max_iter = 5,
			tools=[]

		)

	@agent
	def data_summarizer(self) -> Agent:
		return Agent(
			config=self.agents_config['data_summarizer'],
		)
	
	@task
	def research_task(self) -> Task:
		return Task(
			config=self.tasks_config['retrieve_data'],
			max_iter= 5,
		)

	@task
	def reporting_task(self) -> Task:
		return Task(
			config=self.tasks_config['summarize_data'],
			max_iter=5,
		)
	
	@crew
	def crew(self) -> Crew:
		"""Creates the Testcrew crew"""

		return Crew(
			agents=self.agents,
			tasks=self.tasks,
			process=Process.sequential,
			verbose=True,
		)