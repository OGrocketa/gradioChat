from crew.crew import Testcrew
from crewai_tools import RagTool
import gradio as gr
import os,shutil

def get_agent_tools(agentName):
    if(agentName == 'PdfExpert'):
        return ["Summarize Text", "Tool2", "Tool3"]
    elif(agentName == 'Agent 2'):
        return ["Tool1", "Tool2"]
    else:
        return []

def process_file(uploaded_files,logs):
    pdf_dir = os.path.join(os.path.dirname(__file__), "pdfs")
    if os.path.exists(pdf_dir):
        shutil.rmtree(pdf_dir)

    os.makedirs(pdf_dir)
    
    for uploaded_file in uploaded_files:
        file_name = os.path.basename(uploaded_file.name)
        destination = os.path.join(pdf_dir, file_name)
        shutil.copy(uploaded_file.name, destination)

    return logs + "\n- Files uploaded, you can ask questions"


with gr.Blocks() as demo:
    gr.Markdown("# CrewAI Demo")
    with gr.Row():
        with gr.Column(scale=1):
            agentSelection = gr.Dropdown(choices=['Select an agent','PdfExpert','Agent 2'], label="Select Agent",interactive=True)
            agentConfig = gr.CheckboxGroup(label="Agent Config", interactive=True,choices=[])
            files = gr.File(label="Upload Files", file_count="multiple", file_types=[".pdf"])
            userInput = gr.Textbox(lines=5, label="Enter your query")
            submitBtn = gr.Button("Submit")
    
        with gr.Column(scale=2):
            processLogs = gr.Textbox(lines=5, label="Logs", autoscroll=True, interactive=False)
            output = gr.Textbox(lines=5, label="Output Box")
            
    
    def update_agent_config(agent):
        return gr.update(choices=get_agent_tools(agent))

    agentSelection.change(
        fn=update_agent_config, 
        inputs=agentSelection, 
        outputs=agentConfig
    )

    @files.upload(inputs=[files,processLogs],outputs=processLogs)
    def upload_files(files,logs):
        return process_file(files,logs)
    
    @files.clear(inputs=[files,processLogs],outputs=processLogs)
    def upload_files(files,logs):
        pdf_dir = os.path.join(os.path.dirname(__file__), "pdfs")
        shutil.rmtree(pdf_dir)
        return logs + "\n " + "- Files deleted to ask questions you need to upload files again"
    

    @submitBtn.click(inputs=[userInput,agentSelection,processLogs], outputs=[output, processLogs])
    def get_answer(userInput,agentSelection,processLogs):
        if not userInput:
            return "Please enter a query."
        if agentSelection == 'Select an agent':
            return "Please select an agent."

        crew = Testcrew().crew()
        ragTool = RagTool()

        pdf_dir = os.path.join(os.path.dirname(__file__), "pdfs")

        for file in os.listdir(pdf_dir):
            pdf_path = os.path.join(pdf_dir, file)
            ragTool.add(source=pdf_path)
        

        if agentSelection == 'PdfExpert':
            for agent in crew.agents:
                if hasattr(agent, "role") and agent.role.strip().lower() == "data extractor":
                    data_extractor_agent = agent
                    break

            data_extractor_agent.tools.append(ragTool)
            newProcessLogs = processLogs + '\n- Added RagTool to PdfExpert' 
            yield (None, newProcessLogs)

        newProcessLogs = processLogs + '\n- Thinking on the answer...' 
        yield (None, newProcessLogs)

        response = crew.kickoff({"query": userInput})
        if response:
            newProcessLogs = processLogs + '\n- Answer is ready' 
            
        yield (response, newProcessLogs)

try:
    demo.launch()
except e:
    print("Error launching the app:", e)
finally:
    pdf_dir = os.path.join(os.path.dirname(__file__), "pdfs")
    if os.path.exists(pdf_dir):
        shutil.rmtree(pdf_dir)