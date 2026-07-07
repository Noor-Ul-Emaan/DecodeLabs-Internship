import os
import sys
import re
from pathlib import Path
import google.generativeai as genai
from rich.console import Console
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Rich Console
console = Console()

class CodeReviewer:
    def __init__(self):
        """Initialize the Code Reviewer with Gemini API."""
        # Get API key from environment variable
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            console.print("[red]ERROR: GOOGLE_API_KEY not found in environment variables![/red]")
            console.print("[yellow]Please create a .env file with: GOOGLE_API_KEY=your_api_key[/yellow]")
            sys.exit(1)
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # System instructions - hardcoded behavior constraints
        self.system_instructions = """
        You are an expert code reviewer and explainer. Your task is to analyze code and provide:
        
        1. A bug report with:
           - Syntax anomalies
           - Logical vulnerabilities
           - Performance bugs
           - Potential improvements
           
        2. Refactored code that is:
           - Corrected and compilable
           - Optimized
           - Well-documented
           
        FORMATTING REQUIREMENTS - STRICTLY ENFORCED:
        
        You MUST respond with EXACTLY two sections:
        
        ## BUG_REPORT
        - Only direct, concise bullet points
        - Detail syntax anomalies, logical vulnerabilities, performance bugs
        - No extra text or explanations outside bullet points
        
        ## REFACTORED_CODE
        - A single, valid Markdown-fenced code block
        - Must include the language identifier
        - Contains the corrected, compilable code
        - No extra text outside the code block
        
        WARNING: Failure to return both explicit section headers will cause the response to be rejected.
        """
        
        # Initialize model
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=self.system_instructions
        )
    
    def read_file(self, file_path: str) -> str:
        """Read and return the content of a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            return content
        except FileNotFoundError:
            console.print(f"[red]ERROR: File '{file_path}' not found![/red]")
            sys.exit(1)
        except Exception as e:
            console.print(f"[red]ERROR reading file: {e}[/red]")
            sys.exit(1)
    
    def get_language_from_extension(self, file_path: str) -> str:
        """Determine programming language from file extension."""
        extension = Path(file_path).suffix.lower()
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.go': 'go',
            '.rb': 'ruby',
            '.rs': 'rust',
            '.ts': 'typescript',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.xml': 'xml',
            '.sh': 'bash',
            '.sql': 'sql'
        }
        return language_map.get(extension, 'text')
    
    def validate_response(self, response_text: str) -> bool:
        """Validate that the response contains both required sections."""
        has_bug_report = '## BUG_REPORT' in response_text
        has_refactored_code = '## REFACTORED_CODE' in response_text
        
        if not has_bug_report:
            console.print("[red]WARNING: Missing '## BUG_REPORT' section in response![/red]")
        if not has_refactored_code:
            console.print("[red]WARNING: Missing '## REFACTORED_CODE' section in response![/red]")
        
        return has_bug_report and has_refactored_code
    
    def extract_code_block(self, text: str) -> str:
        """Extract code block from markdown text."""
        # Pattern to match code blocks with language identifier
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        
        if matches:
            # Return the content of the last code block (should be the refactored code)
            return matches[-1][1].strip()
        return None
    
    def review_code(self, file_path: str):
        """Main method to review code from a file."""
        # Phase 1: Input & Payload Capture
        console.print("\n[bold cyan]📁 INGESTING CODE FILE[/bold cyan]")
        console.print(f"File: [yellow]{file_path}[/yellow]")
        
        code_content = self.read_file(file_path)
        language = self.get_language_from_extension(file_path)
        
        # Display original code with syntax highlighting
        console.print("\n[bold yellow]📄 ORIGINAL CODE:[/bold yellow]")
        syntax = Syntax(code_content, language, theme="monokai", line_numbers=True)
        console.print(syntax)
        
        # Phase 2: Context Orchestration
        console.print("\n[bold cyan]🤖 ANALYZING CODE...[/bold cyan]")
        
        # Prepare prompt with code content
        prompt = f"""
        Analyze the following {language} code and provide a bug report and refactored version.
        
        Code: