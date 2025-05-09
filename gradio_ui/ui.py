from crews import PdfCrew
from crews.pdf_crew import doc_to_summary_tool
from crewai_tools import RagTool
from .file_handling import handle_file_upload, handle_file_deletion, handle_files_clear
from .crew_data_fetch import discover_agent_tools, discover_available_crews
from .get_crew_response import get_crew_response
import gradio as gr
import os, shutil


def create_ui():
    with gr.Blocks() as demo:
        gr.Markdown("# CrewAI Demo")
        with gr.Row():
            with gr.Column(scale=1):
                agentSelection = gr.Dropdown(choices=discover_available_crews(), label="Select Crew", interactive=True, value=discover_available_crews()[0])
                agentConfig = gr.CheckboxGroup(label="Crew Additional Tools", interactive=True, choices=discover_agent_tools(discover_available_crews()[0]))
                files = gr.File(label="Upload Files", file_count="multiple", file_types=[".pdf"])
                userInput = gr.Textbox(lines=5, label="Enter your query")
                submitBtn = gr.Button("Submit")
                
        
            with gr.Column(scale=2):
                processLogs = gr.Textbox(lines=5, label="Logs", autoscroll=True, interactive=False)
                output = gr.Textbox(lines=5, label="Output Box")
                
        
        def update_agent_config(agent):
            return gr.update(choices=discover_agent_tools(agent))

        agentSelection.change(
            fn=update_agent_config, 
            inputs=agentSelection, 
            outputs=agentConfig
        )

        @files.upload(inputs=[files,processLogs,agentSelection],outputs=processLogs)
        def upload_files(files,logs,agentSelection):
            return handle_file_upload(files,logs,agentSelection)
        
        @files.delete(inputs=[processLogs,agentSelection], outputs=processLogs)
        def remove_file(deleted_data: gr.DeletedFileData, logs, agentSelection):
            return handle_file_deletion(deleted_data, logs, agentSelection)

        @files.clear(inputs=[processLogs,agentSelection],outputs=processLogs)
        def remove_all_files(logs,agentSelection):
            return handle_files_clear(logs,agentSelection)

        @submitBtn.click(inputs=[userInput,agentSelection,processLogs,agentConfig], outputs=[output, processLogs])
        def get_answer(userInput,agentSelection,processLogs,agentConfig):
            return get_crew_response(userInput,agentSelection,processLogs,agentConfig)

    return demo 