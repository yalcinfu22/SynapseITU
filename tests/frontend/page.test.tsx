import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import Home from "@/app/page";

afterEach(cleanup);

describe("landing page", () => {
  it("renders the SynapseITU heading", () => {
    render(<Home />);
    expect(
      screen.getByRole("heading", { level: 1, name: "SynapseITU" }),
    ).toBeTruthy();
  });
});
