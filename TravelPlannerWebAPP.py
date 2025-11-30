# 1. Setting up Enviroment and Loading API Keys
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import operator
import sqlite3
import json
import os
import uuid
from typing import List, Annotated, TypedDict
from datetime import datetime, date, timedelta
from langchain_core.messages import AnyMessage, AIMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langgraph.types import Send
from langgraph.checkpoint.sqlite import SqliteSaver
from amadeus import Client, ResponseError


# 2. Streamlit Page Configuration

st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="✈️",
    layout="wide"
)

st.title("✈️ AI Travel Planner")
st.markdown("Plan your perfect trip with AI-powered flight and hotel search")

# 3. AMADEUS API Setup

@st.cache_resource
def initialize_amadeus_client():
    try:
        client = Client(
            client_id=os.environ.get('AMADEUS_CLIENT_ID'),
            client_secret=os.environ.get('AMADEUS_CLIENT_SECRET')
        )
        return client
    except Exception:
        return None

amadeus_client = initialize_amadeus_client()

# 4. Helping Functions

def convert_city_to_airport_code(city_name):
    if amadeus_client is None:
        return city_name
    
    try:
        api_response = amadeus_client.reference_data.locations.get(
            keyword=city_name, 
            subType='CITY'
        )
        
        if api_response.data:
            airport_code = api_response.data[0]['iataCode']
            return airport_code
    except Exception:
        pass
    
    return city_name


def convert_currency(amount, from_currency, to_currency):
    """Convert currency using Frankfurter API (free, no API key needed)"""
    if from_currency == to_currency:
        return amount
    
    try:
        import requests
        url = f"https://api.frankfurter.app/latest?amount={amount}&from={from_currency}&to={to_currency}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if 'rates' in data and to_currency in data['rates']:
                return float(data['rates'][to_currency])
        
        return amount
    except Exception:
        return amount


def check_if_dates_are_valid(arrival_date_string, return_date_string):
    try:
        today = datetime.now().date()
        arrival_date = datetime.strptime(arrival_date_string, "%Y-%m-%d").date()
        return_date = datetime.strptime(return_date_string, "%Y-%m-%d").date()
        
        if arrival_date < today:
            error_message = "Arrival date cannot be in the past. Please select a future date."
            return False, error_message
        
        if return_date < today:
            error_message = "Return date cannot be in the past. Please select a future date."
            return False, error_message
        
        if return_date <= arrival_date:
            error_message = "Return date must be after arrival date."
            return False, error_message
        
        return True, "Dates are valid"
    except ValueError:
        error_message = "Invalid date format. Please use YYYY-MM-DD format."
        return False, error_message


def convert_json_string_to_list(json_string):
    try:
        data = json.loads(json_string)
        if isinstance(data, list):
            return data
        else:
            return []
    except Exception:
        return []


def replace_old_value_with_new(old_value, new_value):
    return new_value

# 5. Defining the State Schema

class TravelAgentState(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]
    origin: Annotated[str, replace_old_value_with_new]
    destination: Annotated[str, replace_old_value_with_new]
    currency: Annotated[str, replace_old_value_with_new]
    budget: Annotated[str, replace_old_value_with_new]
    num_people: Annotated[str, replace_old_value_with_new]
    arrival_date: Annotated[str, replace_old_value_with_new]
    stay_duration: Annotated[str, replace_old_value_with_new]
    return_date: Annotated[str, replace_old_value_with_new]
    flight_options: Annotated[List[dict], operator.add]
    hotel_options: Annotated[List[dict], operator.add]
    date_error: Annotated[str, replace_old_value_with_new]

# 6. Implementing The Core Tools

