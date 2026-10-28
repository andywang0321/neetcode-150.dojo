Given a binary tree, return true if the tree is a mirror image of itself. A
tree is symmetric when its left and right subtrees are mirror images of each
other: their root values are equal, and the left subtree of one mirrors the
right subtree of the other (and vice versa).

Example 1: a tree whose root is 3, whose left child 2 has children 1 and 2,
and whose right child 2 has children 2 and 1, is symmetric -> true.

Example 2: a tree whose root is 3, whose left child 2 has children 1 and 2,
and whose right child 4 has children 1 and 1, is not symmetric -> false.

You should aim for a solution with O(n) time and O(n) space, where n is the
number of nodes.

Input format: the tree is passed as a nested list [value, left, right], where
left and right are either None or nested lists. An empty tree is None.
