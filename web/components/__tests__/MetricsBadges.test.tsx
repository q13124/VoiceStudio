import { render, screen } from "@testing-library/react";
import { MetricsBadges } from "../MetricsBadges";

test("renders LUFS and clip badges when provided", () => {
  render(<MetricsBadges m={{ lufs: -24.2, clip_pct: 0.2 }} />);
  expect(screen.getByText("LUFS")).toBeInTheDocument();
  expect(screen.getByText("-24.2")).toBeInTheDocument();
  expect(screen.getByText("clip")).toBeInTheDocument();
});

test("renders warning tone for LUFS outside target range", () => {
  render(<MetricsBadges m={{ lufs: -30.0 }} />);
  const lufsBadge = screen.getByText("LUFS").closest('span');
  expect(lufsBadge).toHaveClass("bg-amber-100", "text-amber-800");
});

test("renders fail tone for high clipping percentage", () => {
  render(<MetricsBadges m={{ clip_pct: 2.0 }} />);
  const clipBadge = screen.getByText("clip").closest('span');
  expect(clipBadge).toHaveClass("bg-red-100", "text-red-800");
});

test("renders ok tone for good metrics", () => {
  render(<MetricsBadges m={{ lufs: -23.0, clip_pct: 0.05 }} />);
  const lufsBadge = screen.getByText("LUFS").closest('span');
  const clipBadge = screen.getByText("clip").closest('span');
  expect(lufsBadge).toHaveClass("bg-green-100", "text-green-800");
  expect(clipBadge).toHaveClass("bg-green-100", "text-green-800");
});

test("renders all metric types when provided", () => {
  render(<MetricsBadges m={{
    lufs: -23.0,
    clip_pct: 0.1,
    dc_offset: 0.3,
    head_ms: 100,
    tail_ms: 120,
    true_peak: -0.5,
    lra: 8.5
  }} />);

  expect(screen.getByText("LUFS")).toBeInTheDocument();
  expect(screen.getByText("clip")).toBeInTheDocument();
  expect(screen.getByText("DC")).toBeInTheDocument();
  expect(screen.getByText("head")).toBeInTheDocument();
  expect(screen.getByText("tail")).toBeInTheDocument();
  expect(screen.getByText("TP")).toBeInTheDocument();
  expect(screen.getByText("LRA")).toBeInTheDocument();
});

test("returns null when no metrics provided", () => {
  const { container } = render(<MetricsBadges m={undefined} />);
  expect(container.firstChild).toBeNull();
});

test("returns null when empty metrics object provided", () => {
  const { container } = render(<MetricsBadges m={{}} />);
  expect(container.firstChild).toBeNull();
});
