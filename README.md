# Project Report: Multi-Agent Travel Planner
## Title: Multi-Agent Travel Planner

### Overview: 
This project is a conversational AI agent that functions as a "team" of travel specialists. A user can chat with it through a web interface to plan a trip by providing a destination, budget, and travel dates. The agent will dispatch specialist agents to research diverse travel options (flights, trains, and buses) and various accommodation choices (hotels, Airbnbs, etc.) in parallel. It will then consolidate all these options into a single, comprehensive list—complete with links where the user can book manually. The agent uses persistent memory to remember the conversation, allowing the user to ask follow-up questions to refine the plan.

### Reason for picking up this project This project is designed to synthesize and demonstrate mastery of all the major topics covered in this course:

#### LangGraph (State, Nodes, Graph): 
The entire application is built as a stateful graph using StateGraph. It uses a custom TypedDict state (TravelAgentState) to manage messages, user preferences, and research results.

#### Tool Calling & RAG: 
The agent uses tools (e.g., search_flights, search_trains, search_airbnbs) to perform "Retrieval-Augmented Generation" (RAG). Instead of just retrieving from a static database, it fetches live data (options and links) to answer the user's request.

#### Persistent Memory (Module 2): 
The graph is compiled with a SqliteSaver checkpointer. This gives the agent persistent, long-term memory, allowing a user to close the chat, come back later, and have the agent remember their thread_id and all previous conversation details.

#### Human-in-the-Loop (Module 3): 
The agent operates in a continuous loop with the user. It researches, presents its findings (the travel and accommodation links), and then waits for the user's next request. The user can then provide feedback (e.g., "Those flights are too expensive, find another option"), which starts a new research cycle. This uses the core concepts of breakpoints.ipynb (pausing for input) and edit-state-human-feedback.ipynb (acting on new feedback) in a natural conversational flow.

#### Multi-Agent (Module 4): 
This is the core of the capstone.

#### Sub-Graphs (Module 4): 
A travel_agent (handling flights, trains, and buses) and an accommodation_agent (handling hotels and Airbnbs) are built as their own compiled graphs.

#### Parallelization (Module 4): 
The main graph's "planner" node runs these two specialist sub-graphs at the same time, as their tasks are independent.

#### Map-Reduce (Module 4):
The main graph "maps" the research tasks to these specialist agents and then "reduces" their separate findings into a single, unified plan presented to the user.

#### Deployment (Module 1): 
The final agent will be served as an API using langgraph dev and accessed via a simple web interface, as shown in the final module.

### Plan I plan to execute these steps to complete my project. As per the assignment instructions, I will commit after each step is complete.

#### [DONE](https://github.com/MAT496-Monsoon2025-SNU/AryanRastogi72-LLM-Capstone-Project-MAT496-SNU/blob/main/State_%26_Graph_With_PersistantMemory.ipynb) Step 1: Define State & Graph with Persistent Memory.

Define the main TravelAgentState (TypedDict) to hold messages, destination, dates, budget, and keys for all options (e.g., flight_options, train_options, accommodation_options).

Use Annotated with operator.add for all the new option lists to collect parallel results.

Compile the main StateGraph with a SqliteSaver checkpointer.

#### [TODO] Step 2: Implement Core Tools.

Create and bind Python tool functions: search_flights, search_trains, search_buses, search_hotels, and search_airbnbs.

These tools will return mock data, including a "link" key with a dummy URL (e.g., {"price": 80, "link": "https://example.com/trains"}).

#### [TODO] Step 3: Create Travel Agent Sub-Graph.

Build and compile a travel_agent sub-graph.

This agent will be given the tools search_flights, search_trains, and search_buses and will be responsible for finding all travel options.

#### [TODO] Step 4: Create Accommodation Agent Sub-Graph.

Build and compile an accommodation_agent sub-graph.

This agent will be given the tools search_hotels and search_airbnbs to find all lodging options.

#### [TODO] Step 5: Implement Map-Reduce Flow.

In the main graph, create a "planner" node.

Use a conditional edge with Send to call the travel_agent and accommodation_agent sub-graphs in parallel (this is the "map" step).

#### [TODO] Step 6: Implement Reduce & Chat Loop.

Create a "present_plan" node that waits for both sub-graphs to finish (the "reduce" step).

This node's job is to gather all the lists (e.g., state['flight_options'], state['hotel_options']) and format them into a single, clean message for the user, including the links for booking.

The main agent will present this plan and then flow to END, waiting for the user's next message (which will start a new, memory-enabled run).

#### [TODO] Step 7: Deploy & Build Web Interface.

Deploy the final compiled graph as an API using langgraph dev.

Create a simple Streamlit (or Flask) web app with a chat interface that connects to the agent's API using the langgraph_sdk.

#### [TODO] Step 8: Final Test.

Test the full end-to-end flow through the web interface to ensure memory and breakpoints work.

### Conclusion 

