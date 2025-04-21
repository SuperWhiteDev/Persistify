from typing import TextIO, Any, Optional, Union
import inspect
from ast import literal_eval
from Crypto.Cipher import AES
import hashlib
import base64
from re import finditer


def is_supported_data_type(data) -> bool:
    """
    Checks whether the provided data is of a supported type.

    Supported types include:
        - list, tuple, dict, set, frozenset, int, float, str, bool, or None.
        - Objects whose __init__ method takes no arguments or, if it requires parameters, all parameter names are present as attributes of the object.

    Returns:
        bool: True if the data type is supported; otherwise, False.
    """

    if isinstance(data, (list, tuple, dict, set, frozenset, int, float, str, bool)):
        return True

    if data is None:
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


def _convert_data(data, indent: Optional[Union[int, str]], temp: dict) -> Any:
    if not is_supported_data_type(data):
        raise TypeError(
            "Argument 'data' must be of type list, tuple, dict, set, frozenset, str, int, float, bool or object or NoneType.\nIf data is an object, then the class of which data is an instance must have a constructor with parameters whose value is stored in the class attributes."
        )

    if isinstance(data, str):
        return data
    elif isinstance(data, (int, float, bool)):
        return data
    elif isinstance(data, (list, tuple, dict, set, frozenset)):
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                result[_convert_data(key, indent, temp)] = _convert_data(
                    value, indent, temp
                )
            return result

        elif isinstance(data, list):
            result = []
            for item in data:
                result.append(_convert_data(item, indent, temp))
            return result

        elif isinstance(data, tuple):
            temp = []
            for item in data:
                temp.append(_convert_data(item, indent, temp))
            return tuple(temp)

        elif isinstance(data, set):
            result = set()
            for item in data:
                result.add(_convert_data(item, indent, temp))
            return result

        elif isinstance(data, frozenset):
            temp = set()
            for item in data:
                temp.add(_convert_data(item, indent, temp))
            return frozenset(temp)
        else:
            raise TypeError("Unsupported container type.")
    elif data is None:
        return data
    else:
        data_id = id(data)
        if data_id in temp:
            return {"__classname__": data.__class__.__name__, "__classid__": data_id}
        else:
            attrs = {"__classname__": data.__class__.__name__, "__classid__": data_id}

            temp[id(data)] = attrs

            for attr in data.__dir__():
                if attr == "__dict__" or attr == "__module__":
                    continue
                if not callable(getattr(data, attr)):
                    attr_value = getattr(data, attr)

                    if not is_supported_data_type(attr_value):
                        raise TypeError(
                            "Argument 'data' must be of type list, tuple, dict, set, frozenset, str, int, float, bool or object or NoneType.\nIf data is an object, then the class of which data is an instance must have a constructor with parameters whose value is stored in the class attributes."
                        )

                    attrs[attr] = _convert_data(attr_value, indent, temp)

            return attrs


def save(
    file: Optional[TextIO], data, indent=Optional[Union[int, str]]
) -> Optional[str]:
    """
    Saves the given data as a string to a file or returns it as a formatted string.

    Args:
        file (Optional[TextIO]): The file object to write the data to. If None, the function returns the string.
        data: The data to be saved. Must be of a supported type.
        indent (Optional[Union[int, str]]): Optional indentation level or characters for formatting.

    Returns:
        Optional[str]: None if the data is written to the file; otherwise, the formatted string.
    """

    if not is_supported_data_type(data):
        raise TypeError(
            "Argument 'data' must be of type list, tuple, dict, set, frozenset, str, int, float, bool or object or NoneType.\nIf data is an object, then the class of which data is an instance must have a constructor with parameters whose value is stored in the class attributes."
        )

    # Storage for intermediate results during conversion
    temp = {}

    if isinstance(data, str):
        data = _convert_data(data, indent, temp)
        if data.find("\n") != -1:
            data = f'"""{data}"""'
        else:
            data = f'"{data}"'
    elif isinstance(data, (int, float, bool)):
        data = str(_convert_data(data, indent, temp))
    elif isinstance(data, (list, tuple, dict, set, frozenset)):
        data = str(_convert_data(data, indent, temp))

        # find all strings in data
        quotes = [
            (m.start(), m.end() + 1) for m in finditer(r"\"[^\"]*\"|'[^']*'", data)
        ]
        if indent:
            k = 1

            # find all brackets
            for m in finditer(r"\[|\]|\(|\)|\{|\}", data):
                skip = False
                for quote in quotes:
                    if m.start() >= quote[0] and m.end() <= quote[1]:
                        skip = True
                if skip:
                    continue

                if m.group() in ("[", "(", "{"):
                    data = (
                        data[: m.start() + 1 * k] + "\n" + data[m.end() + 1 * (k - 1) :]
                    )
                else:
                    data = (
                        data[: m.start() + 1 * k - 1]
                        + "\n"
                        + data[m.start() + 1 * k - 1 :]
                    )
                k += 1
            data = data.replace(", ", ",\n")

        if isinstance(indent, int):
            strings = data.split("\n")
            data = ""
            level = 0

            for string in strings:
                if string.startswith(("]", ")", "}")):
                    level -= 1

                data += " " * indent * level + string + "\n"

                if string.startswith(("[", "(", "{")) or (
                    ": [" in string
                    or ":[" in string
                    or ": {" in string
                    or ":{" in string
                    or ": (" in string
                    or ":(" in string
                ):
                    level += 1

        elif isinstance(indent, str):
            data = _convert_data(data, indent, temp).replace(" ", indent)
    elif data is None:
        data = str(_convert_data(data, indent, temp))
    else:
        data = str(_convert_data(data, indent, temp))

    if file:
        file.seek(0)
        file.write(data)
    else:
        return data


