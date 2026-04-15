import os
import importlib

#Search Target Exposure Factor Function File
path_PROJECT      = os.path.dirname(os.path.realpath(__file__))
path_tefFunctions = os.path.join(path_PROJECT, 'tef_function_models')
files_teffunctions = os.listdir(path_tefFunctions)

#Import Target Exposure Factor Function Files
TEFFUNCTIONS_GET_TEF     = dict()
TEFFUNCTIONS_DESCRIPTORS = dict()
for name_file in files_teffunctions:
    if name_file.startswith('teff_') and name_file.endswith('.py'):
        name_module   = name_file[:-3]
        name_function = name_file[5:-3]
        try:
            module = importlib.import_module(f"tef_function_models.{name_module}")
            func = getattr(module, 'getTEF')
            desc = getattr(module, 'DESCRIPTOR')
            TEFFUNCTIONS_GET_TEF[name_function]     = func
            TEFFUNCTIONS_DESCRIPTORS[name_function] = desc
        except Exception as e:
            print(e)