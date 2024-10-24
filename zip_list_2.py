from typing import List, Tuple, Any
from collections import deque

def iterative_zip(list1: List, list2: List, shape: Tuple[int, ...]) -> List:
    """
    Iteratively zip two lists according to a shape tuple.
    
    Args:
        list1: First list to zip
        list2: Second list to zip
        shape: Tuple describing the expected shape of the input lists
        
    Returns:
        List: Zipped lists according to the shape
        
    Raises:
        ValueError: If the lists don't match the expected shape
    """
    def validate_shape(lst: List, expected_shape: Tuple[int, ...]) -> bool:
        current = lst
        for dim in expected_shape:
            if not isinstance(current, list) or len(current) != dim:
                return False
            if current:
                current = current[0]
        return True
    
    def get_actual_shape(lst: List) -> Tuple[int, ...]:
        shape_list = []
        current = lst
        while isinstance(current, list):
            shape_list.append(len(current))
            if not current:
                break
            current = current[0]
        return tuple(shape_list)
    
    # Validate input shapes
    if not validate_shape(list1, shape) or not validate_shape(list2, shape):
        actual_shape1 = get_actual_shape(list1)
        actual_shape2 = get_actual_shape(list2)
        raise ValueError(
            f"Lists don't match expected shape {shape}. "
            f"Actual shapes: list1{actual_shape1}, list2{actual_shape2}"
        )
    
    if not shape:
        return list(zip(list1, list2))
    
    # Initialize result with the same structure
    result = []
    
    # Use a queue to keep track of the current position in each list
    # Each queue item is (list1_part, list2_part, current_depth, parent_list, index_in_parent)
    queue = deque([(list1, list2, 0, None, None)])
    
    while queue:
        l1, l2, depth, parent, idx = queue.popleft()
        
        # If we're at the last dimension, zip the current lists
        if depth == len(shape) - 1:
            current_result = list(zip(l1, l2))
            if parent is None:
                result = current_result
            else:
                parent[idx] = current_result
        else:
            # Create a new list for this level
            current_result = [[] for _ in range(shape[depth])]
            if parent is None:
                result = current_result
            else:
                parent[idx] = current_result
                
            # Add sublists to the queue
            for i in range(shape[depth]):
                queue.append((l1[i], l2[i], depth + 1, current_result, i))
    
    return result

# 2D example
list1 = [[1, 2], [3, 4]]
list2 = [[5, 6], [7, 8]]
shape = (2, 2)
result = iterative_zip(list1, list2, shape)
print(result)  # [[(1, 5), (2, 6)], [(3, 7), (4, 8)]]

# 3D example
list1 = [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]
list2 = [[[9, 10], [11, 12]], [[13, 14], [15, 16]]]
shape = (2, 2, 2)
result = iterative_zip(list1, list2, shape)
print(result)  # [[[(1, 9), (2, 10)], [(3, 11), (4, 12)]], [[(5, 13), (6, 14)], [(7, 15), (8, 16)]]]
