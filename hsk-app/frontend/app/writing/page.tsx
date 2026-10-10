import { fetchLevels } from "@/lib/hskDataServer";
import WritingListClient from "@/components/vocabulary/WritingListClient";

export const revalidate = 3600;
export const metadata = { title: "Luyện viết Hán tự | HSK 3.0" };

export default async function WritingPage() {
  const levels = await fetchLevels();
  return <WritingListClient levels={levels} />;
}
