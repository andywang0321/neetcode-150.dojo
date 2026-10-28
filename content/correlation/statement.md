Given two lists X and Y of equal length, return the Pearson correlation
coefficient between them:

    corr = (E[XY] - E[X] * E[Y]) / (SD(X) * SD(Y))

where E denotes the mean and SD the population standard deviation.

Example 1:
Input: X = [1, 2, 3, 4, 5], Y = [3, 2, 5, 9, 6]
Output: 0.7506 (rounded to four decimals)

You should aim for a solution with O(n) time and O(1) space, where n is the
length of the lists.
