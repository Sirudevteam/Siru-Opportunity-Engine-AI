import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StatusBadge } from "./status-badge";

describe("StatusBadge", () => {
  it("renders title cased status text", () => {
    render(<StatusBadge value="very_hot" />);
    expect(screen.getByText("Very Hot")).toBeInTheDocument();
  });
});
