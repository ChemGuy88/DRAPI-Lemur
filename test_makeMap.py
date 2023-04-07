"""
"""

from hermanCode.hermanCode import makeMap

map1 = makeMap(IDset=set([1, 2, 3]),
               IDName="varName",
               startFrom=1,
               irbNumber="123456789",
               suffix="_sfx",
               columnSuffix="_vsfx")

map2 = makeMap(IDset=set([1, 2, 3]),
               IDName="varName",
               startFrom=[11, 12, 13],
               irbNumber="123456789",
               suffix="_sfx",
               columnSuffix="_vsfx")

map3 = makeMap(IDset=set(),
               IDName="varName",
               startFrom=[11, 12, 13],
               irbNumber="123456789",
               suffix="_sfx",
               columnSuffix="_vsfx")

map4 = makeMap(IDset=set(),
               IDName="varName",
               startFrom=1,
               irbNumber="123456789",
               suffix="_sfx",
               columnSuffix="_vsfx")

map5 = makeMap(IDset=set(),
               IDName="varName",
               startFrom=[0],
               irbNumber="123456789",
               suffix="_sfx",
               columnSuffix="_vsfx")


print(map1)

print(map2)

print(map3)