@tool
def search_flight(origin, destination, date, currency="USD"):
    """Search for flights between two cities on a specific date"""
    if amadeus_client is None:
        empty_result = []
        return json.dumps(empty_result)
    
    try:
        origin_airport_code = convert_city_to_airport_code(origin)
        destination_airport_code = convert_city_to_airport_code(destination)
        
        api_response = amadeus_client.shopping.flight_offers_search.get(
            originLocationCode=origin_airport_code,
            destinationLocationCode=destination_airport_code,
            departureDate=date,
            adults=1,
            currencyCode=currency,
            max=3
        )
        
        flight_results = []
        
        for flight in api_response.data[:3]:
            flight_price = float(flight['price']['total'])
            flight_currency = flight['price']['currency']

            if flight_currency != currency:
                flight_price = convert_currency(flight_price, flight_currency, currency)
                flight_currency = currency
            
            flight_segments = flight['itineraries'][0]['segments']
            airline_code = flight_segments[0]['carrierCode']
            
            departure_time_full = flight_segments[0]['departure']['at']
            arrival_time_full = flight_segments[-1]['arrival']['at']
            
            if 'T' in departure_time_full:
                departure_time = departure_time_full.split('T')[1][:5]
            else:
                departure_time = departure_time_full
            
            if 'T' in arrival_time_full:
                arrival_time = arrival_time_full.split('T')[1][:5]
            else:
                arrival_time = arrival_time_full
            
            try:
                date_object = datetime.strptime(date, "%Y-%m-%d")
                formatted_date = date_object.strftime("%y%m%d")
            except:
                formatted_date = date.replace("-", "")[2:]
            
            skyscanner_url = (
                f"https://www.skyscanner.com/transport/flights/"
                f"{origin_airport_code.lower()}/{destination_airport_code.lower()}/{formatted_date}/"
                f"?adults=1&cabinclass=economy&rtn=0"
            )
            
            flight_info = {
                "type": "flight",
                "airline": airline_code,
                "route": f"{origin_airport_code} -> {destination_airport_code}",
                "origin_code": origin_airport_code,
                "destination_code": destination_airport_code,
                "price": flight_price,
                "currency": flight_currency,
                "departure": departure_time,
                "arrival": arrival_time,
                "date": date,
                "link": skyscanner_url
            }
            
            flight_results.append(flight_info)
        
        return json.dumps(flight_results)
    
    except ResponseError:
        empty_result = []
        return json.dumps(empty_result)
    except Exception:
        empty_result = []
        return json.dumps(empty_result)

@tool
def search_hotel(location, checkin_date, checkout_date, currency="USD"):
    """Search for hotels in a city for specific dates"""
    if amadeus_client is None:
        empty_result = []
        return json.dumps(empty_result)
    
    try:
        city_airport_code = convert_city_to_airport_code(location)
        
        hotels_api_response = amadeus_client.reference_data.locations.hotels.by_city.get(
            cityCode=city_airport_code
        )
        
        if not hotels_api_response.data:
            location_url_encoded = location.replace(' ', '+')
            fallback_url = f"https://www.booking.com/searchresults.html?ss={location_url_encoded}&checkin={checkin_date}&checkout={checkout_date}&selected_currency={currency}"
            
            fallback_hotel = {
                "type": "hotel",
                "name": f"Hotels in {location}",
                "price": None,
                "currency": currency,
                "rating": 0,
                "rating_word": "",
                "stars": 0,
                "address": location,
                "distance_to_center": "Various",
                "link": fallback_url
            }
            
            return json.dumps([fallback_hotel])
        
        hotel_results = []
        hotel_id_list = []
        
        for hotel in hotels_api_response.data[:5]:
            hotel_id = hotel['hotelId']
            hotel_id_list.append(hotel_id)
        
        hotel_ids_joined = ','.join(hotel_id_list)
        
        try:
            offers_api_response = amadeus_client.shopping.hotel_offers_search.get(
                hotelIds=hotel_ids_joined,
                checkInDate=checkin_date,
                checkOutDate=checkout_date,
                adults=1,
                currency=currency
            )
            
            for hotel_offer in offers_api_response.data:
                hotel_name = hotel_offer['hotel']['name']
                hotel_id = hotel_offer['hotel']['hotelId']
                
                hotel_price = None
                hotel_currency = currency
                
                if hotel_offer.get('offers') and len(hotel_offer['offers']) > 0:
                    hotel_price = float(hotel_offer['offers'][0]['price']['total'])
                    api_currency = hotel_offer['offers'][0]['price']['currency']
                    
                    if api_currency != currency:
                        hotel_price = convert_currency(hotel_price, api_currency, currency)
                    
                    hotel_currency = currency
                
                hotel_name_url_encoded = hotel_name.replace(" ", "+")
                location_url_encoded = location.replace(' ', '+')
                booking_url = f"https://www.booking.com/searchresults.html?ss={hotel_name_url_encoded}+{location_url_encoded}&checkin={checkin_date}&checkout={checkout_date}&selected_currency={currency}"
                
                hotel_info = {
                    "type": "hotel",
                    "name": hotel_name,
                    "price": hotel_price,
                    "currency": hotel_currency,
                    "rating": 0,
                    "rating_word": "",
                    "stars": 0,
                    "address": location,
                    "distance_to_center": "N/A",
                    "link": booking_url
                }
                
                hotel_results.append(hotel_info)
        
        except ResponseError:
            for hotel in hotels_api_response.data[:5]:
                hotel_name = hotel.get('name', 'Unknown Hotel')
                hotel_name_url_encoded = hotel_name.replace(" ", "+")
                location_url_encoded = location.replace(' ', '+')
                booking_url = f"https://www.booking.com/searchresults.html?ss={hotel_name_url_encoded}+{location_url_encoded}&checkin={checkin_date}&checkout={checkout_date}&selected_currency={currency}"
                
                hotel_info = {
                    "type": "hotel",
                    "name": hotel_name,
                    "price": None,
                    "currency": currency,
                    "rating": 0,
                    "rating_word": "",
                    "stars": 0,
                    "address": location,
                    "distance_to_center": "N/A",
                    "link": booking_url
                }
                
                hotel_results.append(hotel_info)
        
        return json.dumps(hotel_results)
    
    except ResponseError:
        empty_result = []
        return json.dumps(empty_result)
    except Exception:
        empty_result = []
        return json.dumps(empty_result)

