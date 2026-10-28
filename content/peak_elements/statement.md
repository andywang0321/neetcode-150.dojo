Given an array of positive integers, a peak element is one that is greater
than both of its neighbors (an endpoint only needs to beat its single
neighbor). Return the index of any peak element in the array.

Example 1:
Input: [3, 5, 2, 4, 1]
Output: 1 (value 5) or 3 (value 4) — either peak is correct.

Example 2:
Input: [4, 3, 2, 1]
Output: 0

Example 3:
Input: [1, 2, 3, 4]
Output: 3

You should aim for a solution with O(log n) time and O(1) space, where n is
the length of the array. (Why does comparing an element with one neighbor
always let you halve the search space?)
