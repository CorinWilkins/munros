from bng_latlon import OSGB36toWGS84
import plotly.express as px

class MapPresenter():
    
    def __call__(self, route, route_distance):
        print(f"Distance of the route: {round(route_distance/1000, 2)}km\n")
        latlongs = [OSGB36toWGS84(t.e, t.n) for t in route]
        self.fig = px.line_geo(lat = [lat for lat, _ in latlongs], lon=[lon for _, lon in latlongs], hover_name=[t.name for t in route ], scope="europe")
        
    def present(self):
        self.fig.show()
