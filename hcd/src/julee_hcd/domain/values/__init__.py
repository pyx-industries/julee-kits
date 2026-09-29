"""What hcd is made of but does not keep.

A value object has no identity (ADR 018). A JourneyStep is one step of
one journey; an ExternalDependency is something outside that an
integration needs. Neither has an id and no repository keeps either.

hcd's entities -- App, Epic, Journey, Persona, Story, Integration and
ContribModule -- stay in domain/models/, along with Authored, the base
they share.
"""
