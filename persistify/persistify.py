from typing import TextIO, Any

def save(file : TextIO, *args) -> bool:
    """
    
    """
    file.seek(0)
    
    for arg in args:
        data = str(arg)

        file.write(data)

def load(file) -> Any:
    """
    """
    data = []

    file.seek(0)
    lines = file.readlines()
    
    for line in lines:
        data.append(eval(line))
    
    if len(data) == 1:
        return data[0]
    else:
        return data
