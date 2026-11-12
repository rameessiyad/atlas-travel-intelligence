export interface DaySection {
  title: string;
  body: string;
}

const clean = (s: string) =>
  s
    .replace(/\*\*/g, "")
    .replace(/^#+\s*/gm, "")
    .trim();

const DAY_START = /\n(?=\s*(?:[-*]\s*)?(?:#{1,4}\s*)?(?:\*\*)?Day\s*\d+)/i;

export function parseItinerary(text: string): DaySection[] {
  const parts = text.split(DAY_START);
  if (parts.length < 2) return [{ title: "Your plan", body: clean(text) }];

  return parts
    .map((part) => {
      const lines = clean(part).split("\n");
      const first = lines[0].replace(/^[-*]\s*/, "").trim();
      if (/^day\s*\d+/i.test(first)) {
        const body = lines
          .slice(1)
          .map((l) => l.replace(/^\s{2,}/, ""))
          .join("\n")
          .trim();
        return { title: first.replace(/:\s*$/, ""), body };
      }
      return { title: "Overview", body: clean(part) };
    })
    .filter((s) => s.body || s.title !== "Overview");
}
