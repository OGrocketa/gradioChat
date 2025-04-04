import os
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode

source = "/Users/yaraslausedach/Code/gradioChat/crew/knowledge"
output_dir = "/Users/yaraslausedach/Code/gradioChat/crew/markdown_outputs"

os.makedirs(output_dir, exist_ok=True)

for filename in os.listdir(source):
    file_path = os.path.join(source, filename)
    if os.path.isdir(file_path):
        continue
    
    try:
        
        options = PdfPipelineOptions()
        options.generate_page_images = True
        
        converter = DocumentConverter(format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=options)
        })

        result = converter.convert(file_path)
        mdFile = result.document.export_to_markdown()

        base_name, _ = os.path.splitext(filename)
        output_file_path = os.path.join(output_dir, f"{base_name}.md")

        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write(mdFile)
        
        print(f"Written markdown file to {output_file_path}")
    except Exception as e:
        print(f"Error processing {filename}: {e}")
