import os
import shutil


class FileController:
    def handle_file_upload(self, new_files, logs, selected_agent, uploaded_files):
        pdf_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "crews", selected_agent, "knowledge"
        )

        if not os.path.exists(pdf_dir):
            os.makedirs(pdf_dir)

        for uploaded_file in new_files:
            file_name = os.path.basename(uploaded_file.name)
            destination = os.path.join(pdf_dir, file_name)
            shutil.copy(uploaded_file.name, destination)
            uploaded_files.extend([destination])

        return logs + "\n- Files uploaded, you can ask questions", uploaded_files


    def handle_file_deletion(self, deleted_data, logs, uploaded_files):
        file_name = os.path.basename(deleted_data.file.path)
        try:
            file_to_delete = None
            for file_path in uploaded_files:
                if os.path.basename(file_path) == file_name:
                    file_to_delete = file_path
                    break

            if file_to_delete and os.path.exists(file_to_delete):
                os.remove(file_to_delete)
                logs += f"\n- {file_name} deleted from directory."
                uploaded_files.remove(file_to_delete)
            else:
                logs += f"\n- {file_name} not found in directory."

        except Exception as e:
            logs += f"\n- Error deleting {file_name}: {e}"

        return logs, uploaded_files


    def handle_files_clear(self, logs, uploaded_files):
        for file in uploaded_files:
            if os.path.exists(file):
                os.remove(file)

        uploaded_files.clear()
        return (
            logs
            + "\n "
            + "- Files deleted to ask questions you need to upload files again",
            uploaded_files,
        )
