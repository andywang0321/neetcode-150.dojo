Given a target integer, a sample size n, and a real number sigma >= 0,
generate a list of exactly n integers such that:

- the elements sum exactly to the target, and
- the sample's standard deviation does not exceed sigma.

The generator may be random — any list meeting both conditions is a correct
answer. Different runs may return different lists.

Example 1:
Input: n = 5, sigma = 3.6, target = 6
Output: any list of 5 integers summing to 6 whose standard deviation is at
most 3.6.

You should aim for a solution with O(n) time and O(n) space, where n is the
sample size (any valid sample is accepted; the checker verifies the sum and the
standard deviation, never a particular list).
