import plotly.express as px


def main():
    df = px.data.gapminder().query("year == 2007")
    print(df)
    fig = px.line_geo(df, locations="iso_alpha",
                    color="continent", # "continent" is one of the columns of gapminder
                    projection="orthographic")
    fig.show()