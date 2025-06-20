# Persistify

Persistify is a Python library for saving Python data structures as valid Python code.  
It allows you to serialize various data types (lists, dictionaries, sets, custom objects, etc.) into a human‐readable string format that can later be evaluated back into the original Python objects.

## Features

- **Data Serialization:** Converts common Python data structures into executable Python code.
- **Custom Object Support:** Automatically handles serialization of custom objects with simple constructor signatures.
- **Readable Format:** The generated code is formatted in a way that makes it easy to understand and modify if necessary.
- **Secure Persistence (Optional):** With additional secure functions (e.g. using encryption), you have the option to safely store sensitive data.

## Installation

Clone the repository and install the package:

## Examples

You can find examples of using Persistify in the 'example' folder.

```bash
git clone https://github.com/SuperWhiteDev/Persistify.git
cd Persistify
pip install .
```