import type { Contact } from "./types.ts";

const HEADER = "id,email,name,phone,tags,updatedAt";

/** Parses the address-book export: one contact per line, tags separated by ";". No quoting. */
export function parseContactsCsv(text: string): Contact[] {
  const [header, ...lines] = text.split("\n").map((line) => line.trim());
  if (header !== HEADER) {
    throw new Error(`Unexpected CSV header: "${header}"`);
  }
  return lines
    .filter((line) => line !== "")
    .map((line) => {
      const [id, email, name, phone, tags, updatedAt] = line.split(",");
      return {
        id,
        email,
        name,
        phone,
        tags: tags === "" ? [] : tags.split(";"),
        updatedAt: Number(updatedAt),
      };
    });
}

export function toContactsCsv(contacts: Contact[]): string {
  const rows = contacts.map((c) => [c.id, c.email, c.name, c.phone, c.tags.join(";"), c.updatedAt].join(","));
  return [HEADER, ...rows].join("\n") + "\n";
}
