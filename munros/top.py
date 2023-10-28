from math import sqrt


class Top():
    def __init__(self, id: int, name:str, e:int, n:int) -> None:
        self.id = id
        self.name = name
        self.e = e
        self.n = n
    
    def __sub__(self, other) -> int:
        
            deltaE = int(other.e)-int(self.e)
            deltaN = int(other.n)-int(self.n)
            dist_meters = sqrt(deltaE*deltaE + deltaN*deltaN)
            return round(dist_meters)