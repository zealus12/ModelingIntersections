from bauhaus import Encoding, proposition, constraint
Intersection_E = Encoding()

@proposition(Intersection_E)
class IntersectionPropositions:

    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return f"A.{self.data}"

left = IntersectionPropositions("left")
right = IntersectionPropositions("right")
straight = IntersectionPropositions("straight")

class Intersection:
    def __init__(self, lightstate: bool):
        # Intersection_E.add_constraint((lightstate | ~lightstate))
        self.lightstate = lightstate
        Intersection_E.add_constraint(lightstate >> (left | straight | right))
        Intersection_E.add_constraint(lightstate >> right)
        return Intersection_E

    @staticmethod 
    def get_encoding():
        return Intersection_E
