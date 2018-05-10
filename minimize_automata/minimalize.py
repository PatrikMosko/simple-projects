#Modul for minimalization
from fsm import rule_dest

""" stores list of object names """
class minS:
    def __init__(self, idx, states):
        self.index = idx
        self.set = states


class Minimize:
    def __init__(self, fsm):
        self.first = ""
        self.minimize(fsm)
        self.automata = self.get_min_fsm(fsm)

    """ function returns new, minimized states (sets of states) """
    def minimize(self, WSFA):
        fsm = WSFA.automata

        # declared for all states except finals
        other = []
        # list of objects 'minS' representing new, minimalized states
        self.min = []
        # unique index of every instantiated object 'minS'
        self.index = 0
        # upcoming 'while' quits state division when this flag is False
        next_dividing = True

        # initialization of first two sets (final states and other ones)
        if len(fsm["finals"]) != 0:
            self.min.append( minS(self.idx(), fsm["finals"]) )
        
        for state in fsm["states"]:
            if state not in fsm["finals"]:
                other.append(state)
        
        if len(other) != 0:
            self.min.append( minS(self.idx(), other) )

        while(next_dividing is True):
            next_dividing = False
            
            for sym in fsm["alphabet"]:
                counter = 0
                
                for state_set in self.min:
                    # index of "set of states" will be mapped on state-name
                    new_list = {}
                    
                    for state in state_set.set:
                        # store index of first state in actual set
                        if state_set.set.index(state) == 0:
                            self.first = state
                        
                        dest_name = rule_dest(WSFA, state, sym)
                        
                        # final state
                        if dest_name is False:
                            continue
                        
                        new_list[state] = self.get_set(dest_name).index
                    
                    # index of set for the first state
                    chop_idx = new_list[self.first]
                    # new_set will contain all states heading to states from set with index 'chop_idx'
                    new_set = []
                    
                    for state in state_set.set:
                        if new_list[state] == chop_idx:
                            new_set.append(state)
                    if len(new_set) == len(state_set.set):
                        counter += 1
                        continue

                    diff = list(set(state_set.set) - set(new_set))
                    # new divisions
                    self.min.append(minS(self.idx(), new_set))
                    self.min.append(minS(self.idx(), diff))
                    del self.min[counter]

                    # increase counter for new 'set of states' => one minimized state
                    counter += 1
                    next_dividing = True


    """ function will set minimized states (sets of states) and rules (names) """
    def get_min_fsm(self, WSFA):
        fsm = WSFA.automata
        startS = None
        finals = []
        states = []
        rules = []

        # this for creates new state names (also with rules)
        for state_set in self.min:
            new = ""
            final = False
            start = False
            set = sorted(sorted(state_set.set), key=str.upper)
            
            for s in set:
                if s in fsm["finals"]:
                    final = True
                if s == fsm["start"]:
                    start = True
                new += s+'_'
            new = new[0:-1]
            
            if final is True:
                finals.append(new)
            if start is True:
                startS = new
            
            states.append(new)

            # this loop creates new rules for minimized automaton
            for char in fsm["alphabet"]:
                next = False
                
                for s in set:
                    if next is True:
                        continue
                    dest_s = rule_dest(WSFA, s, char)
                    
                    if dest_s is False and final is True:
                        continue
                    
                    dest_set = self.get_set(dest_s)
                    rule = new + ' \'' + char + '\' -> '
                    set2 = sorted(sorted(dest_set.set), key=str.upper)
                    
                    for s in set2:
                        rule += s + '_'
                    rules.append(rule[0:-1])
                    next = True

        # return new minimized automata structure
        return {"start"    : startS,
                "states"   : sorted(sorted(states), key=str.upper),
                "alphabet" : sorted(sorted(fsm["alphabet"]), key=str.upper),
                "finals"   : sorted(sorted(finals), key=str.upper),
                "rules"    : sorted(sorted(rules), key=str.upper)}


    """ auto-incrementing index function"""
    def idx(self):
        self.index += 1
        return self.index - 1

    """ function returns set of states in 'minS' object """
    def get_set(self, name):
        for set in self.min:
            for state in set.set:
                if name == state:
                    return set
