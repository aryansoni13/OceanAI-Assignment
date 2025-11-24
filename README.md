# Autonomous QA Agent

An intelligent agent that generates Test Cases and Selenium Scripts from project documentation and HTML.

## Features

- **Knowledge Base Ingestion**: Uploads MD, TXT, JSON, and HTML files to build a vector database.
- **Test Case Generation**: Generates comprehensive test plans grounded in the provided documentation.
- **Selenium Script Generation**: Converts test cases into executable Python Selenium scripts using the actual HTML structure.

## Setup

1. **Prerequisites**

   - Python 3.9+
   - Google API Key (Get it from [Google AI Studio](https://makersuite.google.com/app/apikey))

2. **Installation**

   ```bash
   cd qa_agent
   pip install -r requirements.txt
   ```

3. **Environment Configuration**

   Create a `.env` file in the project root:

   ```bash
   cp .env.example .env
   ```

   Then edit `.env` and add your API key:

   ```
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

   **For deployment**: Make sure to set the `GOOGLE_API_KEY` environment variable in your deployment platform (Streamlit Cloud, Heroku, etc.)

4. **Running the Application**
   ```bash
   streamlit run app.py
   ```

## Usage

1. **Build Knowledge Base**

   - Go to the "Knowledge Base" tab.
   - Upload your support documents (e.g., `product_specs.md`, `ui_ux_guide.txt`) and the target `checkout.html`.
   - Click "Build Knowledge Base".

2. **Generate Test Cases**

   - Go to the "Test Cases" tab.
   - Enter a feature to test (e.g., "Discount Code").
   - Click "Generate Test Cases".

3. **Generate Scripts**
   - Copy a generated test case.
   - Go to the "Selenium Scripts" tab.
   - Paste the test case.
   - Click "Generate Script".

## Project Structure

- `app.py`: Main Streamlit application.
- `backend/`: Core logic for ingestion and RAG agents.
- `assets/`: Sample files for testing.
