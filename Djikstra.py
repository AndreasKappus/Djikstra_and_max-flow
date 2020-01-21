infinity = 100000
invalid_node = -1

class Node:
    previous = invalid_node
    distfromsource = infinity
    visited = False

class Dijkstra:

    def __init__(self):
        '''initialise the class'''
        self.startnode = 0
        self.endnode = 0
        self.network = []
        self.network_populated = False
        self.nodetable = []
        self.nodetable_populated = False
        self.currentnode = 0

    def populate_network(self, filename):
        '''populate the network data structure'''
        self.network_populated = False
        try:
            networkfile = open(filename, "r")
        except IOError:
            print "Network file does not exist!"
            return
        for line in networkfile:
            self.network.append(map(int, line.strip().split(','))) # values in network are seperated by commas
        self.network_populated = True
        networkfile.close()

        self.populate_node_table()  # populate node table is called here instead of main, as this method is also being used for MaxFlow and would save time

    def populate_node_table(self):
        '''populate the node table with data from the network'''
        self.nodetable = []
        self.nodetable_populated = False
        if not self.network_populated:
            print "network not populated!"  # check if network is populate before populating node table
            return
        for node in self.network:
            self.nodetable.append(Node())   # Append nodetable with node class to allow their use for checking distfromsource .etc
        self.nodetable[self.startnode].distfromsource = 0   # set by default since no transitions have taken place
        self.nodetable[self.startnode].visited = True   # start node is visited as that is the current node
        self.nodetable_populated = True

    def parse_route(self, filename):
        '''load route file'''
        self.route_populated = False
        self.route = []
        try:
            routefile = open(filename, "r")
        except IOError:
            print "Route file does not exist!"
            return
        for line in routefile:
            self.route = map(str, line.strip().split('>')) # append characters of route file, characters are split with ">"
        self.route_populated = True
        routefile.close()
        self.endnode = ord(self.route[-1]) - 65 # convert characters from route list to enable working with them for comparason and indexing .etc
        self.startnode = ord(self.route[0]) - 65

        self.currentnode = self.startnode


    def return_near_neighbor(self):
        '''determine nearest neighbors of the current node'''
        nn = []
        for index, edge in enumerate(self.network[self.currentnode]):   # goes through values of the current node
            if edge > 0 and not self.nodetable[index].visited:  # the check for neighbors while ensuring the node isn't visited
                nn.append(index)
        return nn

    def calculate_tentative(self):
        '''calculate tentative distances of nearest neighbors'''
        nn = self.return_near_neighbor()
        for neighbourindex in nn: # iterates through the nearest neighbors list
            tentativedist = self.nodetable[self.currentnode].distfromsource + self.network[self.currentnode][neighbourindex]
            # add the tentative distance with the distance of the current node and add the current node's index to find the tentative distances
            if tentativedist < self.nodetable[neighbourindex].distfromsource:
                # checks if the distance from source is less than the current distfromsource
                # if the tentative distance is lower than dist from source, then set the current distfromsource to the tentative distance as that is a shorter path
                self.nodetable[neighbourindex].distfromsource = tentativedist
                self.nodetable[neighbourindex].previous = self.currentnode

    def determine_next_node(self):
        '''determine next node to examine'''
        best_distance = infinity
        self.currentnode = invalid_node # since the node has been visited, the node becomes invalid
        for nodeindex, node in enumerate(self.nodetable):
            if(node.distfromsource < best_distance) and node.visited == False:
                # overwrites the distance from source with a shorter distance if it exists and sets the current node to the nodeindex
                best_distance = node.distfromsource
                self.currentnode = nodeindex

    def calculate_shortest_path(self):
        ''' keep looping until the current node has reached the end of the path or no options available
        code would iterate through the nodes using the calculate tentative and determine next node methods,
        since the current node would be visited, it then becomnes invalid because nodes cannot be visited more than once '''

        while not (self.currentnode == self.endnode or self.currentnode == invalid_node):
            self.calculate_tentative()
            self.determine_next_node()
            self.nodetable[self.currentnode].visited = True
            # ensures that if there is no path available, then return false
        if self.currentnode == invalid_node:
            return "no path found", False
        else:
            return True

    def return_shortest_path(self):
        '''return shortest path as list (start->end), and total distance'''
        ''' this method is called after calculate shortest path so the current node would be the end node or invalid depending if there's a path available
         the path would be reversed by calling ".previous" of the current node which would determine the shortest path.
         the current node is then appended to a list
         Since the path is iterating backwards, the list containing the shortest path would be reversed to show the path in the correct order'''
        shortest_path = []
        dist = self.nodetable[self.endnode].distfromsource
        msg_path = "path and total distance = "

        if self.calculate_shortest_path():  # if this method returned True, loop through path backwards
            while self.currentnode != invalid_node: # since the node before the start is invalid, loop through
                shortest_path.append(chr(self.currentnode + 65))    # convert current node to char for readability
                self.currentnode = self.nodetable[self.currentnode].previous    # iterating backwards so would get the previous value

            dist = self.nodetable[self.endnode].distfromsource  # variable declared which will be returned at the end of method
            shortest_path = shortest_path[::-1] # reverse the shortest path list
            return msg_path, shortest_path, dist
        else:
            return False

