import os
import sys
from collections.abc import Iterator
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from persistify.persistify import save, load

data = [1, 2, 3, 4, 5, "end", {"Name": "admin", "password": "admin"}]

file = os.path.join(os.path.dirname(__file__), "example1.data")

if not os.path.exists(file):
    with open(file, "w", encoding="UTF-8") as f:
        #save(f, data, indent=4, expand=True)
        save(f, data)
else:
    with open(file, "r", encoding="UTF-8") as f:
        loaded_data = load(f)
        print(f"Data is {loaded_data} Type: {type(loaded_data)}")

        for element in loaded_data:
            if isinstance(element, Iterator) or isinstance(element, dict):
                for subelement in element:
                    print(f"\tElement{type(element)} - SubElement{type(subelement)}: {subelement}.")
            else:
                print(f"Element{type(element)}: {element}.")

            