import click
import csv
from math import sqrt
from typing import Any
from munros.top import Top
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import numpy as np
from bng_latlon import OSGB36toWGS84
import plotly.express as px

class MunrosCSVGateway():
    def __init__(self, file_name) -> None:
        self.file_name = file_name
    
    def __call__(self) -> Any:
        tops = [None]
    
        with open(self.file_name, newline='') as csvfile:
            spamreader = csv.DictReader(csvfile, delimiter=',')
            for row in spamreader:
                tops.append(Top(int(row["ID"]), row["Name"], int(row["Easting"]), int(row["Northing"])))
        
        return tops

class FastestRouteSolver():
    def __init__(self, munros_gateway) -> None:
        self.munros_gateway = munros_gateway
        
    
    def __call__(self, fast) -> Any:
        tops = self.munros_gateway()
        distances = self.deltas(tops)
        
        manager = pywrapcp.RoutingIndexManager(
            len(tops), 1, 0
        )
        
        routing = pywrapcp.RoutingModel(manager)
        
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return distances[from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        
        assignment = routing.SolveWithParameters(self.get_search_parameters(fast))
        
        if assignment:
            index = routing.Start(0)
            route_distance = 0
            route = []
            
            while not routing.IsEnd(index):
                top = tops[manager.IndexToNode(index)]
                if top is not None:
                    route.append(top)
                    
                previous_index = index
                index = assignment.Value(routing.NextVar(index))
                delta = routing.GetArcCostForVehicle(previous_index, index, 0)
                route_distance += delta
   
            return route, route_distance

    def deltas(self, tops):
        length = len(tops)
        distances = [[0]*length for i in range(length)]
        
        def grid_distance(ref1, ref2):
            deltaE = int(ref2.e)-int(ref1.e)
            deltaN = int(ref2.n)-int(ref1.n)
            dist_meters = sqrt(deltaE*deltaE + deltaN*deltaN)
            return round(dist_meters)
        
        for x, top0 in enumerate(tops):
            for y, top1 in enumerate(tops):
                if top1 is None or top0 is None:
                    delta = 0
                else:  
                    delta = grid_distance(top0, top1)
                distances[x][y] = delta
        return distances
    
    def get_search_parameters(self, fast):
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        if fast:
            search_parameters.first_solution_strategy = (
                routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
            )
        else:
            search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
            search_parameters.time_limit.seconds = 60
            search_parameters.log_search = True
        return search_parameters


class MapPresenter():
    def __call__(self, route, route_distance) -> Any:
        print(f"Distance of the route: {round(route_distance/1000, 2)}km\n")
        latlongs = [OSGB36toWGS84(t.e, t.n) for t in route]
        fig = px.line_geo(lat = [lat for lat, _ in latlongs], lon=[lon for _, lon in latlongs], hover_name=[t.name for t in route ], scope="europe")
        fig.show()





@click.command()
@click.option('--fast', default=True, help='Use first solution strategy')
def main(fast):
    usecase = FastestRouteSolver(MunrosCSVGateway('munros.csv'))
    MapPresenter()(*usecase(fast))
    