def _parse(data, args: Optional[object] = None, temp: dict = {}) -> Any:
    if isinstance(data, dict):
        if "__classname__" in data and "__classid__" in data:
            # Check if the same object has already been created, and if so, return it.
            if data["__classid__"] in temp:
                return temp[data["__classid__"]]
            else:
                if args:
                    for cls in args:
                        if cls.__name__ == data["__classname__"]:
                            # Counting the number of parameters of the class constructor and then creating an instance of the class
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

                            # Save this object so we don't have to create it again later.
                            temp[data["__classid__"]] = ret_cls

                            # Restore all saved attributes of the class
                            for attr, value in data.items():
                                try:
                                    if attr == "__classname__" or attr == "__classid__":
                                        continue
                                    setattr(ret_cls, attr, _parse(value, args, temp))
                                except AttributeError:
                                    pass

                            return ret_cls
            raise RuntimeError(
                f"The required class template is not found in 'args' argument that restore an instance of {data['__classname__']} class"
            )

    if isinstance(data, (list, tuple, dict, set, frozenset)):
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                result[_parse(key, args, temp)] = _parse(value, args, temp)
            return result

        elif isinstance(data, list):
            result = []
            for item in data:
                result.append(_parse(item, args, temp))
            return result

        elif isinstance(data, tuple):
            temp = []
            for item in data:
                temp.append(_parse(item, args, temp))
            return tuple(temp)

        elif isinstance(data, set):
            result = set()
            for item in data:
                result.add(_parse(item, args, temp))
            return result

        elif isinstance(data, frozenset):
            temp = set()
            for item in data:
                temp.add(_parse(item, args, temp))
            return frozenset(temp)
        else:
            raise TypeError("Unsupported container type.")

    return data


def load(source: Optional[Union[TextIO, str]], args: Optional[object] = None) -> Any:
    """
    Loads and parses data from a file or a string.

    Args:
        source (Optional[Union[TextIO, str]]): A file object or a string containing the saved data.
        args (Optional[object]): Optional argument (typically a tuple of classes) used to reconstruct custom object instances.

    Returns:
        Any: The reconstructed Python object.
    """

    if isinstance(source, str):
        data = literal_eval(source)
    else:
        source.seek(0)
        line = source.read()

        data = literal_eval(line)

    # Storage for intermediate results during parsing
    temp = {}

    return _parse(data, args, temp)


def save_s(file: Optional[TextIO], data, key: Union[str, int]) -> Optional[str]:
    """
    Saves data in encrypted form using PyCryptodome.

    Arguments:
      file: A file object (TextIO) to write the encrypted data to, or None if the encrypted string should be returned.
      data: The data to be saved. Supported types include: list, tuple, dict, set, frozenset, str, int, float, bool,
            an object whose constructor parameters correspond to its attributes, or None.
      key:  The encryption key (can be provided as a str or int).

    Returns:
      If file is not None, writes the encrypted data into the file and returns None.
      Otherwise, returns the base64-encoded encrypted string.
    """
    if not is_supported_data_type(data):
        raise TypeError(
            "Argument 'data' must be of type list, tuple, dict, set, frozenset, str, int, float, bool or object or NoneType.\nIf data is an object, then the class of which data is an instance must have a constructor with parameters whose value is stored in the class attributes."
        )

    # Storage for intermediate results during conversion
    temp = {}

    if isinstance(data, str):
        data = _convert_data(data, None, temp)
        if data.find("\n") != -1:
            data = f'"""{data}"""'
        else:
            data = f'"{data}"'
    elif isinstance(data, (int, float, bool)):
        data = str(_convert_data(data, None, temp))
    elif isinstance(data, (list, tuple, dict, set, frozenset)):
        data = str(_convert_data(data, None, temp))
    elif data is None:
        data = str(_convert_data(data, None, temp))
    else:
        data = str(_convert_data(data, None, temp))

    key = hashlib.sha256(str(key).encode("UTF-8")).digest()

    cipher = AES.new(key, AES.MODE_EAX)
    cipher_text, tag = cipher.encrypt_and_digest(data.encode("UTF-8"))
    encrypted_bytes = cipher.nonce + tag + cipher_text
    encrypted_str = base64.b64encode(encrypted_bytes).decode("UTF-8")

    if file:
        file.seek(0)
        file.write(encrypted_str)
    else:
        return encrypted_str


def load_s(
    source: Optional[Union[TextIO, str]], key, args: Optional[object] = None
) -> Any:
    """
    Loads encrypted data, decrypts it, and returns the original object.

    Arguments:
      source: A file object or a string containing the encrypted data (base64-encoded).
      key:    The encryption key (can be provided as a str or int).
      args:   Optional additional arguments to be passed to _parse (if necessary).

    Returns:
      The decrypted data is converted to the original object
    """

    if isinstance(source, str):
        encrypted_data = source
    else:
        source.seek(0)
        encrypted_data = source.read()

    key = hashlib.sha256(str(key).encode("UTF-8")).digest()

    encrypted_bytes = base64.b64decode(encrypted_data)

    nonce, tag, cipher_text = (
        encrypted_bytes[:16],
        encrypted_bytes[16:32],
        encrypted_bytes[32:],
    )

    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)

    try:
        decrypted_bytes = cipher.decrypt_and_verify(cipher_text, tag)
    except ValueError:
        raise ValueError("Incorrect key or corrupted data")

    decrypted_str = decrypted_bytes.decode("UTF-8")

    # Convert the decrypted string back to a data object (using literal_eval for safety)
    data = literal_eval(decrypted_str)

    # Storage for intermediate results during parsing
    temp = {}
    return _parse(data, args, temp)
