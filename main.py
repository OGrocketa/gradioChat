from crew.crew import Testcrew
import gradio as gr


def get_agent_tools(agentName):
    if(agentName == 'PdfExpert'):
        return ["Summarize Text", "Tool2", "Tool3"]
    elif(agentName == 'Agent 2'):
        return ["Tool1", "Tool2"]
    else:
        return []


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
        return logs + "\n " + "- Files uploaded successfully you can ask questions now"
    
    @files.clear(inputs=[files,processLogs],outputs=processLogs)
    def upload_files(files,logs):
        return logs + "\n " + "- Files deleted to ask questions you need to upload files again"
    

    @submitBtn.click(inputs=userInput, outputs=output)
    def get_answer(userInput):
        crew = Testcrew().crew()
        response = crew.kickoff({"query": userInput})
        return response

demo.launch()