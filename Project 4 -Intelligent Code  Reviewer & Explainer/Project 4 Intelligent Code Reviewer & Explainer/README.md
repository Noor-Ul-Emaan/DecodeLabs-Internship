# Intelligent Code Reviewer & Explainer

## Project 4: Optional Mastery Phase

### Overview
This project is an AI-powered code reviewer that analyzes code files, identifies bugs, and explains code in plain language. It uses Google's Gemini API with strict system instructions to enforce structured outputs.

### Features
- **File Ingestion**: Reads code files (.py, .js, .java) as string variables
- **AI Analysis**: Uses Gemini API with hardcoded system instructions
- **Structured Output**: Enforces `## BUG_REPORT` and `## REFACTORED_CODE` sections
- **Syntax Highlighting**: Renders code with color-coded syntax in the terminal
- **Validation**: Rejects malformed responses that don't meet formatting requirements

### Project Structure