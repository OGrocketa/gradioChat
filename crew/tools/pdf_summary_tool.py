from crewai.tools import tool

@tool("PdfSummaryTool")
def pdf_summary_tool(question: str) -> str:
    """This tool helps with pdf summarization. Converts pdf to text and extract the necessary chunks"""
    
    return "Result from your custom tool"
