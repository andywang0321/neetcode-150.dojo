"""The private assessment tree: cases, oracles, references and measurement plans.

Every module here is quarantined. It never reaches a student, the tutor, the teacher
or the leak auditor. It registers with `neetcode_dojo.registry`, the local decorator
surface that replaced the old engine import.
"""
