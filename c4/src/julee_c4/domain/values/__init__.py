"""What c4 is made of but does not keep.

A value object has no identity (ADR 018). The six diagrams are
assembled on demand from elements that do have identity, and a
ContainerInstance is one container running on one node. Nothing keeps
any of them under an id.

c4's entities -- Component, Container, DeploymentNode, DynamicStep,
Relationship and SoftwareSystem -- stay in domain/models/.
"""
