from pathlib import Path
import os
current_path = Path(__file__)

def get_data_xml(name):
    c_path = current_path
    x_path = os.path.join(str(c_path), 'data', 'xml')
    my_file = Path(x_path)
    con = 0
    while not my_file.exists():
        if con > 3:
            break
        c_path = c_path.parent
        x_path = os.path.join(str(c_path), 'output', 'audio')
        my_file = Path(x_path)
        con += 1
    
    return os.path.join(str(my_file), name)
