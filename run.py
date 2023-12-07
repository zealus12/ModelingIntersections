
from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import count_solutions, likelihood
import random
# These two lines make sure a faster SAT solver is used.
from nnf import config
config.sat_backend = "kissat"

# Encoding that will store all of your constraints
E = Encoding()

@constraint.none_of(E)
@proposition(E)
class AlwaysFalse:

    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return f"A.{self.data}"
    
false = AlwaysFalse("false")
true = ~false
    

class Intersection:
    def __init__(self, red_light_col, no_west, no_north, no_east, no_south):
        self.red_light_col = red_light_col
        self.no_west = no_west
        self.no_north = no_north
        self.no_east = no_east
        self.no_south = no_south

    def __str__(self):  
        return "Red light % s, No West:% s, No North:% s, No East:% s, No South:% s," % (self.red_light_col, self.no_west, self.no_north, self.no_east, self.no_south)

class Map:
    def __init__(self, num_of_rows, num_of_cols, one_way_row, one_way_col):
        self.num_of_rows = num_of_rows
        self.num_of_cols = num_of_cols
        self.one_way_row = one_way_row
        self.one_way_col = one_way_col
        self.map = [[0]*self.num_of_cols for i in range(self.num_of_rows)]

        if(self.num_of_rows < self.one_way_row):
            self.one_way_row = self.num_of_rows
        if(self.num_of_cols < self.one_way_col):
            self.one_way_col = self.num_of_cols
        
        self.col_roads = []
        self.row_roads = []
        for x in range(0, self.one_way_col):
            self.col_roads.append(["one way", random.randint(0,1)]) # One way up if 1, down if 0
        while(len(self.col_roads) < self.num_of_cols):
            self.col_roads.append(["two way"])
        
        for x in range(0, self.one_way_row):
            self.row_roads.append(["one way", random.randint(0,1)])
        while(len(self.row_roads) < self.num_of_rows):
            self.row_roads.append(["two way"])
        
        random.shuffle(self.col_roads)
        random.shuffle(self.row_roads)
        self.roads = [self.col_roads, self.row_roads]
        for y in range(self.num_of_rows):
            for x in range(self.num_of_cols):
                no_north = False
                no_south = False
                no_east = False
                no_west = False

                if self.roads[0][x][0] == "one way":
                    if self.roads[0][x][1] == 1:
                        no_south = True
                    else:
                        no_north = True
                
                if self.roads[1][y][0] == "one way":
                    if self.roads[1][y][1] == 1:
                        no_west = True
                    else:
                        no_east = True

                if x == 0:
                    no_west = True
                if y == 0:
                    no_south = True 
                if x == self.num_of_cols-1:
                    no_east = True
                if y == self.num_of_rows-1:
                    no_north = True
                        
                self.map[x][y] = Intersection(random.randint(0,1),no_west,no_north,no_east,no_south)
                print_statement = "X:" + str(x) + " Y:" + str(y)
                print(print_statement)

Route_E = Encoding()

@proposition(Route_E)
class IntersectionPropositions:

    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return f"A.{self.data}"
    
grid = Map(3, 3, 0, 0)

approachDirections = ["N", "E", "S", "W"]

gridProps = []
propNames = []


#generate all propositions that could possibly be used
def createProps(grid):
    for i in range(len(grid.map)):
        for j in range(len(grid.map[0])):
            for direction in approachDirections:
                left = IntersectionPropositions("L"+direction+str(i)+str(j))
                right = IntersectionPropositions("R"+direction+str(i)+str(j))
                straight = IntersectionPropositions("S"+direction+str(i)+str(j))
                propNames.append("L"+direction+str(i)+str(j))
                propNames.append("R"+direction+str(i)+str(j))
                propNames.append("S"+direction+str(i)+str(j))
                gridProps.append(left)
                gridProps.append(right)
                gridProps.append(straight)
    print(propNames)


createProps(grid)
# list of the names (data field) for all of our grid props
gridPropNames = [x.data for x in gridProps]


target = [2, 2]
start = [0, 0]
startDir = "N"
prevLocations = [[]]

# TODO - update the following 3 functions when we include the rest of the factors for whether a move is valid
def turnLeft(intersection, direction):
    # converting old direction to direction after turn
    direction = approachDirections[(approachDirections.index(direction)-1)%4]
    if direction == "N":
        return not intersection.no_north
    elif direction == "E":
        return not intersection.no_east
    elif direction == "S":
        return not intersection.no_south
    elif direction == "W":
        return not intersection.no_west


def turnRight(intersection, direction):
    # converting old direction to direction after turn
    direction = approachDirections[(approachDirections.index(direction)+1)%4]
    if direction == "N":
        return not intersection.no_north
    elif direction == "E":
        return not intersection.no_east
    elif direction == "S":
        return not intersection.no_south
    elif direction == "W":
        return not intersection.no_west

def goStraight(intersection, direction):
    if direction == "N":
        return not intersection.no_north
    elif direction == "E":
        return not intersection.no_east
    elif direction == "S":
        return not intersection.no_south
    elif direction == "W":
        return not intersection.no_west
    
def findNewLocation(location, turnDir, direction):
    direction = findNewDirection(turnDir, direction)
    if direction == "N":
        return [location[0], location[1]+1]
    elif direction == "E":
        return [location[0]+1, location[1]]
    elif direction == "S":
        return [location[0], location[1]-1]
    elif direction == "W":
        return [location[0]-1, location[1]]

