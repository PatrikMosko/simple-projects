import sys
from args import Args, print_exit
from fsm import FSM
from minimalize import Minimize

# ----------------------------------< --analyze-string >---------------------------------------#
def analyze_string(string, automata):
    for char in string:
        if char not in automata["alphabet"]:
            print_exit('0', 1)

    state = automata["start"]
    char_cnt = 0
    str_len = len(string)

    for char in string:
        found = False
        
        for rule in automata["rules"]:
            if rule.c == char and rule.s1 == state:
                state = rule.s2
                char_cnt += 1
                found = True
                break;
        
        if found is False:
            return '0'

    if rule.s2 not in automata["finals"]:
        return '0'
    else:
        return '1'

# -------------------------------------< FINAL OUTPUT >-----------------------------------------#
def print_FSM(fsm):
    str = "(\n{"

    # all states
    for state in fsm["states"]:
        str += state+', '
    str = str[0:-2]+'},\n{'

    # alphabet
    for char in fsm["alphabet"]:
        str += '\''+char+'\', '
    str = str[0:-2]+'},\n{\n'

    # rules
    for rule in fsm["rules"]:
        str += rule+',\n'

    # start state
    str = str[0:-2] + '\n},\n' + fsm["start"] + ',\n{'

    # final states
    for state in fsm["finals"]:
        str += state+', '
    str = str[0:-2]+'}\n)\n'

    return str

# ----------------------------------------------------------------------------------------------#
#Parse arguments
args = Args()
#Check arguments
args.check_args()

#Print help if exists switch
if args.argv.help is True:
    if len(sys.argv) != 2:
        print_exit("Wrong arguments1.", 1)
    print(args.print_help())
    sys.exit(0)

#Use stdin if --input switch does not exist
if args.argv.input is None:
    inputFile = sys.stdin
else:
    try:
        inputFile = open(args.argv.input, mode="r", newline="", encoding="utf-8")
    except IOError:
        print_exit("Opening input file failed.", 2)

#Use stdout if --output switch does not exist
if args.argv.output is None:
    outputFile = sys.stdout
else:
    try:
        outputFile = open(args.argv.output, mode="w", newline="", encoding="utf-8")
    except IOError:
        print_exit("Opening output file failed.", 3)

#Let the scanner do the work and get us all the tokens.
WSFA = FSM(inputFile.read(), args)

# final output based on command line options
if args.argv.analyze is not None:
    ret = analyze_string(args.argv.analyze, WSFA.automata)
    outputFile.write(ret)

elif args.argv.f is True:
    outputFile.write(WSFA.nonFinState)

elif args.argv.m is True:
    min = Minimize(WSFA)
    outputFile.write(print_FSM( min.automata ))

else:
    WSFA.create_sorted_automata()
    outputFile.write(print_FSM( WSFA.automata ))

inputFile.close()
outputFile.close()

exit(0)
