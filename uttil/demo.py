list1 = ["www", "bbbbb", "pppp"]
print(list1.index("bbbbb"))
print(list1[1])
list2 = ["oooooo", "ppppppp", "eeeeeeee"]
list1.extend(list2)
print(list1)
list2.insert(1, "4444")
print(list2)
aaa = "test.txt"
bbb = aaa.split(".")
print(bbb)

list3 = [1, 1, 2, 3, 4, 6, 6, 2, 2, 9]
lists = list(set(list3))
print(lists)
list4 = ["a", "b", "c"]
print(list4[::-1])
