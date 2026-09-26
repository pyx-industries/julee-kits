import { describe, expect, it } from "vitest";

import { configHelpers } from "./config";

/**
 * The config helpers turn a base URL and an endpoint into the URLs this
 * UI calls. Small, pure, and the one place a leading slash is decided,
 * which is the part worth pinning down.
 */
describe("getApiUrl", () => {
  it("joins an endpoint that names its own leading slash", () => {
    expect(configHelpers.getApiUrl("/health")).toMatch(/\/health$/);
  });

  it("adds the slash an endpoint leaves out", () => {
    expect(configHelpers.getApiUrl("health")).toBe(
      configHelpers.getApiUrl("/health"),
    );
  });

  it("does not double a slash that is already there", () => {
    expect(configHelpers.getApiUrl("/health")).not.toMatch(/\/\/health$/);
  });

  it("keeps the rest of a nested path intact", () => {
    expect(configHelpers.getApiUrl("knowledge_service_queries/42")).toMatch(
      /\/knowledge_service_queries\/42$/,
    );
  });

  it("builds on the same base every other helper uses", () => {
    expect(configHelpers.getApiUrl("/health")).toBe(
      `${configHelpers.getApiBaseUrl()}/health`,
    );
  });
});

describe("the documented endpoints", () => {
  it("puts docs under the API base", () => {
    expect(configHelpers.getApiDocsUrl()).toBe(
      `${configHelpers.getApiBaseUrl()}/docs`,
    );
  });

  it("puts health under the API base", () => {
    expect(configHelpers.getHealthUrl()).toBe(
      `${configHelpers.getApiBaseUrl()}/health`,
    );
  });

  it("keeps Temporal's web UI on its own host", () => {
    expect(configHelpers.getTemporalWebUrl()).not.toBe(
      configHelpers.getApiBaseUrl(),
    );
  });
});
