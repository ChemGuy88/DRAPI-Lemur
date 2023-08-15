"""
Test suite for `makeSetComplement`

Pseudocode draft for `makeSetComplement`:

Get set of all used numbers, s1
Get set of range from 0 to max of all used numbers, s1c
Get set difference from the two above sets, sd
Get the cardinality of the new numbers you need, qnew
Subtract from that cardinality the cardinality of the set difference from above, this the contiguous part of the set complement, qnewc
if qnewc is > 0, create the set of range from max of all used numbers to max + qnewc, snewc
union sd and snewc, call this sfinal
return sfinal
"""

from Code.drapi.drapi import makeSetComplement


# Test suite 1
if True:
    oldSet1 = set([1, 2, 3, 4, 5])
    oldSet2 = set([3, 4, 5])
    oldSet3 = set([1, 3, 5])
    for cardinalityOfNewSet in [-2, -1, 0, 1, 2, 3]:
        indentFactor = 2
        print(f"""{" " * indentFactor}`cardinalityOfNewSet`: {cardinalityOfNewSet}.""")
        for set1 in [oldSet1, oldSet2, oldSet3]:
            indentFactor = 4
            print(f"""{" " * indentFactor}`set1`: {set1}.""")
            # Function
            if cardinalityOfNewSet < 1:
                print(f"""{" " * indentFactor}`cardinalityOfNewSet` must be greater than 0.""")
            elif cardinalityOfNewSet > 0:
                set1Min = 1
                print(f"""{" " * indentFactor}`set1Min`: {set1Min}.""")
                set1Max = max(set1)
                print(f"""{" " * indentFactor}`set1Max`: {set1Max}.""")
                s1Contiguous = set(range(set1Min, set1Max + 1))
                print(f"""{" " * indentFactor}`s1Contiguous`: {s1Contiguous}.""")
                setDifference = s1Contiguous.difference(set1)
                print(f"""{" " * indentFactor}`setDifference`: {setDifference}.""")
                cardinalityOfSetDifference = len(setDifference)
                print(f"""{" " * indentFactor}`cardinalityOfSetDifference`: {cardinalityOfSetDifference}.""")
                cardinalityOfContiguousSubset = cardinalityOfNewSet - cardinalityOfSetDifference
                print(f"""{" " * indentFactor}`cardinalityOfContiguousSubset`: {cardinalityOfContiguousSubset}.""")
                if cardinalityOfContiguousSubset > 0:
                    setDifferenceSubset = setDifference
                    contiguousSubset = set(range(set1Max + 1, set1Max + cardinalityOfContiguousSubset + 1))
                elif cardinalityOfContiguousSubset == 0:
                    setDifferenceSubset = setDifference
                    contiguousSubset = set()
                elif cardinalityOfContiguousSubset < 0:
                    setDifferenceSubset = set(list(setDifference)[:cardinalityOfNewSet])
                    contiguousSubset = set()
                print(f"""{" " * indentFactor}`contiguousSubset`: {contiguousSubset}.""")
                newSet = setDifferenceSubset.union(contiguousSubset)
                newSet = sorted(list(newSet))
                print(f"""{" " * indentFactor}`newSet`: {newSet}.""")
            print()

# Test suite 2
if True:
    oldSet1 = set([1, 2, 3, 4, 5])
    oldSet2 = set([3, 4, 5])
    oldSet3 = set([1, 3, 5])
    for cardinalityOfNewSet in [-2, -1, 0, 1, 2, 3]:
        indentFactor = 2
        print(f"""{" " * indentFactor}`cardinalityOfNewSet`: {cardinalityOfNewSet}.""")
        for set1 in [oldSet1, oldSet2, oldSet3]:
            indentFactor = 4
            print(f"""{" " * indentFactor}`set1`: {set1}.""")
            newSet = makeSetComplement(set1, cardinalityOfNewSet)
            print(sorted(list(newSet)))