class MaxFlow(Dijkstra): #inherits from Dijkstra class
    def __init__(self):
        '''initialise class'''
        Dijkstra.__init__(self)
        self.original_network = []  # declaration so copy of the network can be made

    def populate_network(self, filename):
        '''Dijkstra method + need to make a copy of original network (hint)'''
        Dijkstra.populate_network(self, filename) # call populate network method from Dijkstra since inherited classes can use parent classes
        self.original_network = [row[:] for row in self.network] # store a copy of the network, since the network will be used for Max flow

    def return_bottleneck_flow(self):
        '''determine the bottleneck flow of a given path'''
        # Bottleneck flow would be the lowest value in a given path
        bottleneck = infinity # set to infinity by default
        # get shortest path since it uses all the Dijkstra methods, this enables the creation of a modified Dijkstra for max flow
        _msg, path, _dist = self.return_shortest_path() # inherited classes can use Base class methods, the "_" allows the method to ignore returned variables

        for node in path[::-1][:-1]: # reverse the path and leave out first node since that's the minimum cutoff point
            row = (ord(node) - 65)  # row = node, node is converted to numerical value so list calculations can be made
            column = self.nodetable[row].previous # column would be the previous row, since this is using the shortest_Path list to find the bottleneck

            if self.network[row][column] < bottleneck: # sets the bottleneck to the value in the network if lower
                bottleneck = self.network[row][column]
        return bottleneck, path

    def remove_flow_capacity(self):
        '''remove flow from network and return both the path and the amount removed'''

        bottleneck, path = self.return_bottleneck_flow() # get returned bottleneck and the path

        for node in path[::-1][:-1]: # same as return bottleneck flow method
            row = (ord(node) - 65)
            column = self.nodetable[row].previous

            self.network[row][column] -= bottleneck # remove flow capacity of value in network
            self.network[column][row] -= bottleneck # same as above but removing previous row's flow capacity, since there is a flow running through

        for index, node in enumerate(self.nodetable): # reset nodetable, so path can iterate through with the augmented network
            self.nodetable[index].visited = False
            self.nodetable[index].distfromsource = infinity
        self.currentnode = self.startnode
        self.nodetable[self.startnode].distfromsource = 0
        self.nodetable[self.startnode].visited = True

        return bottleneck, path

    def return_max_flow(self):
        '''calculate max flow across network, from start to end, and return both the max flow value and all the relevant paths'''
        # loop through Dijkstra, append all paths and bottlenecks
        # add bottlenecks to the total
        # return the total and all the paths
        msg_maxflow = "total max flow:"   # string for the output that's being returned
        msg_paths = "bottleneck and paths: "
        path_available = True   # condition to use with loop until no more paths are available
        total = 0
        paths = []

        while path_available:
            flow, route = self.remove_flow_capacity() # call the values of this method to append to list and add up the bottlenecks to get maximum flow
            paths.append(flow)
            paths.append(route)
            total += flow
            if flow == infinity:    # condition to break out of loop
                path_available = False
        paths.pop(-1) # last indexed value stores infinity, so pop last indexed value
        paths.pop(-1) # last indexed value stores an empty list, so pop last indexed value
        total -= infinity # stores infinity so subtract infinity from the flow
        return msg_paths, paths, msg_maxflow, total



if __name__ == '__main__':

    Algorithm = Dijkstra()
    Algorithm.parse_route("route.txt")
    Algorithm.populate_network("network.txt")
    Algorithm.calculate_shortest_path()
    print Algorithm.return_shortest_path()

    MF = MaxFlow()
    MF.populate_network("network.txt")
    # MF.parse_route("route.txt")
    MF.populate_node_table()
    print MF.return_max_flow()
