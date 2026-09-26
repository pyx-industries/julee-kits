/**
 * The shape of a JSON Schema node as this UI reads it.
 *
 * Deliberately open: a schema node carries whatever keywords its author
 * wrote, and the editor reads a handful of them without claiming to model
 * the whole vocabulary. Naming the type is still worth it — it says the
 * value is a schema node rather than leaving it to an untyped `get`.
 */
export interface JsonSchemaNode {
  title?: string;
  description?: string;
  type?: string;
  properties?: Record<string, JsonSchemaNode>;
  items?: JsonSchemaNode;
  required?: string[];
  enum?: unknown[];
  const?: unknown;
  default?: unknown;
  minLength?: number;
  maxLength?: number;
  pattern?: string;
  minimum?: number;
  maximum?: number;
  multipleOf?: number;
  minItems?: number;
  maxItems?: number;
  [keyword: string]: unknown;
}
