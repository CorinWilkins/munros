from munros.munro import Munro
import csv

class MunrosCSVGateway():
    def __init__(self, file_name) -> None:
        self.file_name = file_name
    
    def __call__(self):
        tops = [None]
    
        with open(self.file_name, newline='') as csvfile:
            spamreader = csv.DictReader(csvfile, delimiter=',')
            for row in spamreader:
                tops.append(Munro(int(row["ID"]), row["Name"], int(row["Easting"]), int(row["Northing"])))
        
        return tops