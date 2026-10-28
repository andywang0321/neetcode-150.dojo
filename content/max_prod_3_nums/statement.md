Given an integer array with at least three elements, return the maximum
product of any three numbers in the array. Elements may be negative, and the
answer itself may be negative.

Example 1:
Input: A = [1, 3, 4, 5]
Output: 60
Explanation: 3 * 4 * 5 = 60.

Example 2:
Input: B = [-2, -4, 5, 3]
Output: 40
Explanation: -2 * -4 * 5 = 40 — two large negatives can beat two positives.

You should aim for a solution with O(n log n) time and O(1) space, where n is
the length of the array. (A single pass tracking the three largest and two
smallest values gives O(n) time.)
