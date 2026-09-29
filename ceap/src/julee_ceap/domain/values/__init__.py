"""What ceap is made of but does not keep.

A value object has no identity (ADR 018). A JsonSchema is a schema, an
AssembledData is what came out of one, a QueryResult is what a knowledge
service answered, a DocumentSeed is what a document is made from, and a
ContentMultihash is what some bytes hash to. Two of any of these with
the same contents are the same one, so no repository keeps them and no
driven port is bound to them.

ceap's entities — Document, Assembly, AssemblySpecification,
KnowledgeServiceQuery, KnowledgeServiceConfig, Policy and
DocumentPolicyValidation — stay in domain/models/.
"""
