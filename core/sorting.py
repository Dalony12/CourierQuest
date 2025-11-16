def merge_sort(arr, key_func):
    # Ordenamiento Merge Sort usando una función clave personalizada
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid], key_func)
    right = merge_sort(arr[mid:], key_func)
    return merge(left, right, key_func)


def merge(left, right, key_func):
    # Mezclar dos listas ya ordenadas según la clave
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if key_func(left[i]) <= key_func(right[j]):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def heap_sort(arr, key_func):
    import heapq
    # Ordenamiento usando heap mínimo basado en la clave
    heap = [(key_func(item), i, item) for i, item in enumerate(arr)]
    heapq.heapify(heap)

    sorted_arr = []
    while heap:
        sorted_arr.append(heapq.heappop(heap)[2])
    return sorted_arr