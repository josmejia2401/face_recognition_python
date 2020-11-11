from pathlib import Path
import os
current_path = Path(__file__)

def get_data_xml(name):
    c_path = current_path
    x_path = os.path.join(str(c_path), 'data', 'xml')
    my_file = Path(x_path)
    con = 0
    while my_file.exists() == False:
        if con > 3:
            break
        c_path = c_path.parent
        x_path = os.path.join(str(c_path), 'data', 'xml')
        my_file = Path(x_path)
        con += 1
    
    my_file = os.path.join(str(my_file), name)
    my_file = Path(my_file)
    if my_file.exists() == False:
        raise Exception("not found")
    return str(my_file)


def get_data_config(name):
    c_path = current_path
    x_path = os.path.join(str(c_path), 'config', 'config')
    my_file = Path(x_path)
    con = 0
    while my_file.exists() == False:
        if con > 3:
            break
        c_path = c_path.parent
        x_path = os.path.join(str(c_path), 'data', 'config')
        my_file = Path(x_path)
        con += 1
    
    my_file = os.path.join(str(my_file), name)
    my_file = Path(my_file)
    if my_file.exists() == False:
        raise Exception("not found")
    return str(my_file)