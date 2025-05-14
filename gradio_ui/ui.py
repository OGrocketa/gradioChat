from .file_handling import handle_file_upload, handle_file_deletion, handle_files_clear
from .crew_data_fetch import discover_agent_tools, discover_available_crews, extract_variables_from_tasks
from .get_crew_response import get_crew_response
import gradio as gr
import os, shutil


def create_ui():
    with gr.Blocks() as demo:
        gr.Markdown("# CrewAI Demo")
        with gr.Row():
            with gr.Column(scale=1):
                agentSelection = gr.Dropdown(choices=discover_available_crews(), label="Select Agent", interactive=True, value=discover_available_crews()[0])
                agentConfig = gr.CheckboxGroup(label="Agent Config", interactive=True, choices=discover_agent_tools(discover_available_crews()[0]))
                files = gr.File(label="Upload Files", file_count="multiple", file_types=[".pdf"])
                
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
                        # Extract values from args
                        user_inputs = args[:-3]  # All but last 3 args are user inputs
                        selected_agent = args[-3]  # Second to last is agent selection
                        current_logs = args[-2]  # Second to last is process logs
                        selected_config = args[-1]  # Last is agent config
                        
                        response_generator = get_crew_response(*user_inputs, selected_agent, current_logs, selected_config)
                        
                        final_response = None
                        final_logs = current_logs
                        
                        for response, logs in response_generator:
                            if response is not None:
                                final_response = response
                            if logs is not None:
                                final_logs = logs
                        
                        return final_response, final_logs

            with gr.Column(scale=2):
                processLogs = gr.Textbox(lines=5, label="Logs", autoscroll=True, interactive=False)
                output = gr.Textbox(lines=5, label="Output Box")
                
        
        def update_agent_config(agent):
            return gr.update(choices=discover_agent_tools(agent))

        def cleanup_knowledge_directories(agent,files,logs):
            for crew in os.listdir(os.path.join(os.path.dirname(os.path.dirname(__file__)),'crews')):
                if os.path.exists(os.path.join(os.path.dirname(os.path.dirname(__file__)),'crews',crew,'knowledge')):
                    shutil.rmtree(os.path.join(os.path.dirname(os.path.dirname(__file__)),'crews',crew,'knowledge'))
            if files != None:
                upload_files(files, logs, agent)

            return update_agent_config(agent)

        agentSelection.change(
            fn=cleanup_knowledge_directories, 
            inputs=[agentSelection,files,processLogs], 
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

    return demo 