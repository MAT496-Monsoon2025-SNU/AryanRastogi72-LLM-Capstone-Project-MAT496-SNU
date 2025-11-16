# Project Report: Multi-Agent Travel Planner
## Title: Persistent Multi-Agent Travel Planner

### Overview: 
This project is a conversational AI agent that functions as a "team" of travel specialists. A user can chat with it through a web interface to plan a trip. The agent will remember the user's preferences (like destination, budget, and dates) across sessions using persistent memory. When asked for a plan, it will dispatch specialist agents to research flights and hotels in parallel. Finally, it will present a combined plan and pause to ask for the user's final approval before "booking" the trip.

### Reason for picking up this project This project is designed to synthesize and demonstrate mastery of all the major topics covered in this course:

#### LangGraph (State, Nodes, Graph): 
The entire application is built as a stateful graph using StateGraph. It uses a custom TypedDict state (TravelAgentState) to manage messages, user preferences, and research results.

#### Tool Calling & RAG: 
The agent uses tools (e.g., TavilySearchResults or mock functions) to perform "Retrieval-Augmented Generation" (RAG). Instead of just retrieving from a static database, it fetches live data (flights, hotels) to answer the user's request.

#### Persistent Memory (Module 2): 
The graph is compiled with a SqliteSaver checkpointer. This gives the agent persistent, long-term memory, allowing a user to close the chat, come back later, and have the agent remember their thread_id and all previous conversation details.

#### Human-in-the-Loop (Module 3): 
The agent uses a dynamic breakpoint (NodeInterrupt) to automatically pause the graph only when the book_trip tool is about to be called. This allows the user to review the plan and give explicit approval. It also supports state editing, as the user can provide corrections (e.g., "No, use the other hotel") before resuming.

#### Multi-Agent (Module 4): 
This is the core of the capstone. The project is a multi-agent system:

#### Sub-Graphs (Module 4): 
A flight_agent and a hotel_agent are built as their own compiled graphs.

#### Parallelization (Module 4): 
The main graph's "planner" node runs these two specialist sub-graphs at the same time, as their tasks are independent.

#### Map-Reduce (Module 4):
The main graph "maps" the research tasks to these specialist agents and then "reduces" their separate findings into a single, unified plan presented to the user.

#### Deployment (Module 1): 
The final agent will be served as an API using langgraph dev and accessed via a simple web interface, as shown in the final module.

### Plan I plan to execute these steps to complete my project. As per the assignment instructions, I will commit after each step is complete.

#### [TODO] Step 1: Define State & Graph with Persistent Memory.

Define the main TravelAgentState (TypedDict) to hold messages, destination, dates, flight_options, hotel_options, etc..

Compile the main StateGraph with a SqliteSaver checkpointer.

#### [TODO] Step 2: Implement Core Tools.

Create and bind three Python functions as tools: search_flights, Google Hotels, and book_trip. These will return mock data for the project.

#### [TODO] Step 3: Create Flight Agent Sub-Graph.

Build and compile a simple flight_agent graph whose only job is to call the search_flights tool.

#### [TODO] Step 4: Create Hotel Agent Sub-Graph.

Build and compile a simple hotel_agent graph whose only job is to call the Google Hotels tool.

#### [TODO] Step 5: Implement Map-Reduce Flow.

In the main graph, create a "planner" node.

Use a conditional edge with Send to call the flight_agent and hotel_agent sub-graphs in parallel (this is the "map" step).

#### [TODO] Step 6: Implement Reduce & Breakpoint Logic.

Create a "present_plan" node that waits for both sub-graphs to finish (the "reduce" step) and formats their results into a plan.

Modify the main agent node to check if the LLM's intent is to book_trip. If it is, raise NodeInterrupt to pause the graph for human approval.

#### [TODO] Step 7: Deploy & Build Web Interface.

Deploy the final compiled graph as an API using langgraph dev.

Create a simple Streamlit (or Flask) web app with a chat interface that connects to the agent's API using the langgraph_sdk.

#### [TODO] Step 8: Final Test.

Test the full end-to-end flow through the web interface to ensure memory and breakpoints work.

### Conclusion 
I have planned to achieve a fully functional, multi-agent application that directly revises all modules from the course. This plan is ambitious but provides a clear path to demonstrating a practical understanding of LangGraph, from basic state management to complex, parallel multi-agent workflows with persistent memory and human oversight. Successful completion of this project will result in a portfolio-ready application that truly showcases the power of agentic AI development.
Conclusion I have planned to achieve a fully functional, multi-agent application that directly revises all modules from the course. This plan is ambitious but provides a clear path to demonstrating a practical understanding of LangGraph, from basic state management to complex, parallel multi-agent workflows with persistent memory and human oversight. Successful completion of this project will result in a portfolio-ready application that truly showcases the power of agentic AI development.
