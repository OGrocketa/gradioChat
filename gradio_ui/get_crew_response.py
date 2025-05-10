def get_crew_response(userInput,agentSelection,processLogs,agentConfig):
            if not userInput:
                yield(None,"Please enter a query.") 
            if agentSelection == 'Select an agent':
                yield(None,"Please select an agent.") 
            accumulated_logs = processLogs

            crew = PdfCrew().crew()

            pdf_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "crews", "pdf_crew", "knowledge")

            for file in os.listdir(pdf_dir):
                pdf_path = os.path.join(pdf_dir, file)
                ragTool.add(source=pdf_path)
            

            if agentSelection == 'PdfExpert':
                for agent in crew.agents:
                    if hasattr(agent, "role") and agent.role.strip().lower() == "data_extractor":
                        data_extractor_agent = agent
                        break

                if("Summarize Text" in agentConfig):
                    data_extractor_agent.tools.append(doc_to_summary_tool)
                
                yield (None, accumulated_logs)

            accumulated_logs = accumulated_logs + '\n- Thinking on the answer...' 
            yield (None, accumulated_logs)

            response = crew.kickoff({"query": userInput})
            if response:
                accumulated_logs = accumulated_logs + '\n- Answer is ready' 

            yield (response, accumulated_logs)