# finds the direction the car is facing after turning
def findNewDirection(turnDir, direction):
    if turnDir == "L":
        return approachDirections[(approachDirections.index(direction)-1)%4]
    if turnDir == "R":
        return approachDirections[(approachDirections.index(direction)+1)%4]
    if turnDir == "S":
        return direction

# converts the movement information into the correct proposition
def moveToProp(turnDir, direction, location):
    #originally this would return a new IntersectionPropositions with the same name as one of the possible ones in the array above. This would compile incorrectly as they were treated as seperate props
    #now we find the proposition in gridpros by name
    return gridProps[gridPropNames.index(IntersectionPropositions(turnDir+direction+str(location[0])+str(location[1])).data)]

# list of all correct paths as a list of positions and propositions
correctPaths = []
correctProps = []

# if this doesnt work, remove the recursion and use loops
class Route:
    def __init__(self, location, direction, target, previousLocations, previousProps, left_count, right_count, straight_count, test):
        # if the game is over
        print("dir:",direction)
        if previousLocations.count(location) >= 2 or location == target: # TODO - add loss condition for if it has no available moves
            # if the game ended in a win
            print(previousLocations)
            print(previousProps)
            correctPaths.append(previousLocations)
            correctProps.append(previousProps)
            if location == target:
                print("location:",location)
                print("target:",target)
                print("Good:",previousLocations)
            else: 
                print("location:",location)
                print("target:",target)
                print("Bad:",previousLocations)
        else:
            # if turning left is valid
            if turnLeft(grid.map[location[0]][location[1]], direction):
                test1 = test + "1"
                previousLocations1 = list(previousLocations)
                previousLocations1.append(findNewLocation(location, "L", direction))
                previousProps1 = list(previousProps)
                previousProps1.append(moveToProp("L", direction, location))
                Route(findNewLocation(location, "L", direction), findNewDirection("L", direction), target, list(previousLocations1), list(previousProps1), left_count + 1, right_count, straight_count, test1)

            # if turning right is valid
            if turnRight(grid.map[location[0]][location[1]], direction):
                test2 = test + "2"
                previousLocations2 = list(previousLocations)
                previousLocations2.append(findNewLocation(location, "R", direction))
                previousProps2 = list(previousProps)
                previousProps2.append(moveToProp("R", direction, location))
                Route(findNewLocation(location, "R", direction), findNewDirection("R", direction), target, list(previousLocations2), list(previousProps2), left_count, right_count + 1, straight_count, test2)

            # if going straight is valid
            if goStraight(grid.map[location[0]][location[1]], direction):
                test3 = test + "3"
                previousLocations3 = list(previousLocations)
                previousLocations3.append(findNewLocation(location, "S", direction))
                previousProps3 = list(previousProps)
                previousProps3.append(moveToProp("S", direction, location))
                Route(findNewLocation(location, "S", direction), findNewDirection("S", direction), target, list(previousLocations3), list(previousProps3), left_count, right_count, straight_count + 1, test3)

# Build a full theory for your setting and return it.
#
#  There should be at least 10 variables, and a sufficiently large formula to describe it (>50 operators).
#  This restriction is fairly minimal, and if there is any concern, reach out to the teaching staff to clarify
#  what the expectations are.
print(grid.map)
# generating routes
Route(start, startDir, target, [[0, 0]], [], 0, 0, 0, "")

# printing information about tasks
print("NUM PATHS:", len(correctProps))
print("PATHS:",correctPaths)
print("PROPS:",correctProps)

string = ""
path_constraint = []
i = 0
#For all valid paths
for path in correctProps:
    #create a new path constraint
    path_constraint.append(true)
    string += str("T")
    test_str =""
    #collect all propositions that must be true to reach our target
    for prop in path:
        path_constraint[i]  = path_constraint[i]  & prop
        string += str(" && " + str(prop))
        test_str += str(" && " + str(prop))
    #collect and negate everything else
    for allProp in gridProps:
        found = False
        for all in path:
            if all.data == allProp.data:
                found = True
        if not found:
            path_constraint[i]  = path_constraint[i]  & ~allProp
            string += str(" && ~" + str(allProp))
    i+=1


# This section of code generates a function called generate_con()
# generate_con() will return all of our propositions | together
# this will look like:
#
# def generate_con():
#   return path_constraint[0] | path_constraint[1] | path_constraint[2] | ... path_constraint[x]
# 
#  It will then set the constrain function to the return value of generate_con()
constraint_str = "def generate_con():\n\t return "
for i in range(len(path_constraint)):
    constraint_str += "path_constraint["+str(i)+"] | "
exec(constraint_str[:-2], globals())
constraint = generate_con()


Route_E.add_constraint(constraint)
    
 


if __name__ == "__main__":

    T = Route_E#example_theory()
    # Don't compile until you're finished adding all your constraints!
    T = T.compile()
    E.pprint(T)
    print(len(T.vars()))
    # After compilation (and only after), you can check some of the properties
    # of your model:
    print("\nSatisfiable: %s" % T.satisfiable())
    print("# Solutions: %d" % count_solutions(T))
    print("   Solution: %s" % T.solve())
    print("   Solution: %s" % T.solve())
    print("   Solution: %s" % T.solve())
    print()


    #docker run -it -v "C:\Users\Mike\Documents\uni\CISC 204\ModelingIntersections":/PROJECT cisc204 /bin/bash