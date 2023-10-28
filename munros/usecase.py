from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


class FastestRouteSolver():
    def __init__(self, munros_gateway, presenter) -> None:
        self.munros_gateway = munros_gateway
        self.presenter = presenter
        
    
    def __call__(self, fast):
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
   
            return self.presenter(route, route_distance)

    def deltas(self, tops):
        length = len(tops)
        distances = [[0]*length for i in range(length)]
        
        for x, top0 in enumerate(tops):
            for y, top1 in enumerate(tops):
                if top1 is None or top0 is None:
                    delta = 0
                else:  
                    delta = top0 - top1
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