# 7. Making The Travel Specialist Sub-Graph

def travel_agent_node(state):
    user_currency = state.get('currency', 'USD')
    
    outbound_flight_result = search_flight.invoke({
        "origin": state['origin'],
        "destination": state['destination'],
        "date": state['arrival_date'],
        "currency": user_currency
    })
    
    return_flight_result = search_flight.invoke({
        "origin": state['destination'],
        "destination": state['origin'],
        "date": state['return_date'],
        "currency": user_currency
    })
    
    outbound_flights = convert_json_string_to_list(outbound_flight_result)
    return_flights = convert_json_string_to_list(return_flight_result)
    
    all_flights = outbound_flights + return_flights
    
    return {"flight_options": all_flights}


travel_graph_builder = StateGraph(TravelAgentState)
travel_graph_builder.add_node("travel_agent", travel_agent_node)
travel_graph_builder.add_edge(START, "travel_agent")
travel_graph_builder.add_edge("travel_agent", END)
travel_graph = travel_graph_builder.compile()

# 8. Making The Accommodation Specialist Sub-Graph

def hotel_agent_node(state):
    user_currency = state.get('currency', 'USD')
    
    hotel_search_result = search_hotel.invoke({
        "location": state['destination'],
        "checkin_date": state['arrival_date'],
        "checkout_date": state['return_date'],
        "currency": user_currency
    })
    
    hotels = convert_json_string_to_list(hotel_search_result)
    
    return {"hotel_options": hotels}


hotel_graph_builder = StateGraph(TravelAgentState)
hotel_graph_builder.add_node("hotel_agent", hotel_agent_node)
hotel_graph_builder.add_edge(START, "hotel_agent")
hotel_graph_builder.add_edge("hotel_agent", END)
hotel_graph = hotel_graph_builder.compile()

# 9. Building The Main Graph Nodes

def intake_node(state):
    return {
        "flight_options": [],
        "hotel_options": []
    }


def planner_node(state):
    dates_are_valid, validation_message = check_if_dates_are_valid(
        state['arrival_date'], 
        state['return_date']
    )
    
    if not dates_are_valid:
        return {"date_error": validation_message}
    
    return {}


def decide_next_step_after_planning(state):
    if state.get('date_error'):
        return "present_plan"
    return "specialists"


def route_to_both_agents(state):
    return [
        Send("travel_agent", state),
        Send("accommodation_agent", state)
    ]


