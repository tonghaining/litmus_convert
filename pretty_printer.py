def pretty_print(thread_map):
    res = ""
    column_width = max([len(instruction) for thread in thread_map for instruction in thread_map[thread]]) + 5
    column_length = max([len(thread_map[thread]) for thread in thread_map])
    # print thread header
    for tid in list(thread_map.keys())[:-1]:
        extension_width = column_width - len(tid)
        res += f"{tid}" + " " * extension_width + " | "
    last_tid = list(thread_map.keys())[-1]
    last_extension_width = column_width - len(last_tid)
    res += f"{last_tid}" + " " * last_extension_width + " ;"
    res += "\n"
    # print thread instructions
    for i in range(column_length):
        for tid in list(thread_map.keys())[:-1]:
            if i < len(thread_map[tid]):
                extension_width = column_width - len(thread_map[tid][i])
                res += f"{thread_map[tid][i]}" + " " * extension_width + " | "
            else:
                res += " " * column_width + " | "
        last_tid = list(thread_map.keys())[-1]
        if i < len(thread_map[last_tid]):
            last_extension_width = column_width - len(thread_map[last_tid][i])
            res += f"{thread_map[last_tid][i]}" + " " * last_extension_width + " ;"
        else:
            res += " " * column_width + " ;"
        res += "\n"
    return res
