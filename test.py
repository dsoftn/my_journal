def  get_translated_list(str_list):
    return [int(x.split(":")[0])*60 + int(x.split(":")[1]) for x in str_list if x != ""]


def time_scheduler(p1sch, p2sch, p1bound, p2bound):
    p1s = get_translated_list(p1sch)
    p2s = get_translated_list(p2sch)
    p1b = get_translated_list(p1bound)
    p2b = get_translated_list(p2bound)

    p12s = p1s + p2s
    p12s.sort()


print (123 % 60)
