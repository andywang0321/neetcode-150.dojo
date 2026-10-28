Given a binary tree, return the length of its diameter: the longest path
between any two nodes in the tree, measured in number of edges. The path may
or may not pass through the root.

Example 1:
Input: a tree whose root is 0, with left child 1 (children 2 and 2) and right
child 1 (right child 2); the left-most 2 has a right child 3 and the
right-most 2 has a left child 3.
Output: 6
Explanation: the longest path runs from one 3, up through the root, to the
other 3 — six edges.

Example 2:
Input: a single node.
Output: 0

Example 3:
Input: root 0 with left child 1, which has right child 2.
Output: 2

You should aim for a solution with O(n) time and O(n) space, where n is the
number of nodes.

Input format: the tree is passed as a nested list [value, left, right], where
left and right are either None or nested lists. The tree is never empty.
