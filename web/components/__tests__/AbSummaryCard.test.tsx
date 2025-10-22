import { render, screen } from "@testing-library/react";
import { AbSummaryCard } from "../components/AbSummaryCard";

test("renders engines and metrics", () => {
  render(<AbSummaryCard data={{
    sessionId: "s1",
    total_items: 3,
    engines: [
      { engine:"A", n_items:2, wins:1, win_rate:0.5, win_rate_ci95_low:0.1, win_rate_ci95_high:0.8, mean_score:4.3, median_lufs:-23.2, clip_hit_rate:0.0 },
      { engine:"B", n_items:1, wins:1, win_rate:1.0, win_rate_ci95_low:0.3, win_rate_ci95_high:1.0, mean_score:4.7, median_lufs:-22.9, clip_hit_rate:0.2 },
    ]
  }} />);
  expect(screen.getByText(/A\/B Results|A\/B Results|A\/B Results/i)).toBeTruthy();
  expect(screen.getByText("A")).toBeInTheDocument();
  expect(screen.getByText("B")).toBeInTheDocument();
});