def present_plan_node(state):
    if state.get('date_error'):
        error_message = state.get('date_error')
        error_text = f"**Error:** {error_message}"
        return {"messages": [AIMessage(content=error_text)]}
    
    return {"messages": [AIMessage(content="Success")]}

# 10. Building The Main Graph

@st.cache_resource
def build_workflow():
    database_connection = sqlite3.connect("travel_planner_streamlit.db", check_same_thread=False)
    memory_saver = SqliteSaver(conn=database_connection)
    
    workflow_builder = StateGraph(TravelAgentState)
    
    workflow_builder.add_node("intake", intake_node)
    workflow_builder.add_node("planner", planner_node)
    workflow_builder.add_node("specialists", lambda state: {})
    workflow_builder.add_node("present_plan", present_plan_node)
    workflow_builder.add_node("travel_agent", travel_graph)
    workflow_builder.add_node("accommodation_agent", hotel_graph)
    
    workflow_builder.add_edge(START, "intake")
    workflow_builder.add_edge("intake", "planner")
    workflow_builder.add_conditional_edges(
        "planner",
        decide_next_step_after_planning,
        {"specialists": "specialists", "present_plan": "present_plan"}
    )
    workflow_builder.add_conditional_edges(
        "specialists",
        route_to_both_agents,
        ["travel_agent", "accommodation_agent"]
    )
    workflow_builder.add_edge(["travel_agent", "accommodation_agent"], "present_plan")
    workflow_builder.add_edge("present_plan", END)
    
    return workflow_builder.compile(checkpointer=memory_saver)

app = build_workflow()

# 11. Building The Streamlit Interface

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    origin = st.text_input("Origin City", value="New York", placeholder="e.g., Mumbai, New York, London")
    arrival_date = st.date_input("Arrival Date", value=date.today(), min_value=date.today())
    currency = st.selectbox("Currency", ["USD", "EUR", "GBP", "INR", "JPY"], index=0)

with col2:
    destination = st.text_input("Destination City", value="Paris", placeholder="e.g., Paris, Delhi, Tokyo")
    return_date = st.date_input("Return Date", value=date.today() + timedelta(days=7), min_value=date.today())
    budget = st.number_input("Budget", value=2000, min_value=100, step=100)

num_people = st.number_input("Number of Travelers", value=1, min_value=1, max_value=10)

st.markdown("---")

