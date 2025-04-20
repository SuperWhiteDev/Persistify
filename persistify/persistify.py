from typing import TextIO, Any, Optional, Union
import inspect
from re import finditer

def is_supported_data_type(data) -> bool:
    if isinstance(data, (list, tuple, dict, set, frozenset, int, float, str, bool)):
        return True

    if data == None:
        return True

    if isinstance(data, object):
        signature = inspect.signature(data.__init__)
        if len(signature.parameters) <= 1:
            return True
        else:
            attrs = data.__dir__()
            for parameter in signature.parameters:
                if parameter not in attrs:
                    return False
            
            return True

    return False

def _convert_data(data, indent=Optional[Union[int, str]]) -> Any:
    if not is_supported_data_type(data):
        raise TypeError("Argument 'data' must be of type list, tuple, dict, set, frozenset, str, int, float, bool or object.")
    
    if isinstance(data, str):
        return data
    elif isinstance(data, (int, float, bool)):
        return data
    elif isinstance(data, (list, tuple, dict, set, frozenset)):
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                result[_convert_data(key, indent)] = _convert_data(value, indent)
            return result

        # Если data - список.
        elif isinstance(data, list):
            result = []
            for item in data:
                result.append(_convert_data(item, indent))
            return result

        # Если data - кортеж (tuple) (неизменяемый).
        # Сначала собираем обработанные данные в список, затем преобразуем его в кортеж.
        elif isinstance(data, tuple):
            temp = []
            for item in data:
                temp.append(_convert_data(item, indent))
            return tuple(temp)

        # Если data - множество (set).
        elif isinstance(data, set):
            result = set()
            for item in data:
                result.add(_convert_data(item, indent))
            return result

        # Если data - frozenset (также неизменяемый).
        elif isinstance(data, frozenset):
            temp = set()
            for item in data:
                temp.add(_convert_data(item, indent))
            return frozenset(temp)
        else:
            raise TypeError("Unsupported container type.")
    elif data == None:
        return data
    else:
    
        attrs = {"__classname__": data.__class__.__name__}
    
        for attr in data.__dir__():
            if attr == "__dict__" or attr == "__module__":
                continue
            if not callable(getattr(data, attr)):
                attr_value = getattr(data, attr)

                if not is_supported_data_type(attr_value):
                    raise TypeError("Argument 'data' must be of type list, tuple, dict, set, frozenset, str, int, float, bool or object.")

                attrs[attr] = _convert_data(attr_value, indent)

        return attrs

def save(file : Optional[TextIO], data, indent=Optional[Union[int, str]]) -> Optional[str]:
    """
    
    """

    if not is_supported_data_type(data):
        raise TypeError("Argument 'data' must be of type list, tuple, dict, set, frozenset, str, int, float, bool or object.")
    
    if isinstance(data, str):
        data = _convert_data(data, indent)
        if data.find("\n") != -1:
            data = f"\"\"\"{data}\"\"\""
        else:
            data = f"\"{data}\""
    elif isinstance(data, (int, float, bool)):
        data = str(_convert_data(data, indent))
    elif isinstance(data, (list, tuple, dict, set, frozenset)):
        data = str(_convert_data(data, indent))

        # find all strings in data
        quotes = [(m.start(), m.end()+1) for m in finditer(r"\"[^\"]*\"|'[^']*'", data)]
        if indent:
            k = 1
            for m in finditer(r"\[|\]|\(|\)|\{|\}", data):
                skip = False
                for quote in quotes:
                    if m.start() >= quote[0] and m.end() <= quote[1]:
                        #print(m.start(), m.end(), data[quote[0]:quote[1]])
                        skip = True
                if skip:
                    continue

                if m.group() in ("[", "(", "{"):
                    data = data[:m.start()+1*k] + "\n" + data[m.end()+1*(k-1):] 
                else:
                    data = data[:m.start()+1*k - 1] + "\n" + data[m.start()+1*k - 1:]
                k += 1
            data = data.replace(", ", ",\n")
        
        if isinstance(indent, int):
            strings = data.split("\n")
            data = ""
            level = 0
            
            for string in strings:
                if string.startswith(("]", ")", "}")) or ("]" in string or "}" in string or ")" in string):
                    level -= 1

                data += " " * indent * level + string + "\n"

                if string.startswith(("[", "(", "{")) or (": [" in string or ":[" in string or  ": {" in string or  ":{" in string or  ": (" in string or  ":(" in string):
                    level += 1

        elif isinstance(indent, str):
            data = _convert_data(data, indent).replace(" ", indent)
    elif data == None:
        data = str(_convert_data(data, indent))
    else:
        data = str(_convert_data(data, indent))
    
    if file:
        file.seek(0)
        file.write(data)
    else:
        return data
    
def _parse(data, args: Optional[object] = None) -> Any:
    if isinstance(data, dict):
        if "__classname__" in data:
            if args:
                for cls in args:
                    if cls.__name__ == data["__classname__"]:
                        signature = inspect.signature(cls)
                        
                        if len(signature.parameters) > 0:
                            params = []

                            for parameter in signature.parameters:
                                for attr, value in data.items():
                                    try:
                                        if attr == "__classname__":
                                            continue
                                        if attr == parameter:
                                            params.append(value)
                                    except AttributeError:
                                        pass
                                
                            ret_cls = cls(*params)
                        else:
                            ret_cls = cls()
                        for attr, value in data.items():
                            try:
                                if attr == "__classname__":
                                    continue
                                setattr(ret_cls, attr, _parse(value, args))
                            except AttributeError:
                                pass
                        return ret_cls
            
            raise RuntimeError(f"The required class template is not found in 'args' argument that restore an instance of {data["__classname__"]} class")
        
    if isinstance(data, (list, tuple, dict, set, frozenset)):
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                result[_parse(key, args)] = _parse(value, args)
            return result

        # Если data - список.
        elif isinstance(data, list):
            result = []
            for item in data:
                result.append(_parse(item, args))
            return result

        # Если data - кортеж (tuple) (неизменяемый).
        # Сначала собираем обработанные данные в список, затем преобразуем его в кортеж.
        elif isinstance(data, tuple):
            temp = []
            for item in data:
                temp.append(_parse(item, args))
            return tuple(temp)

        # Если data - множество (set).
        elif isinstance(data, set):
            result = set()
            for item in data:
                result.add(_parse(item, args))
            return result

        # Если data - frozenset (также неизменяемый).
        elif isinstance(data, frozenset):
            temp = set()
            for item in data:
                temp.add(_parse(item, args))
            return frozenset(temp)
        else:
            raise TypeError("Unsupported container type.")
    
    return data


def load(source : Optional[Union[TextIO, str]], args: Optional[object] = None) -> Any:
    """

    """

    if isinstance(source, str):
        data = eval(source)
    else:
        source.seek(0)
        line = source.read()

        data = eval(line)
    
    return _parse(data, args)
    
def save_s(file : Optional[TextIO], data, key) -> Optional[str]:
    """
    
    """

    if not is_supported_data_type(data):
        raise TypeError("Argument 'data' must be of type list, tuple, dict, set, frozenset, str, int, bool or object.")

    raise NotImplementedError("")

def load_s(source : Optional[Union[TextIO, str]], key, args: Optional[object] = None) -> Any:
    """
    
    """
    raise NotImplementedError("")