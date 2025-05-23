import os
import shutil

def handle_file_upload(uploaded_files, logs, selected_agent, uploadedFiles):
    pdf_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "crews", selected_agent, "knowledge")

    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)
    
    for uploaded_file in uploaded_files:
        file_name = os.path.basename(uploaded_file.name)
        destination = os.path.join(pdf_dir, file_name)
        shutil.copy(uploaded_file.name, destination)
        uploadedFiles.extend([destination])

    return logs + "\n- Files uploaded, you can ask questions", uploadedFiles

def handle_file_deletion(deleted_data, logs, agentSelection, uploadedFiles):
    pdf_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "crews", agentSelection, "knowledge")
    file_name = os.path.basename(deleted_data.file.path)
    file_path = os.path.join(pdf_dir, file_name)
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logs += f"\n- {file_name} deleted from directory."
            uploadedFiles.remove(file_path)
            
        else:
            logs += f"\n- {file_name} not found in directory."
    except Exception as e:
        logs += f"\n- Error deleting {file_name}: {e}"

    return logs,uploadedFiles

def handle_files_clear(logs, agentSelection, uploadedFiles):
    for file in uploadedFiles:
        if os.path.exists(file):
            os.remove(file)
    uploadedFiles.clear()
    return logs + "\n " + "- Files deleted to ask questions you need to upload files again", uploadedFiles
