from crews import PdfCrew
from crews.pdf_crew import doc_to_summary_tool
from crewai_tools import RagTool
import gradio as gr
import os, shutil

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


def process_file(uploaded_files, logs, selected_agent):
    pdf_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "crews", selected_agent, "knowledge")
    if os.path.exists(pdf_dir):
        shutil.rmtree(pdf_dir)

    os.makedirs(pdf_dir)
    
    for uploaded_file in uploaded_files:
        file_name = os.path.basename(uploaded_file.name)
        destination = os.path.join(pdf_dir, file_name)
        shutil.copy(uploaded_file.name, destination)

    return logs + "\n- Files uploaded, you can ask questions"

def create_ui():
    with gr.Blocks() as demo:
        gr.Markdown("# CrewAI Demo")
        with gr.Row():
            with gr.Column(scale=1):
                agentSelection = gr.Dropdown(choices=get_crews(), label="Select Agent", interactive=True, value=get_crews()[0])
                agentConfig = gr.CheckboxGroup(label="Agent Config", interactive=True, choices=get_agent_tools(get_crews()[0]))
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

        @files.upload(inputs=[files,processLogs,agentSelection],outputs=processLogs)
        def upload_files(files,logs,agentSelection):
            return process_file(files,logs,agentSelection)
        
        @files.delete(inputs=[processLogs,agentSelection], outputs=processLogs)
        def delete_files(deleted_data: gr.DeletedFileData, logs, agentSelection):
            pdf_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "crews", agentSelection, "knowledge")
            file_name = os.path.basename(deleted_data.file.path)
            file_path = os.path.join(pdf_dir, file_name)
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logs += f"\n- {file_name} deleted from directory."
                else:
                    logs += f"\n- {file_name} not found in directory."
            except Exception as e:
                logs += f"\n- Error deleting {file_name}: {e}"
            return logs

        
        @files.clear(inputs=[files,processLogs,agentSelection],outputs=processLogs)
        def clear_files(files,logs,agentSelection):
            pdf_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "crews", agentSelection, "knowledge")
            shutil.rmtree(pdf_dir)
            return logs + "\n " + "- Files deleted to ask questions you need to upload files again"
        

        @submitBtn.click(inputs=[userInput,agentSelection,processLogs,agentConfig], outputs=[output, processLogs])
        def get_answer(userInput,agentSelection,processLogs,agentConfig):
            if not userInput:
                yield(None,"Please enter a query.") 
            if agentSelection == 'Select an agent':
                yield(None,"Please select an agent.") 
            accumulated_logs = processLogs

            crew = PdfCrew().crew()
            ragTool = RagTool()

            pdf_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "crews", "pdf_crew", "knowledge")

            for file in os.listdir(pdf_dir):
                pdf_path = os.path.join(pdf_dir, file)
                ragTool.add(source=pdf_path)
            

            if agentSelection == 'PdfExpert':
                for agent in crew.agents:
                    if hasattr(agent, "role") and agent.role.strip().lower() == "data_extractor":
                        data_extractor_agent = agent
                        break

                data_extractor_agent.tools.append(ragTool)

                if("Summarize Text" in agentConfig):
                    data_extractor_agent.tools.append(doc_to_summary_tool)
                
                accumulated_logs = accumulated_logs + '\n- Added RagTool to PdfExpert' 
                yield (None, accumulated_logs)

            accumulated_logs = accumulated_logs + '\n- Thinking on the answer...' 
            yield (None, accumulated_logs)

            response = crew.kickoff({"query": userInput})
            if response:
                accumulated_logs = accumulated_logs + '\n- Answer is ready' 

            yield (response, accumulated_logs)

    return demo 