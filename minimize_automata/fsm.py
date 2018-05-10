import re
from args import print_exit

class Rule:
    def __init__(self, s1, c, s2):
        self.s1 = s1
        self.c = c
        self.s2 = s2

class Token:
    def __init__(self, name, type):
        self.name = name
        self.type = type

class State:
    def __init__(self, name):
        self.checked = False
        self.name = name
        self.fin = None
        self.check_fin = []
    
    #set state as finishing or non-finishing
    def set_fin(self, fin):
        self.fin = fin

class FSM:
    """ Main class for FSM parsing """
    """Constructor removes Comments, Whitespaces, initialize variables and calls the root method"""
    def __init__(self, fsm, args):
        self.fsm     = self.comment_remove(fsm)
        self.fsm     = self.whitespace_remove(self.fsm)
        self.index   = 0            #Indexing the tokens
        self.args    = args         #Arguments of the program
        self.cS      = {}           #List for checking the completness of FSM
        self.nonFinC = 0            #Counter for Non finishing states
        self.rules_only_fin1 = False
        self.rules_only_fin2 = False
        self.nonFinState     = "0"
        self.check_determinism()

    """Method for removing comments"""
    def comment_remove(self, fsm):
        return re.sub('(?<!\')#.*|(?<=\')#(?!\').*', "", fsm)

    """Method for removing whitespaces"""
    def whitespace_remove(self, fsm):
        newFsm = ""
        
        for i in range(0, len(fsm)):
            """Whitespace not as alphabetical character"""
            if fsm[i].isspace():
                if i == (len(fsm)-1) or i == 0:
                    continue
                """Whitespace as alphabetical character"""
                if fsm[i-1] != "'" or fsm[i+1] != "'":
                    continue
            newFsm += fsm[i]
        
        return newFsm

    """Method for Scanner, to load the tokens"""
    def scanner(self):
        tokens = []
        state = 0
        id = ""
        length = len(self.fsm)
        i = 0
        
        while(i < length):
            """Start"""
            if state == 0:
                if re.match("\w", self.fsm[i], re.UNICODE) is not None:
                    """Identifier"""
                    id = id + self.fsm[i]
                    state =  1
                elif self.fsm[i] == '(':
                    """Other symbols"""
                    tokens.append(Token("(", "("))
                elif self.fsm[i] == ')':
                    tokens.append(Token(")", ")"))
                elif self.fsm[i] == '{':
                    tokens.append(Token("{", "{"))
                elif self.fsm[i] == '}':
                    tokens.append(Token("}", "}"))
                elif self.fsm[i] == ',':
                    tokens.append(Token(",", ","))
                elif self.fsm[i] == "'":
                    tokens.append(Token("'", "'"))
                elif self.fsm[i] == '-':
                    tokens.append(Token("-", "-"))
                elif (self.fsm[i] == '>'):
                    tokens.append(Token(">", ">"))
                elif (self.fsm[i] == '#'):
                    tokens.append(Token("#", "#"))
                elif (self.fsm[i] == '.'):
                    tokens.append(Token(".", "."))
                elif (self.fsm[i] == " "):
                    tokens.append(Token(" ", " "))
                elif re.match('[^\u0000-\u001f]', self.fsm[i]):
                    tokens.append(Token(self.fsm[i], "sym"))
                elif (self.fsm[i] == "\\"):
                    i += 1
                    if self.fsm[i] == "t":
                        tokens.append(Token("\\t", "\\t"))
                    elif self.fsm[i] == "n":
                        tokens.append(Token("\\n", "\\n"))
                    else:
                        print_exit("Lexical Error.\n", 60)
                else:
                    print_exit("Lexical Error.\n", 60)
            elif state == 1:
                """ Loading whole identifier """
                if re.match("\w", self.fsm[i], re.UNICODE) is not None:
                    id = id + self.fsm[i]
                else:
                    if re.match('[0-9]', id[0]) is not None and \
                        len(id) > 1:
                        print_exit("Lexical Error.\n", 60)
                    if len(tokens) != 0:
                        if tokens[-1] == "_":
                            print_exit("Lexical Error.\n", 60)
                    i -= 1
                    tokens.append(Token(id, "id"))
                    id = ""
                    state = 0
            i += 1
        if id != "":
            tokens.append(Token(id, "id"))
        tokens.append(Token("EOF", "EOF"))
        return tokens

    """Method for fetching the tokens, one by one"""
    def getToken(self, tokens):
        token = tokens[self.index]
        self.index += 1
        return token

    """Method for parsing the tokens and checking syntax of the FSM"""
    def parser(self, tokens):
        token = self.getToken(tokens)
        token1 = self.getToken(tokens)

        # Check opening parenthesis
        if token.type != '(' or token1.type != '{':
            print_exit("Syntactical Error.1\n", 60)

        # check syntax of states
        self.states(tokens)
        token = self.getToken(tokens)
        if token.type != ',':
            print_exit("Syntactical Error.2\n", 60)

        # check syntax of the alphabet
        self.alphabet(tokens)
        token = self.getToken(tokens)
        if token.type != ',':
            print_exit("Syntactical Error.3\n", 60)

        # check syntax of rules
        self.rules(tokens)
        token = self.getToken(tokens)
        
        if token.type != ',':
            print_exit("Syntactical Error.4\n", 60)
        token = self.getToken(tokens)
        if token.type != "id" or self.no_undr(token.name) is False:
            print_exit("Syntactical Error.5\n", 60)

        # check if start state exist in set of all states
        if token.name not in self.automata["states"]:
            print_exit("Semantical Error1.", 61)

        # Save the start state
        self.automata["start"] = token.name
        token = self.getToken(tokens)
        if token.type != ',':
            print_exit("Syntactical Error.6\n", 60)

        # check syntax of final states
        token = self.getToken(tokens)
        if token.type != '{':
            print_exit("Syntactical Error.1\n", 60)
        self.states(tokens, True)

        # end of the automata
        token = self.getToken(tokens)
        
        if token.type != ')':
            print_exit("Syntactical Error.7\n", 60)
        token = self.getToken(tokens)
        
        if token.type != 'EOF':
            print_exit("Syntactical Error.(EOF expected)\n", 60)
        return


    """ Method checks syntax of every state of FSM """
    def states(self, tokens, final=False):
        token = self.getToken(tokens)
        
        if final is True and token.type == "}":
            return
        # Beginning of the states component
        if token.type == "id" and self.no_undr(token.name):
            
            # Switch -i is active
            if self.args.argv.i is True:
                token.name = token.name.lower()
            
            if final is False:
                # All states component
                # Check duplicates
                if token.name not in self.automata["states"]:
                    self.automata["states"].append(token.name)
            else:
                # Final states component
                # Check if is in all states component
                if token.name not in self.automata["states"]:
                    print_exit("Semantical Error2.", 61)
                # Check duplicates
                if token.name not in self.automata["finals"]:
                    self.automata["finals"].append(token.name)
            
            token = self.getToken(tokens)
            
            # Expecting another state in Final states component
            if token.type == ',' and final == True:
                self.states(tokens, True)
            
            # Expecting another state in All states component
            elif token.type == ',' and final == False:
                self.states(tokens)
            elif token.type == '}':
                return
            else:
                print_exit("Syntactical Error.9\n", 60)
        
        elif token.type == "}":
            print_exit("Semantical error.", 61);
        
        else:
            print_exit("Syntactical Error.10\n", 60)


    """ Method checks syntax of input alphabet """
    def alphabet(self, tokens, next=False):
        token = self.getToken(tokens)
        
        # Beginning of the Aplhabet component
        if next == False:
            if token.type != '{':
                print_exit("Syntactical Error.11\n", 60)
            token = self.getToken(tokens)
            
            # Component is empty
            if token.type == "}":
                print_exit("Semantical Error3.", 61)
        
        # Opening apostrophe
        if token.type == "'":
            token = self.getToken(tokens)
            
            # Checks the symbol
            empty = self.valid_symbol(token.name, tokens)
            
            if empty is not False:
                if empty == 'apos':
                    token.name = '\'\''
                
                # The switch -i is active
                if self.args.argv.i is True:
                    token.name = token.name.lower()
                
                # Checks duplicates
                if token.name not in self.automata["alphabet"]:
                    self.automata["alphabet"].append(token.name)
                token = self.getToken(tokens)
                
                # Closing apostrophe
                if token.type == "'":
                    token = self.getToken(tokens)
                    
                    # Expecting another symbol in alphabet
                    if token.type == ',':
                        self.alphabet(tokens, True)
                    elif token.type == '}':
                        return
                    else:
                        print_exit("Syntactical Error.12\n", 60)
                else:
                    print_exit("Syntactical Error.13\n", 60)
            else:
                print_exit("Syntactical Error.14\n", 60)
        else:
            print_exit("Syntactical Error.15\n", 60)


    """ Method checks rules of automata """
    def rules(self, tokens, next=False):
        token1 = self.getToken(tokens)
        
        # Opening of the Rules component
        if next == False:
            if token1.type != '{':
                if self.args.argv.r is False:
                    print_exit("Syntactical Error.16\n", 60)
            else:
                token1 = self.getToken(tokens)
                if token1.type == '}':
                    return
        
        # Default state
        if token1.type == "id" and self.no_undr(token1.name):
            # rules-only option check, if first state is final
            if self.args.argv.r is True:
                if next == False:
                    self.automata["start"] = token1.name
                if self.getToken(tokens).type == ".":
                    self.rules_only_fin1 = True
                else:
                    self.index -= 1
            
            token = self.getToken(tokens)
            
            # Opening apostrophe of the symbol
            if token.type == "'":
                token2 = self.getToken(tokens)
                
                # Checks for empty(Epsilon) transition
                empty = self.valid_symbol(token2.name, tokens, True)
                
                if empty is not False:
                    if empty == '':
                        token2.name = ''
                    elif empty == 'apos':
                        token2.name = '\'\''
                    
                    t1 = self.getToken(tokens)
                    t2 = self.getToken(tokens)
                    t3 = self.getToken(tokens)
                    
                    # Closing apostrophe of the symbol
                    if t1.type == "'" and t2.type == "-" and t3.type == ">":
                        token3 = self.getToken(tokens)
                        
                        # Final state of the rule
                        if token3.type == "id" and self.no_undr(token3.name):
                            if empty == "" and token1.name != token3.name:
                                print_exit("Finite automata is not well-specified1!\n", 62)
                            
                            # rules-only option check, if second state is final
                            if self.args.argv.r is True:
                                if self.getToken(tokens).type == ".":
                                    self.rules_only_fin2 = True
                                else:
                                    self.index -= 1
                            # insert new rule into the list of rules
                            self.create_rule(token1.name,token2.name,token3.name)
                            token = self.getToken(tokens)
                            
                            if token.type == ',':
                                self.rules(tokens, True)
                            
                            elif token.type == '}':
                                if self.args.argv.r is False:
                                    return
                                else:
                                    print_exit("Syntactical Error.(rules_only)\n", 60)
                            
                            elif token.type == 'EOF':
                                return
                            
                            else:
                                print_exit("Syntactical Error.17\n", 60)
                        else:
                            print_exit("Syntactical Error.18\n", 60)
                    else:
                        print_exit("Syntactical Error.19\n", 60)
                else:
                    print_exit("Syntactical Error.20\n", 60)
            else:
                print_exit("Syntactical Error.21\n", 60)
        else:
            print_exit("Syntactical Error.22\n", 60)

    """ Method checks if string represents valid symbol for Alphabet """
    def valid_symbol(self, sym, tokens, rule=False):
        # Check double apostrophe
        if sym == "'":
            token = self.getToken(tokens)
            if token.type == "'":
                return "apos"
            
            # Epsilon in Alphabet
            elif token.type == "," or token.type == "}":
                self.index -= 2
                return True
            
            # Epsilon in Rules
            elif token.type == "-" and rule is True:
                self.index -= 2
                return ""
        
        elif len(sym) <= 2 and \
            (sym in ("\\t","\\n") or \
            re.match('[^\u0000-\u001f]', sym) is not None):
            return True
        
        return False


    """ Method checks existence of "_" at the beginning/end of string """
    def no_undr(self, idn):
        if idn[0] == "_" or idn[-1] == "_":
            return False
        else:
            return True

    """ Method creates new rule for FSM """
    def create_rule(self, s1, c, s2):
        # Switch -i is active
        if self.args.argv.i is True:
            s1 = s1.lower()
            s2 = s2.lower()
            c = c.lower()
        
        if self.args.argv.r is False:
            if s1 not in self.automata["states"] or \
                s2 not in self.automata["states"] or \
                (c not in self.automata["alphabet"] and c is not ''):
                print_exit("Semantical Error4.", 61)
        
        else:
            # rules-only option checking
            if s1 not in self.automata["states"]:
                self.automata["states"].append(s1)
            
            if s2 not in self.automata["states"]:
                self.automata["states"].append(s2)
            
            if self.rules_only_fin1 is not False:
                if s1 not in self.automata["finals"]:
                    self.automata["finals"].append(s1)
                self.rules_only_fin1 = False
            
            if self.rules_only_fin2 is not False:
                if s2 not in self.automata["finals"]:
                    self.automata["finals"].append(s2)
                self.rules_only_fin2 = False
            
            # check for empty string
            if c == "" and s1 == s2:
                return;
            if c not in self.automata["alphabet"]:
                self.automata["alphabet"].append(c)

        # Check determinism
        for rule in self.automata["rules"]:
            if rule.s1 == s1 and rule.c == c:
                if rule.s2 != s2:
                    print_exit("Finite automata is not well-specified!2\n", 62)
                else:
                    return
        
        self.automata["rules"].append(Rule(s1, c, s2))


    """Method for checking completeness of FSM"""
    def complete_check(self, s_from, state, list):
        list = list
        
        if self.state_exists(state) is False:
            self.cS[state] = State(state)
        if self.cS[state].checked is True:
            return self.cS[state].fin
        if state in self.automata["finals"]:
            self.cS[state].set_fin("fin")

        # Non finishing state
        if state not in self.automata["finals"]:
            check = self.state_complete(state)
            
            if ((self.cS[state].fin is not "fin") and (check == "nf")):
                self.cS[state].checked = True
                self.cS[state].set_fin("nf")
                self.nonFinC += 1
                self.nonFinState = state
                
                if self.nonFinC > 1:
                    print_exit("Finite automata is not well-specified!3\n", 62)
                else:
                    return "nf"

        if state in list:
            if state in self.automata["finals"]:
                return "fin"
            else:
                if self.cS[state].checked is not True:
                    self.cS[s_from].check_fin.append(state)
                    return
                else:
                    return self.cS[state].fin
        else:
            list.append(state)

        sym_num = len(self.automata["alphabet"])
        sym_cnt = 1
        
        for sym in self.automata["alphabet"]:
            dest = rule_dest(self, state, sym)
            
            if dest is False:
                continue
            
            if self.cS[state].fin is "fin" and \
                dest is False:
                continue
            
            if dest is False and self.cS[state] in self.automata["finals"]:
                continue
            res = self.complete_check(state, dest, list)
            
            if res is "fin":
                self.cS[state].set_fin("fin")
            
            elif res is "nf":
                if self.cS[state].fin is None:
                    self.cS[state].set_fin("nf")
            
            elif sym_cnt == sym_num and self.cS[state].fin != "fin":
                self.cS[state].set_fin("nf")
            
            sym_cnt += 1
        
        self.cS[state].checked = True
        
        if self.cS[state].fin is "fin":
            return "fin"
        
        elif self.cS[state].fin is "nf":
            return "nf"
        
        else:
            return None


    def state_complete(self, state):
        # Counter for number of non-finishing state
        counter = 0
        
        for symbol in self.automata["alphabet"]:
            found = False
            
            #Check all rules
            for rule in self.automata["rules"]:
                if rule.s1 == state and rule.c == symbol:
                    found = True
                    if rule.s2 == state:
                        counter += 1
            
            #Non complete FSM
            if found is False:
                print_exit("Finite automata is not complete4\n", 62)
        
        #Non finishing state
        if counter == len(self.automata["alphabet"]):
            return "nf"
        else:
            return True

    """ checks if state exists in one of the 'state sets'
        used in minimalization """
    def state_exists(self, state1):
        for state2 in self.cS:
            if state2 == state1:
                return True
        return False

    """ root function for complete scanning, parsing and minimalization
        and checking if automata is well-specified """
    def check_determinism(self):
        tokens = self.scanner()
        self.automata = {"states"  : [],
                         "alphabet": [],
                         "start"   : [],
                         "finals"  : [],
                         "rules"   : []}
        if self.args.argv.r is False:
            self.parser(tokens)
        else:
            self.rules(tokens)
        
        self.complete_check(None, self.automata["start"], [])
        self.final_check()
        self.check_inaccessible_states()

    """ after recursive checking of automata completness, checks
        if every state is accessible """
    def check_inaccessible_states(self):
        for state in self.automata["states"]:
            if state not in self.cS.keys():
                print_exit("Finite automata is not well-specified!5\n", 62)

    """ sets remaining states to fin/not-fin after recursion """
    def final_check(self):
        for (name, state) in self.cS.items():
            for state2 in state.check_fin:
                if self.cS[state2].fin == "fin":
                    self.cS[name].fin = "fin"
                else:
                    self.cS[name].fin = "nf"

    """ return sorted automata with rules converted to sorted strings """
    def create_sorted_automata(self):
        self.automata["alphabet"] = sorted(sorted(self.automata["alphabet"]), key=str.upper)
        self.automata["states"]   = sorted(sorted(self.automata["states"])  , key=str.upper)
        self.automata["finals"]   = sorted(sorted(self.automata["finals"])  , key=str.upper)

        #stringify rules
        rules =  []
 
        for r in self.automata["rules"]:
            rules.append(r.s1+' \''+r.c+'\' -> '+r.s2)

        self.automata["rules"] = rules
        self.automata["rules"] = sorted(sorted(self.automata["rules"]), key=str.upper)

def rule_dest(fsm, source, symbol):
    for rule in fsm.automata["rules"]:
        if rule.s1 == source and rule.c == symbol:
            return rule.s2
    return False
