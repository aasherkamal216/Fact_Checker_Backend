# FactFlow AI 🌊

**FactFlow** is a real-time, AI-powered workflow that takes a user's claim, researches it using multiple web sources, and provides a concise, fact-checked verdict with a shareable social media post. This project was developed for the AiForAll Fact-Checker Agent Hackathon.


<video src="public/fact-checker-demo.mp4" controls width="600"></video>

---

## ✨ Key Features

*   **End-to-End Automation:** From a single claim to a shareable post in seconds.
*   **Real-Time Streaming UI:** The interface provides live updates as the agent analyzes the claim, searches the web, and forms a conclusion.
*   **Modern, Responsive UI:** A clean, mobile-friendly interface built with vanilla HTML/CSS/JS for a lightweight and fast user experience.

---

## 🛠️ Technology Stack

| Component         | Technology/Library                                                                                                                              |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| **Backend Agent** | [**LangGraph**](https://langchain-ai.github.io/langgraph/): For creating a robust, stateful, and cyclic multi-step agent workflow.                |
| **LLMs**          | **Google Gemini 2.5 Flash model**: Used for its reasoning, large context window, and excellent structured output capabilities. |
| **Search Tool**   | [**Tavily Search API**](https://tavily.com/): An AI-native search engine that provides clean, summarized results ideal for agent consumption.      |
| **API Server**    | [**FastAPI**](https://fastapi.tiangolo.com/): For creating a high-performance, asynchronous API that supports Server-Sent Events (SSE) for streaming. |
| **Frontend**      | **HTML5, CSS3, JavaScript (Vanilla)**: For a lightweight, dependency-free, and modern user interface.                                           |
| **Deployment**    | [**Hugging Face Spaces (Docker)**](https://huggingface.co/docs/hub/spaces): For easy, reproducible, and shareable deployment.                     |

---

## 📊 Workflow Diagram

The logic is structured as a graph, where each node represents a specific task. This modular design allows for clear separation of concerns and efficient execution.

![Diagram](/public/hackathon_project.png)