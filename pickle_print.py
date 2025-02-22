#!/usr/bin/env python3

import sys
import pickle
import pprint

from inspect_instance import inspect_object, A
from inspect_inheritance import get_class_details

def main():
    if len(sys.argv) != 2:
        print("Usage: python inspect_pickle.py <pickle_file>")
        sys.exit(1)

    pickle_file = sys.argv[1]

    try:
        with open(pickle_file, 'rb') as f:
            data = pickle.load(f)
        # pprint.pprint(data)
        
        get_class_details(data.__class__)
        inspect_object(data)
    except Exception as e:
        print(f"Error loading pickle file: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

# python pickle_print.py your_pickle_file.pkl
