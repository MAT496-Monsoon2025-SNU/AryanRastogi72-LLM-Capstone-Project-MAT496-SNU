# Project Report: Travel Planner(Video Link Implemented in Step 8)

## Title: AI Travel Planner

### Overview
This project is an advanced conversational AI agent designed to act as a "team" of travel specialists. A user interacts with the system, providing trip details such as origin, destination, budget, dates, and the number of travellers. The system orchestrates a team of specialist agents—a **Travel Agent** (for flights) and a **Hotel Agent** (for accommodation)—to research live options in parallel.

Using the **Amadeus API** for flights and hotels, the agents fetch real-time data including prices, ratings, and direct booking links. The system then consolidates these findings into a comprehensive, formatted itinerary that respects the user's budget and preferences. The entire application state is managed using **LangGraph**, featuring persistent memory to track the conversation and context.

**Disclaimer:** Please note that the flight and hotel data provided by this agent are for demonstration purposes. Due to the nature of the free/test API tiers used (Amadeus Test Environment), pricing and availability are not guaranteed to be 100% accurate or real-time and may differ from final booking prices.

### Reason for picking up this project
This project was selected to synthesise and demonstrate mastery of all the major advanced topics covered in the course:

#### LangGraph (State, Nodes, Graph)
The core architecture is built as a stateful graph using `StateGraph`, managing complex state transitions and data flow between multiple nodes using a custom `TypedDict` state (`TravelAgentState`).

#### Tool Calling & RAG
The agents use custom tools (`search_flight`, `search_hotel`) to perform retrieval-augmented generation by fetching live, structured data from external APIs (Amadeus) rather than relying on static knowledge.

#### Persistent Memory (Module 2)
The graph utilises a `SqliteSaver` checkpointer to provide persistent, long-term memory. This allows the agent to maintain context across multiple interactions and even resume sessions after interruptions.

#### Human-in-the-Loop (Module 3)
The agent operates in a continuous conversational loop. It presents findings and then waits for the user's next message (state update). This allows the user to provide feedback (e.g., "Too expensive, find cheaper hotels"), effectively keeping the human in the loop to refine the search results.

#### Multi-Agent (Module 4)
This is the core of the capstone. The project implements a multi-agent system:
* **Sub-Graphs:** Specialised agents (Travel & Hotel) are built as their own independent, compiled sub-graphs.
* **Parallelisation:** The main graph orchestrator executes these sub-graphs simultaneously to reduce latency.
* **Map-Reduce:** The system "maps" the research task to the specialists and "reduces" their independent findings into a single, cohesive final plan.

#### Deployment (Module 1)
The final agent is designed to be served as an API using `langgraph dev` and accessed via a simple web interface (Streamlit).

### Plan
I plan to execute these steps to complete my project. As per the assignment instructions, I will commit after each step is complete.

#### [DONE] [Step 1: Define State & Graph with Persistent Memory.](https://github.com/MAT496-Monsoon2025-SNU/AryanRastogi72-LLM-Capstone-Project-MAT496-SNU/blob/main/State_%26_Graph_With_PersistantMemory.ipynb)
* Defined the `TravelAgentState` (`TypedDict`) to hold user inputs (`origin`, `destination`, `dates`, `budget`) and results lists.
* Implemented custom reducers (`replace_value` and `operator.add`) to manage state updates from parallel branches safely.
* Initialised `SqliteSaver` for persistent conversational memory.
* **Note:** At this stage, the graph was tested using **mock data** to ensure state persistence worked before integrating real APIs.

#### [DONE] [Step 2: Implement Core Tools (Mock Data).](https://github.com/MAT496-Monsoon2025-SNU/AryanRastogi72-LLM-Capstone-Project-MAT496-SNU/blob/main/Core_Tools.ipynb)
* Created placeholder tools (`search_flight`, `search_hotel`) returning **hardcoded mock data**.
* Real APIs were **not yet implemented**. This allowed me to verify the tool-calling logic and agent loop in isolation without hitting API limits or connectivity issues.

#### [DONE] [Step 3: Create "Travel Agent" Sub-Graph (Mock Data).](https://github.com/MAT496-Monsoon2025-SNU/AryanRastogi72-LLM-Capstone-Project-MAT496-SNU/blob/main/Travel_Sub_Graph.ipynb)
* Built the dedicated `travel_agent` sub-graph specifically for handling flight queries.
* Implemented a parser node to clean the tool outputs.
* **Note:** This agent was initially built and tested using the **mock flight tools** to verify the sub-graph structure and data parsing logic.

#### [DONE] [Step 4: Create "Accommodation Agent" Sub-Graph (Mock Data).](https://github.com/MAT496-Monsoon2025-SNU/AryanRastogi72-LLM-Capstone-Project-MAT496-SNU/blob/main/Accomadation_Sub_Graph.ipynb)
* Built the dedicated `accommodation_agent` sub-graph for handling hotel queries.
* **Note:** Similar to the travel agent, this was first implemented using **mock hotel tools** to ensure the parallel execution logic would work correctly without external dependencies.

#### [DONE] Step 5: [Implement Map-Reduce Orchestrator (Mock Data).](https://github.com/MAT496-Monsoon2025-SNU/AryanRastogi72-LLM-Capstone-Project-MAT496-SNU/blob/main/Map_Reduce.ipynb)
* Built the **Main Graph** to coordinate the workflow, including Intake, Planning, and Routing.
* Implemented the "Map-Reduce" logic to dispatch tasks to both sub-graphs in parallel and aggregate the results.
* **Verified Logic:** Successfully tested the entire multi-agent flow using **hardcoded values** to ensure the parallel execution and state aggregation worked correctly before moving to production data.

#### [DONE] [Step 6: Integrate Real APIs (Amadeus).](https://github.com/MAT496-Monsoon2025-SNU/AryanRastogi72-LLM-Capstone-Project-MAT496-SNU/blob/main/API_Implementations.ipynb)
* **Upgraded Tools:** Replaced the mock/hardcoded tools from Steps 2-5 with live API integrations.
* Integrated **Amadeus API** for flight search, including dynamic Skyscanner link generation.
* Integrated **Amadeus API** for hotel search to get real-time pricing and details.
* Validated that the agents now fetch and process real-world data instead of the initial mock data.

#### [DONE] [Step 7: Deploy & Build Web Interface.](https://github.com/MAT496-Monsoon2025-SNU/AryanRastogi72-LLM-Capstone-Project-MAT496-SNU/blob/main/TravelPlannerWebAPP.py)
* Deploy the final compiled graph as an API using `langgraph dev`.
* Create a simple **Streamlit** web app with a chat interface that connects to the agent's API using the `langgraph_sdk`.

#### [DONE] [Step 8: Final Video Walkthrough.](https://drive.google.com/file/d/1lClsOZuoNLCQWE7WR8_b6LKFLl0VfP4F/view?usp=drive_link)
* Record a comprehensive video walkthrough demonstrating the fully functional Travel Planner via the Streamlit web interface.

### Conclusion
I have planned to achieve a fully functional, multi-agent application that directly revises all modules from the course. This plan is ambitious but provides a clear path to demonstrating a practical understanding of LangGraph, from basic state management to complex, parallel multi-agent workflows with persistent memory and human oversight. Successful completion of this project will result in a portfolio-ready application that truly showcases the power of agentic AI development.