if st.button("Search Flights & Hotels", type="primary", use_container_width=True):
    
    if not origin or not destination:
        st.error("Please enter both origin and destination cities.")
    else:
        
        with st.spinner("Searching for flights and hotels... This may take a moment."):
            
            arrival_date_str = arrival_date.strftime("%Y-%m-%d")
            return_date_str = return_date.strftime("%Y-%m-%d")
            stay_duration = str((return_date - arrival_date).days)
            
            user_inputs = {
                "messages": [],
                "origin": origin,
                "destination": destination,
                "currency": currency,
                "budget": str(budget),
                "num_people": str(num_people),
                "arrival_date": arrival_date_str,
                "return_date": return_date_str,
                "stay_duration": stay_duration,
                "flight_options": [],
                "hotel_options": [],
                "date_error": ""
            }
            
            unique_thread_id = str(uuid.uuid4())
            config = {"configurable": {"thread_id": unique_thread_id}}
            
            try:
                result = app.invoke(user_inputs, config)
                
                if result.get('date_error'):
                    st.error(result['date_error'])
                else:
                    flights = result.get("flight_options", [])
                    hotels = result.get("hotel_options", [])
                    num_nights = (return_date - arrival_date).days
                    
                    st.success("Search completed!")
                    
                    st.markdown(f"## Your Trip Plan: {origin} ↔ {destination}")
                    st.markdown(f"**Dates:** {arrival_date_str} to {return_date_str} ({num_nights} nights)")
                    st.markdown(f"**Budget:** {budget:.2f} {currency}")
                    st.markdown(f"**Travelers:** {num_people}")
                    
                    st.markdown("---")
                    
                    st.markdown("### ✈️ Flight Options")
                    
                    if flights:
                        origin_code = convert_city_to_airport_code(origin)
                        destination_code = convert_city_to_airport_code(destination)
                        
                        outbound_flights = []
                        return_flights = []
                        
                        for flight in flights:
                            if flight.get('origin_code') == origin_code:
                                outbound_flights.append(flight)
                            else:
                                return_flights.append(flight)
                        
                        if outbound_flights:
                            st.markdown("#### Outbound Flights")
                            for i, flight in enumerate(outbound_flights, 1):
                                with st.container():
                                    col1, col2, col3 = st.columns([2, 2, 1])
                                    with col1:
                                        st.markdown(f"**{flight['airline']}** - {flight['route']}")
                                        st.markdown(f"Departs: {flight['departure']} | Arrives: {flight['arrival']}")
                                    with col2:
                                        st.markdown(f"**Price:** {flight['price']:.2f} {flight['currency']}")
                                    with col3:
                                        st.link_button("Book", flight['link'], use_container_width=True)
                                st.markdown("")
                        
                        if return_flights:
                            st.markdown("#### Return Flights")
                            for i, flight in enumerate(return_flights, 1):
                                with st.container():
                                    col1, col2, col3 = st.columns([2, 2, 1])
                                    with col1:
                                        st.markdown(f"**{flight['airline']}** - {flight['route']}")
                                        st.markdown(f"Departs: {flight['departure']} | Arrives: {flight['arrival']}")
                                    with col2:
                                        st.markdown(f"**Price:** {flight['price']:.2f} {flight['currency']}")
                                    with col3:
                                        st.link_button("Book", flight['link'], use_container_width=True)
                                st.markdown("")
                        
                        if outbound_flights and return_flights:
                            cheapest_out = min(outbound_flights, key=lambda x: x['price'])
                            cheapest_ret = min(return_flights, key=lambda x: x['price'])
                            total_flight = cheapest_out['price'] + cheapest_ret['price']
                            st.info(f"**Best Flight Deal:** {total_flight:.2f} {currency} (outbound + return)")
                    else:
                        st.warning("No flights found. Please try different dates or cities.")
                    
                    st.markdown("---")
                    
                    st.markdown("### 🏨 Hotel Options")
                    
                    if hotels:
                        for i, hotel in enumerate(hotels, 1):
                            with st.container():
                                col1, col2, col3 = st.columns([2, 2, 1])
                                with col1:
                                    st.markdown(f"**{hotel['name']}**")
                                    st.markdown(f"Location: {hotel['distance_to_center']} from center")
                                with col2:
                                    if hotel['price']:
                                        total_hotel = hotel['price'] * num_nights
                                        st.markdown(f"**Price:** {hotel['price']:.2f} {hotel['currency']}/night")
                                        st.markdown(f"Total: {total_hotel:.2f} {hotel['currency']} ({num_nights} nights)")
                                    else:
                                        st.markdown("**Price:** See website")
                                with col3:
                                    st.link_button("Book", hotel['link'], use_container_width=True)
                            st.markdown("")
                        
                        if flights and outbound_flights and return_flights:
                            hotels_with_prices = [h for h in hotels if h.get('price')]
                            if hotels_with_prices:
                                cheapest_hotel = min(hotels_with_prices, key=lambda x: x['price'])
                                total_hotel_cost = cheapest_hotel['price'] * num_nights
                                total_cost = total_flight + total_hotel_cost
                                
                                st.markdown("#### Budget Analysis")
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Flights (cheapest)", f"{total_flight:.2f} {currency}")
                                with col2:
                                    st.metric("Hotel (cheapest)", f"{total_hotel_cost:.2f} {currency}")
                                with col3:
                                    if total_cost <= budget:
                                        st.metric("Total", f"{total_cost:.2f} {currency}", f"✓ Within budget")
                                    else:
                                        st.metric("Total", f"{total_cost:.2f} {currency}", f"Over by {total_cost - budget:.2f}")
                    else:
                        st.warning("No hotels found. Please try a different destination.")
                    
                    st.markdown("---")
                    st.info("**Note:** Prices shown are from Amadeus API and may not reflect live rates. Click booking links for current prices.")
            
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.info("Please check your API credentials and try again.")


st.markdown("---")
st.markdown("**Powered by:** Amadeus API | Built with Streamlit & LangGraph")