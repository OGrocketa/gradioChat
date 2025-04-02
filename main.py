from crew.crew import Testcrew

def main():
    crew = Testcrew().crew()
    response = crew.kickoff({"query": "What data types exist?"})
    print(response)

if __name__ == "__main__":
    main()
