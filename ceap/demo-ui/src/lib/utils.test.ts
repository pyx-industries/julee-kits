import { describe, expect, it } from "vitest";

import { cn } from "./utils";

/**
 * `cn` is how every component composes class names: clsx for the
 * conditional part, tailwind-merge for the conflicting part. The second
 * half is the one that would break silently, because a component with
 * two conflicting classes still renders.
 */
describe("cn", () => {
  it("joins plain class names", () => {
    expect(cn("a", "b")).toBe("a b");
  });

  it("drops a falsy class rather than printing it", () => {
    const active = false;

    expect(cn("a", active && "b", undefined, null)).toBe("a");
  });

  it("takes the conditional object form", () => {
    expect(cn({ a: true, b: false })).toBe("a");
  });

  it("lets the last of two conflicting tailwind classes win", () => {
    expect(cn("p-2", "p-4")).toBe("p-4");
  });

  it("keeps classes that do not conflict", () => {
    expect(cn("p-2", "text-sm")).toBe("p-2 text-sm");
  });

  it("is empty when given nothing", () => {
    expect(cn()).toBe("");
  });
});
