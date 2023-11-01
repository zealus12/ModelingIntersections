
from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import count_solutions, likelihood

# These two lines make sure a faster SAT solver is used.
from nnf import config
config.sat_backend = "kissat"

# Encoding that will store all of your constraints
E = Encoding()

# To create propositions, create classes for them first, annotated with "@proposition" and the Encoding
@proposition(E)
class BasicPropositions:

    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return f"A.{self.data}"
    
@constraint.none_of(E)
@proposition(E)
class AlwaysFalse:

    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return f"A.{self.data}"
    
false = AlwaysFalse("false")
true = ~false
    
# false_prop = BasicPropositions("false_prop")
# false = (~false_prop & ~false_prop)


# Different classes for propositions are useful because this allows for more dynamic constraint creation
# for propositions within that class. For example, you can enforce that "at least one" of the propositions
# that are instances of this class must be true by using a @constraint decorator.
# other options include: at most one, exactly one, at most k, and implies all.
# For a complete module reference, see https://bauhaus.readthedocs.io/en/latest/bauhaus.html
# @constraint.at_least_one(E)
# @proposition(E)
# class FancyPropositions:

#     def __init__(self, data):
#         self.data = data

#     def __repr__(self):
#         return f"A.{self.data}"

# # Call your variables whatever you want
# a = BasicPropositions("a")
# b = BasicPropositions("b")   
# c = BasicPropositions("c")
# d = BasicPropositions("d")
# e = BasicPropositions("e")
# # At least one of these will be true
# x = FancyPropositions("x")
# y = FancyPropositions("y")
# z = FancyPropositions("z")

left_is_valid = True
right_is_valid = True
straight_is_valid = True


class Intersection:
    def __init__(self, red_light_vertical, no_west, no_north, no_east, no_south):
        self.red_light_vertical = red_light_vertical
        self.no_west = no_west
        self.no_north = no_north
        self.no_east = no_east
        self.no_south = no_south

class Route:
    def __init__(self, lightstate: bool):

        self.Route_E = Encoding()

        @proposition(self.Route_E)
        class IntersectionPropositions:

            def __init__(self, data):
                self.data = data

            def __repr__(self):
                return f"A.{self.data}"

        left = IntersectionPropositions("left")
        right = IntersectionPropositions("right")
        straight = IntersectionPropositions("straight")

        self.constraint = ((left & ~straight & ~right) | (~left & straight & ~right) | (~left & ~straight & right))
       
    #     self.lightstate = lightstate
    #     # if self.lightstate:
    #         # self.constraint = ((left & ~straight & ~right) | (~left & straight & ~right) | (~left & ~straight & right))
    #         #                 This would be a recursive ca   recurse on straight           recurse on right
    #     if left_is_valid:
    #         left_r = Route(True)
    #         left_c = left_r.get_constraint()
    #     else:
    #         left_c = None

    #     if right_is_valid:
    #         right_r = Route(True)
    #         right_c = right_r.get_constraint()
    #     else:
    #         right_c = None

    #     if straight_is_valid:
    #         straight_r = Route(True)
    #         straight_c = straight_r.get_constraint()
    #     else:
    #         straight_c = None


    #     self.constraint =   (right_c if right_c != None else false) | (straight_c if straight_c != None else false)
    
    def get_encoding(self):
        return self.Route_E
    
    def get_constraint(self):
        return self.constraint



# Build an example full theory for your setting and return it.
#
#  There should be at least 10 variables, and a sufficiently large formula to describe it (>50 operators).
#  This restriction is fairly minimal, and if there is any concern, reach out to the teaching staff to clarify
#  what the expectations are.
def example_theory():
    test = Route(True)
    # E.add_constraint(test.get_constraint())
    E.add_constraint(test.get_constraint() & true)
    # test2 = Route(True)
    # e = test.get_encoding()
    # e2 = test2.get_encoding()

    # Add custom constraints by creating formulas with the variables you created. 
    # E.add_constraint((a | b) & ~x)
    # # Implication
    # E.add_constraint(y >> z)
    # # Negate a formula
    # E.add_constraint(~(x & y))
    # # You can also add more customized "fancy" constraints. Use case: you don't want to enforce "exactly one"
    # # for every instance of BasicPropositions, but you want to enforce it for a, b, and c.:
    # constraint.add_exactly_one(E, a, b, c)
    # return e
    return E


if __name__ == "__main__":

    T = example_theory()
    # Don't compile until you're finished adding all your constraints!
    T = T.compile()
    # After compilation (and only after), you can check some of the properties
    # of your model:
    print("\nSatisfiable: %s" % T.satisfiable())
    print("# Solutions: %d" % count_solutions(T))
    print("   Solution: %s" % T.solve())

    # print("\nVariable likelihoods:")
    # for v,vn in zip([a,b,c,x,y,z], 'abcxyz'):
    #     # Ensure that you only send these functions NNF formulas
    #     # Literals are compiled to NNF here
    #     print(" %s: %.2f" % (vn, likelihood(T, v)))
    print()


"""
EXPLANATION OF PROJECT PLAN

in order to deal with the issue of not being able to compile multiple encodings
we will have two classes
one class which is a route class
one class which is an intersection class which contains similar info to a c struct
the intersection will contain randomly generated booleans which define the map the car is driving along
the route class will be called and determine the first interstections option (left right straight)
it will determine these based off of the constraints for the intersection based off of the intersection struct booleans
inside the route class, we will pass a current location, a list of all previous locations, a goal location and the struct which coresponds to the current intersecion
the constructor of the route class will analyse the intersection and determine which direction can be taken (left right straight)
for each direction which can be taken, the function will be recursively called to explore all the possible paths if the car were to move in a given direction
if the car's current position reaches it's end position the recursion breaks and the function returns it's all the constraints it had
as the functions continue to return up the tree the disjoin all their successful sub paths together
this will end up with a massive constraint of disjunctions which will be the sole constaint of the entire project and can be used to find every successful route through the map
a path will also return if it is unsuccessful
a path is unsuccessful if it has no directions it can legally move or it has hit a previous location the car has already driven 
"""