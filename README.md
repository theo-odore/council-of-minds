# Council of Philosophers

Welcome to the **Council of Philosophers**, a unique chat application that allows you to preside over a debate between some of history's greatest minds. 

## Overview

This project simulates a "council" where you, acting as the Chairman, can present queries or topics. A group of AI-powered philosopher personas—Socrates, Kafka, Dostoevsky, Nietzsche, and Chekhov—will respond to your prompts and to each other, maintaining their distinct philosophical viewpoints and personalities.

The application uses a Python Flask backend to interface with a local **Ollama** instance, allowing you to run powerful LLMs (like Llama 3) locally and privately.

## Features

-   **Distinct Personas**: 5 pre-configured philosophers with unique system prompts and specific models:
    -   **Socrates** (`mistral`): Annoying, questioning, brief.
    -   **Kafka** (`qwen`): Pessimistic, weird, murmuring.
    -   **Dostoevsky** (`phi`): Dramatic, emotional, intense.
    -   **Nietzsche** (`llama3.2`): Arrogant, punchy, mocking "herd mentality".
    -   **Chekhov** (`gemma`): Dry, clinical, ironic.
-   **Dynamic Turn-Taking**: The system randomly selects the next speaker (preventing the same person from speaking twice in a row) to simulate a natural flow of conversation.
-   **Session Management**: Create multiple chat sessions to explore different topics.
-   **Model Configuration**: Configure which LLM model each philosopher uses individually.
-   **Immersive UI**: A dark, atmospheric interface designed to feel like a council chamber.

## Prerequisites

Before running the application, ensure you have the following mapped out:

1.  **Python 3.8+** installed.
2.  **[Ollama](https://ollama.com/)** installed and running.
3.  **Pull the required models**:
    ```bash
    ollama pull llama3.2
    ollama pull mistral
    ollama pull qwen
    ollama pull phi
    ollama pull gemma
    ```

## Installation

1.  **Clone the repository** (if applicable) or navigate to the project directory.

2.  **Create a virtual environment** (optional but recommended):
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install Ollama Model**:
    Check `requirements.txt` for the recommended model, or run:
    ```bash
    ollama pull llama3.2:latest
    ```

## Usage

1.  **Start Ollama**:
    Ensure the Ollama service is running in the background.
    ```bash
    ollama serve
    ```

2.  **Run the Server**:
    ```bash
    python server.py
    ```
    You should see output indicating the server is running on `http://localhost:5000`.

3.  **Open the Application**:
    Open your web browser and navigate to:
    [http://localhost:5000](http://localhost:5000)

4.  **Start a Debate**:
    -   Type your query in the input box at the bottom (e.g., "What is the meaning of life?").
    -   Click "Speak".
    -   Watch as the philosophers respond to you and each other.

## Configuration

To change the model used by a specific philosopher:
1.  Click the **Settings (⚙️)** icon in the UI.
2.  Find the philosopher you wish to update.
3.  Enter the name of the model you have installed in Ollama (e.g., `mistral`, `gemma`, `llama3`).
4.  Save changes.

## Project Structure

-   **`server.py`**: The Flask backend. Handles routing, session management, and communication with the Ollama API.
-   **`index.html`**: The main frontend structure.
-   **`style.css`**: Styling for the dark, atmospheric UI.
-   **`script.js`**: Frontend logic for handling chat updates, API calls, and UI interactions.
-   **`requirements.txt`**: Python dependencies.

## Troubleshooting

-   **Connection Refused**: Make sure Ollama is running (`ollama serve`) and listening on port 11434.
-   **Model Not Found**: If a philosopher fails to respond, ensure the model configured for them (default `llama3.2:latest`) is actually pulled in your Ollama instance (`ollama list`).
