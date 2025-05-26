# Draw a Tree?
#       *
#      ***
#     *****
#    *******
#   *********
#  *********** 11
#       *

# height = 6
# 6 * 2 = 12 - 1 = 11

def tree(height):
    length = height * 2 -1
    stars = 1
    for i in range(1, height +1 ):
        print(("*" * stars).center(length))
        stars += 2
    print("*".center(length))

tree(9)
    