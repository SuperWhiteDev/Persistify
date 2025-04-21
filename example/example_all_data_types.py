import os
import sys
import shutil
import unittest
from random import randint

from persistify.persistify import save, load

class RandomAccessClass:
    statis_attribute_1 = None

    def __init__(self, num : int, string : str, elist : list) -> None:
        self.num = num
        self.string = string
        self.elist = elist
    
    def __str__(self) -> str:
        return f"RandomAccessClass object: num={self.num}, string={self.string}, elist={self.elist}."

class RandomAccessClassChild:
    def __init__(self, parent: list[RandomAccessClass]) -> None:
        self.parent = parent
        self.parent_iter = 0
        self.unique_id = randint(10**8, 10**9)
    def get_parent(self, id : int = None) -> RandomAccessClass:
        if id == None:
            parent = self.parent[self.parent_iter]
        
            self.parent_iter += 1
            if self.parent_iter >= len(self.parent):
                self.parent_iter = 0
            return parent
        else:
            return self.parent[id]
        
class TestPersistyfy(unittest.TestCase):
    def setUp(self) -> None:
        self.data_dir = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(self.data_dir, exist_ok=True)

        self.data_list_file = os.path.join(self.data_dir, "list_data.data")
        self.data_dict_file = os.path.join(self.data_dir, "dict_data.data")
        self.data_set_file = os.path.join(self.data_dir, "set_data.data")
        self.data_string_file = os.path.join(self.data_dir, "string_data.data")
        self.data_multi_string_file = os.path.join(self.data_dir, "multi_string_data.data") 
        self.data_number_file = os.path.join(self.data_dir, "number_data.data")
        self.data_object_file = os.path.join(self.data_dir, "object_data.data")
        self.data_2_object_file = os.path.join(self.data_dir, "object_2_data.data")

    # def tearDown(self) -> None:
    #     if os.path.exists(self.data_dir):
    #         shutil.rmtree(self.data_dir)

    
    def test_data_list(self):
        data = [1, None, "String", ("Data", "(In list)", 1), {"data": None}, [True, False], {1, 2, 5, 8, 11}]
    
        with open(self.data_list_file, "w") as f:
            save(f, data, indent=4)

        with open(self.data_list_file) as f:
            loaded_data = load(f)

        self.assertEqual(data, loaded_data)

    def test_data_dict(self):
        data = {1: 1, 0:0, "Is dictionary": True, "list": [1, 2, 3], "settings": {"toggle": True}}

        with open(self.data_dict_file, "w") as f:
            save(f, data, indent=4)

        with open(self.data_dict_file) as f:
            loaded_data = load(f)
        
        self.assertEqual(data, loaded_data)
    def test_data_set(self):
        k = 4.12
        data = set([i+k for i in range(-4, 50)])

        with open(self.data_set_file, "w") as f:
            save(f, data, indent=4)

        with open(self.data_set_file) as f:
            loaded_data = load(f)
        
        self.assertEqual(data, loaded_data)

    def test_data_number(self):
        data = randint(-999**10, 999**10)

        with open(self.data_number_file, "w") as f:
            save(f, data)

        with open(self.data_number_file) as f:
            loaded_data = load(f)
        
        self.assertEqual(data, loaded_data)

    def test_data_string(self):
        data = "This is string: "
    
        for _ in range(100):
            data += str(randint(0, 1_000_000))

        with open(self.data_string_file, "w") as f:
            save(f, data)

        with open(self.data_string_file) as f:
            loaded_data = load(f)
        
        self.assertEqual(data, loaded_data)


    def test_data_multi_string(self):
        data = """
            This is 
            Multiline string."""

        with open(self.data_multi_string_file, "w") as f:
            save(f, data)
        
        with open(self.data_multi_string_file) as f:
            loaded_data = load(f)

        self.assertEqual(data, loaded_data)

    def test_data_object(self):
        data = RandomAccessClass(randint(-1, 1), "RAC", [None, "Random", "Access", "Memory", None])
        data.statis_attribute_1 = "Correct"

        with open(self.data_object_file, "w") as f:
            save(f, data)
        
        with open(self.data_object_file) as f:
            obj = load(f, (RandomAccessClass,))

        self.assertIsInstance(obj, RandomAccessClass)
        self.assertEqual(str(data), str(obj))
        self.assertEqual(data.statis_attribute_1, obj.statis_attribute_1)

    def test_data_object_2(self):
        data = RandomAccessClassChild([RandomAccessClass(randint(-100, 100), "RAC", [None, "Random", "Access", "Memory", None])])
    
        with open(self.data_2_object_file, "w") as f:
            save(f, data)    

        with open(self.data_2_object_file) as f:
            obj = load(f, (RandomAccessClassChild, RandomAccessClass))

        self.assertIsInstance(obj, RandomAccessClassChild)
        self.assertIsInstance(obj.get_parent(0), RandomAccessClass)

        self.assertEqual(str(data.get_parent()), str(obj.get_parent()))
        self.assertEqual(data.unique_id, obj.unique_id)

if __name__ == "__main__":
    unittest.main() 