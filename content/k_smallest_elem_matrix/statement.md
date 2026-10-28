Given an n x n matrix whose rows and columns are each sorted in ascending
order, return the k-th smallest element in the matrix (1-indexed).

Example 1:
Input:
matrix = [[1, 4, 7],
          [3, 5, 9],
          [6, 8, 11]]
k = 4
Output: 5
Explanation: the elements in sorted order are [1, 3, 4, 5, 6, 7, 8, 9, 11];
the 4th is 5.

Constraints:
1 <= k <= n * n

Both rows and columns are sorted — a heap over the first k rows and columns
avoids flattening and sorting the entire matrix.

You should aim for a solution with O(k log k) time and O(k) space, where k is
the rank asked for (flattening and sorting the whole matrix is O(n^2 log n)).
