from typing import List, Tuple, Any

def recursive_zip(list1: List, list2: List, shape: Tuple[int, ...]) -> List:
    """
    Recursively zip two lists according to a shape tuple.
    
    Args:
        list1: First list to zip
        list2: Second list to zip
        shape: Tuple describing the expected shape of the input lists
        
    Returns:
        List: Recursively zipped lists according to the shape
        
    Raises:
        ValueError: If the lists don't match the expected shape
    """
    def validate_shape(lst: List, expected_shape: Tuple[int, ...]) -> bool:
        if not isinstance(lst, list):
            return False
        
        if not expected_shape:
            return True
            
        if len(lst) != expected_shape[0]:
            return False
            
        if len(expected_shape) == 1:
            return True
            
        return all(validate_shape(item, expected_shape[1:]) for item in lst)
    
    def get_actual_shape(lst: List) -> Tuple[int, ...]:
        if not isinstance(lst, list):
            return tuple()
        if not lst:
            return (0,)
        return (len(lst),) + get_actual_shape(lst[0])
    
    # Validate input shapes
    if not validate_shape(list1, shape) or not validate_shape(list2, shape):
        actual_shape1 = get_actual_shape(list1)
        actual_shape2 = get_actual_shape(list2)
        raise ValueError(
            f"Lists don't match expected shape {shape}. "
            f"Actual shapes: list1{actual_shape1}, list2{actual_shape2}"
        )
    
    # Base case: if shape is empty or has only one dimension
    if not shape or len(shape) == 1:
        return list(zip(list1, list2))
    
    # Recursive case: zip current level and apply to all sublists
    return [
        recursive_zip(l1, l2, shape[1:])
        for l1, l2 in zip(list1, list2)
    ]


# Simple 2D example
list1 = [[1, 2], [3, 4]]
list2 = [[5, 6], [7, 8]]
shape = (2, 2)
result = recursive_zip(list1, list2, shape)
print(result)  # [[(1, 5), (2, 6)], [(3, 7), (4, 8)]]

# 3D example
list1 = [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]
list2 = [[[9, 10], [11, 12]], [[13, 14], [15, 16]]]
shape = (2, 2, 2)
result = recursive_zip(list1, list2, shape)
print(result)  # [[[(1, 9), (2, 10)], [(3, 11), (4, 12)]], [[(5, 13), (6, 14)], [(7, 15), (8, 16)]]]
