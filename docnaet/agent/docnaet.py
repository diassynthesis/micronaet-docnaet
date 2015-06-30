#!/usr/bin/python
import os
import sys
#import subprocess

# Parameters:
import pdb; pdb.set_trace()
# TODO parametrize:
docnaet_path = "C:\\Docnaet\\FileStore"

if len(sys.argv) != 2:
    print("Not all parameters!")
    sys.exit()

# -----------------------------------------------------------------------------
# Extract operation from arguments:
# -----------------------------------------------------------------------------
# Format: docnaet://[operation]parameters
argument = sys.argv[1].split('//')[-1].split("]")
operation = argument[0][1:] # remove [
parameter = argument[1][:-1] # remove /

# -----------------------------------------------------------------------------
# Web Services:
# -----------------------------------------------------------------------------
if operation == 'open':
    # Extract parameters:
    parameters = parameter.split("-")
    protocol_id = parameters[0]
    document_id = parameters[1]
    
    document = os.path.join(docnaet_path, document_id)
    os.system("start %s" % document)
    
elif operation == 'home':
    pass # TODO
    

