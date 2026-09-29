"""What polling is made of.

Every class here is a value object: no identity, so nothing keeps one and
no port is bound to one (ADR 018). polling has no repository at all — it
orchestrates a poll and keeps nothing — so it has no entities, and this
directory is the whole of its domain vocabulary.
"""
