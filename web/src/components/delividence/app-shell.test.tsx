// @vitest-environment jsdom

import { cleanup, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { AppShell } from "./app-shell";

vi.mock("next/navigation", () => ({
  usePathname: () => "/workspace",
  useRouter: () => ({ push: vi.fn() }),
}));

afterEach(cleanup);

describe("AppShell sign-out flow", () => {
  it("asks for confirmation and cancels without signing out", async () => {
    const onSignOut = vi.fn();
    const user = userEvent.setup();
    render(<AppShell onSignOut={onSignOut} onNewRecord={() => undefined}>Content</AppShell>);

    await user.click(screen.getAllByRole("button", { name: "Sign out" })[0]);
    expect(screen.getByRole("alertdialog", { name: "Sign out of Delividence?" })).toBeTruthy();
    await user.click(screen.getByRole("button", { name: "Cancel" }));

    expect(screen.queryByRole("alertdialog")).toBeNull();
    expect(onSignOut).not.toHaveBeenCalled();
  });

  it("runs sign-out only after explicit confirmation", async () => {
    const onSignOut = vi.fn().mockResolvedValue(undefined);
    const user = userEvent.setup();
    render(<AppShell onSignOut={onSignOut} onNewRecord={() => undefined}>Content</AppShell>);

    await user.click(screen.getAllByRole("button", { name: "Sign out" })[0]);
    await user.click(within(screen.getByRole("alertdialog")).getByRole("button", { name: "Sign out" }));

    await waitFor(() => expect(onSignOut).toHaveBeenCalledOnce());
    expect(screen.queryByRole("alertdialog")).toBeNull();
  });

  it("keeps the dialog open and explains a failed sign-out", async () => {
    const onSignOut = vi.fn().mockRejectedValue(new Error("Network unavailable"));
    const user = userEvent.setup();
    render(<AppShell onSignOut={onSignOut} onNewRecord={() => undefined}>Content</AppShell>);

    await user.click(screen.getAllByRole("button", { name: "Sign out" })[0]);
    await user.click(within(screen.getByRole("alertdialog")).getByRole("button", { name: "Sign out" }));

    expect((await screen.findByRole("alert")).textContent).toContain("Network unavailable");
    expect(screen.getByRole("alertdialog")).toBeTruthy();
  });
});
