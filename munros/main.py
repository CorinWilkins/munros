import csv
from munros.grid_references import grid_distance
from munros.top import Top
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import numpy as np


def parse_csv():
    tops = []
    with open('munros.csv', newline='') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter=',')
        for row in spamreader:
            tops.append(Top(int(row["ID"]), row["Name"], int(row["Easting"]), int(row["Northing"]), float(row["Lat"]), float(row["Lon"]) ))
    return tops



def deltas(tops):
    
    length = len(tops)+1
    distances = [ [0]*length for i in range(length)]

    for top0 in tops:
        for top1 in tops:
            delta = grid_distance(top0, top1)
            distances[top0.id][top1.id] = delta
    
    return distances


from bng_latlon import OSGB36toWGS84
import plotly.express as px


# [START solution_printer]
def print_solution(manager, routing, assignment, tops):
    """Prints assignment on console."""
    index = routing.Start(0)
    route_distance = 0
    order = []
    
    while not routing.IsEnd(index):
        # plan_output += f" {manager.IndexToNode(index)} ->"
        if(manager.IndexToNode(index) != 0):
            top = tops[manager.IndexToNode(index)]
            order.append(top)
            
        previous_index = index
        index = assignment.Value(routing.NextVar(index))
        route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
    # print(*[t.name for t in order],sep='\n')
    
    # print(f"Distance of the route: {round(route_distance/1000, 2)}km\n")
    latlongs = [OSGB36toWGS84(t.e, t.n) for t in order]
    fig = px.line_geo(lat = [lat for lat, _ in latlongs], lon=[lon for _, lon in latlongs], hover_name=[t.name for t in order ], scope="europe")
    
     
    fig.show()
    # [END solution_printer]


def main():
    """Entry point of the program."""
    # Instantiate the data problem.
    # [START data]
    # data = create_data_model()
    tops = parse_csv()
    distances = deltas(tops)
    # [END data]

    # Create the routing index manager.
    # [START index_manager]
    manager = pywrapcp.RoutingIndexManager(
        len(tops), 1, 0
    )
    
    # [END index_manager]

    # Create Routing Model.
    # [START routing_model]
    routing = pywrapcp.RoutingModel(manager)
    # [END routing_model]

    # Create and register a transit callback.
    # [START transit_callback]
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distances[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    # [END transit_callback]

    # Define cost of each arc.
    # [START arc_cost]
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    # [END arc_cost]

    # Setting first solution heuristic.
    # [START parameters]
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    # [END parameters]

    # Solve the problem.
    # [START solve]
    assignment = routing.SolveWithParameters(search_parameters)
    # [END solve]

    # Print solution on console.
    # [START print_solution]
    if assignment:
        print_solution(manager, routing, assignment, tops)
    # [END print_solution]
