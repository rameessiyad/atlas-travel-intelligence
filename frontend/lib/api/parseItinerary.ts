export interface DaySection {
  title: string;
  body: string;
}

const clean = (s: string) =>
  s
    .replace(/\*\*/g, "")
    .replace(/^#+\s*/gm, "")
    .trim();

export function parseItinerary(text: string): DaySection[] {
  const parts = text.split(/\n(?=\s*(?:#{1,4}\s*)?(?:\*\*)?Day\s*\d+)/i);
  if (parts.length < 2) return [{ title: "Your plan", body: clean(text) }];

  return parts
    .map((part) => {
      const [first, ...rest] = clean(part).split("\n");
      const isDay = /^day\s*\d+/i.test(first.trim());
      return isDay
        ? { title: first.replace(/:\s*$/, ""), body: rest.join("\n").trim() }
        : { title: "Overview", body: clean(part) };
    })
    .filter((s) => s.body || s.title);
}
