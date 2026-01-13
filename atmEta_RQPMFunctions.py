import os
import importlib

#Import RQP Function Files
path_PROJECT      = os.path.dirname(os.path.realpath(__file__))
path_rqpFunctions = os.path.join(path_PROJECT, 'rqpfunctions')
files_rqpfunctions = os.listdir(path_rqpFunctions)

#Search RQP Function Files and Import
RQPMFUNCTIONS_GET_RQPVAL  = dict()
RQPMFUNCTIONS_DESCRIPTORS = dict()
for name_file in files_rqpfunctions:
    if name_file.startswith('rqpf_') and name_file.endswith('.py'):
        name_module   = name_file[:-3]
        name_function = name_file[5:-3]
        try:
            module = importlib.import_module(f"rqpfunctions.{name_module}")
            func = getattr(module, 'getRQPValue')
            desc = getattr(module, 'DESCRIPTOR')
            RQPMFUNCTIONS_GET_RQPVAL[name_function]  = func
            RQPMFUNCTIONS_DESCRIPTORS[name_function] = desc
        except Exception as e:
            print(e)