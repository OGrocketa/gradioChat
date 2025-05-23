from .file_handling import handle_file_upload, handle_file_deletion, handle_files_clear
from .crew_data_fetch import discover_agent_tools, discover_available_crews, extract_variables_from_tasks
from .get_crew_response import get_crew_response
import gradio as gr
import os, shutil


def create_ui():
    with gr.Blocks() as demo:
        gr.Markdown("# CrewAI Demo")
        uploadedFiles = gr.BrowserState([])
        

        with gr.Row():
            with gr.Column(scale=1):
                agentSelection = gr.Dropdown(choices=discover_available_crews(), label="Select Agent", interactive=True, value=discover_available_crews()[0])
                agentConfig = gr.CheckboxGroup(label="Agent Config", interactive=True, choices=discover_agent_tools(discover_available_crews()[0]))
                files = gr.File(label="Upload Files", file_count="multiple", file_types=[".pdf"])
                preloadedFiles = gr.File(label="Preloaded Files", file_count="multiple")

                @gr.render(inputs=[agentSelection])
                def render_variable_inputs(agent):
                    variables = extract_variables_from_tasks(agent)
                    userInput = []
                    for var in variables:
                        textbox = gr.Textbox(label=var)
                        userInput.append(textbox)

                    submitBtn = gr.Button("Submit")
                    
                    @submitBtn.click(inputs=userInput + [agentSelection, processLogs, agentConfig], outputs=[output, processLogs])
                    def get_answer(*args):    
                        user_inputs = args[:-3]  # All but last 3 args are user inputs
                        selected_agent = args[-3]  # Second to last is agent selection
                        current_logs = args[-2]  # Second to last is process logs
                        selected_config = args[-1]  # Last is agent config
                        
                        response_generator = get_crew_response(*user_inputs, selected_agent, current_logs, selected_config)
                        
                        final_response = None
                        current_logs = current_logs or ""
                        
                        for response, logs in response_generator:
                            if response is not None:
                                final_response = response
                            if logs is not None:
                                current_logs = logs
                                yield None, current_logs  
                        
                        yield final_response, current_logs

            with gr.Column(scale=2):
                processLogs = gr.Textbox(lines=5, label="Logs", autoscroll=True, interactive=False)
                output = gr.Textbox(lines=5, label="Output Box")
                
        
        def update_agent_config(agent):
            return gr.update(choices=discover_agent_tools(agent))

        def relocate_files(agent,files,logs,uploadedFiles):
            for file in uploadedFiles:
                if os.path.exists(file):
                    os.remove(file)
            uploadedFiles.clear()
            if files != None:
                upload_files(files, logs, agent,uploadedFiles)

            return gr.update(choices=discover_agent_tools(agent), value=[]), uploadedFiles

        agentSelection.change(
            fn=relocate_files, 
            inputs=[agentSelection,files,processLogs,uploadedFiles], 
            outputs=[agentConfig,uploadedFiles]
        )

        @files.upload(inputs=[files,processLogs,agentSelection,uploadedFiles],outputs=[processLogs,uploadedFiles])
        def upload_files(files,logs,agentSelection,uploadedFiles):
            response = handle_file_upload(files,logs,agentSelection,uploadedFiles)
            return response
        
        @files.delete(inputs=[processLogs,agentSelection,uploadedFiles], outputs=[processLogs,uploadedFiles])
        def remove_file(deleted_data: gr.DeletedFileData, logs, agentSelection, uploadedFiles):
            response = handle_file_deletion(deleted_data, logs, agentSelection, uploadedFiles)
            return response

        @files.clear(inputs=[processLogs,agentSelection,uploadedFiles],outputs=[processLogs,uploadedFiles])
        def remove_all_files(logs,agentSelection,uploadedFiles):
            return handle_files_clear(logs,agentSelection,uploadedFiles)

    return demo 