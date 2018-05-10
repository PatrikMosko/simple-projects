import argparse
import sys
import re

#Class for arguments handling
class Args:
    def __init__(self):
        """Constructor parses arguments"""
        self.parse()

    def parse(self):
        """Method for parsing arguments"""
        parser = argparse.ArgumentParser(description='Process some arguments.', add_help=False)
        parser.add_argument('--help', action="store_true")
        parser.add_argument('--input')
        parser.add_argument('--output')
        parser.add_argument('-f', '--find-non-finishing', action="store_true", dest="f")
        parser.add_argument('-m', '--minimize'          , action="store_true", dest="m")
        parser.add_argument('-i', '--case-insensitive'  , action="store_true", dest="i")
        parser.add_argument(      '--analyze-string'    ,                      dest='analyze')
        parser.add_argument('-w', '--white-char'        , action='store_true', dest='w')
        parser.add_argument('-r', '--rules-only'        , action='store_true', dest='r')
        try:
            self.argv = parser.parse_args()
        except:
            print_exit("Wrong arguments.", 1)
    
    #Method for checking arguments
    def check_args(self):
        
        #Check duplicity
        self.check_duplicity(sys.argv)
        
        #Help switch with more switches active
        if self.argv.help is True and len(sys.argv) > 2:
            print_exit("Wrong arguments.", 1)
        
        #M switch and F switch active simultaneously
        if self.argv.f is True and self.argv.m is True:
            print_exit("Wrong arguments.", 1)
        
        #Analyze-string option check
        if self.argv.analyze is not None and \
            (self.argv.m is True or self.argv.f is True):
            print_exit("Wrong arguments.", 1)

    #Check duplicity of arguments
    def check_duplicity(self, argv):
        temp = []
        
        for arg in argv:
            arg = re.sub('\=.*', "", arg)
            if   arg == "--find-non-finishing": arg = "-f"
            elif arg == "--minimize":           arg = "-m"
            elif arg == "--case-insensitive":   arg = "-i"
            elif arg == "--white-char":         arg = "-w"
            elif arg == "--rules_only":         arg = "-r"
            
            if arg not in temp:
                temp.append(arg)
            else:
                print_exit("Duplicate argument.", 1)

    #Method for printing Helper
    def print_help(self):
        return("""
            |--------------------------------------------Minimization of finite automata---------------------------------------------|
            |---------------------------------------------------------USAGE:---------------------------------------------------------|
            | -input=filename          => input file with FSM                     
            | -output=filename         => output file with FSM in normalized form 
            | -f, --find-non-finishing => outputs non-finishing state only. If there is none, outputs zero. Can't combine -f with -m 
            | -m, --minimize           => minimizes the input FSM and outputs minimized form. Can't combine -f with -m 
            | -i, --case-insensitive   => will not care about case of the letters in comparisons. 
            | -r, --rules-only         => only rules component is in the input file 
            | -analyze-string="string" => checks, whether the string is valid string of the input FSM. 
        """)

def print_exit(msg, ret):
    """Method for error handling"""
    sys.stderr.write(msg)
    sys.exit(ret)
