# Project Report: AI Travel Planner

## Title: Persistent Multi-Agent Travel Planner

### Overview
This project is an advanced conversational AI agent designed to act as a "team" of travel specialists. A user interacts with the system (initially via CLI, later via a Web UI), providing trip details such as origin, destination, budget, dates, and the number of travellers. The system orchestrates a team of specialist agents—a **Travel Agent** (for flights) and a **Hotel Agent** (for accommodation)—to research live options in parallel.

Using the **Amadeus API** for flights and **Booking.com (via RapidAPI)** for hotels, the agents fetch real-time data including prices, ratings, and direct booking links. The system then consolidates these findings into a comprehensive, formatted itinerary that respects the user's budget and preferences. The entire application state is managed using **LangGraph**, featuring persistent memory to track the conversation and context.

**Disclaimer:** Please note that the flight and hotel data provided by this agent are for demonstration purposes. Due to the nature of the free/test API tiers used (Amadeus Test Environment and RapidAPI), the pricing and availability are not guaranteed to be 100% accurate or real-time and will likely differ from final booking prices.

### Reason for picking up this project
This project was selected to synthesise and demonstrate mastery of all the major advanced topics covered in the course:

#### LangGraph (State, Nodes, Graph)
The core architecture is built as a stateful graph using `StateGraph`, managing complex state transitions and data flow between multiple nodes using a custom `TypedDict` state (`TravelAgentState`).

#### Tool Calling & RAG
The agents use custom tools (`search_flight`, `search_hotel`) to perform retrieval-augmented generation by fetching live, structured data from external APIs (Amadeus & Booking.com) rather than relying on static knowledge.

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

#### [DONE] Step 1: Define State & Graph with Persistent Memory.
* Defined the `TravelAgentState` (`TypedDict`) to hold user inputs (`origin`, `destination`, `dates`, `budget`) and results lists.
* Implemented custom reducers (`replace_value` and `operator.add`) to safely manage state updates from parallel branches.
* Initialised `SqliteSaver` for persistent conversational memory.

#### [DONE] Step 2: Implement Core Tools (API Integration).
* Built `search_flight`: Integrated with **Amadeus API** to fetch real flight offers. Added logic to generate dynamic **Skyscanner booking links** for better usability.
* Built `search_hotel`: Integrated with **Booking.com (via RapidAPI)** to fetch real hotel data, including prices, ratings, and deep links.
* Implemented helper functions like `get_iata_code` and `get_destination_id` to ensure accurate API queries.

#### [DONE] Step 3: Create "Travel Agent" Sub-Graph.
* Designed a dedicated sub-graph for flight research.
* Configured the agent to search for both **outbound** and **return** flights.
* Implemented a parser node to clean raw API data before passing it back to the main state.

#### [DONE] Step 4: Create "Accommodation Agent" Sub-Graph.
* Designed a dedicated sub-graph for hotel research.
* Configured the agent to search for hotels based on check-in/out dates and budget.
* Implemented a parser node to extract key details (price, rating, stars) from the API response.

#### [DONE] Step 5: Implement Map-Reduce Orchestrator.
* Built the **Main Graph** to coordinate the workflow.
* **Intake Node:** Clears previous results to ensure fresh searches.
* **Routing:** Implemented logic to "Map" the task to both specialist sub-graphs to run in **parallel**.
* **Reduce:** Implemented a `present_plan_node` that waits for both agents to finish, aggregates their results, calculates total costs, and formats a final Markdown itinerary.

#### [TODO] Step 6: Deploy & Build Web Interface.
* Deploy the final compiled graph as an API using `langgraph dev`.
* Create a simple **Streamlit** web app with a chat interface that connects to the agent's API using the `langgraph_sdk`.

#### [TODO] Step 7: Final Test.
* Test the full end-to-end flow through the web interface to ensure memory, tool calling, and parallel execution work as expected.

### Conclusion
I have planned to achieve a fully functional, multi-agent application that directly revises all modules from the course. This plan is ambitious but provides a clear path to demonstrating a practical understanding of LangGraph, from basic state management to complex, parallel multi-agent workflows with persistent memory and human oversight. Successful completion of this project will result in a portfolio-ready application that truly showcases the power of agentic AI development.
