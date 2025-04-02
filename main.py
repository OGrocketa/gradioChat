from crew.crew import Testcrew

crew = Testcrew().crew()
response= crew.kickoff({"query":"What data types exist?"})
print(response)