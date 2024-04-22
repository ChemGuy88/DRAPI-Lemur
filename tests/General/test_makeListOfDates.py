from drapi.code.drapi.makeListOfDates import makeListOfDates

TEST_CASES = [('2012-01-01', '2012-02-01', 1),
              ('2012-01-01', '2012-02-01', 6),
              ('2012-01-01', '2013-01-01', 1),
              ('2012-01-01', '2013-02-01', 6),
              ('2012-01-01', '2012-03-01', 6)]

for start, end, periodValue in TEST_CASES:
    print(makeListOfDates(start=start,
                          end=end,
                          period="M",
                          periodValue=periodValue))
