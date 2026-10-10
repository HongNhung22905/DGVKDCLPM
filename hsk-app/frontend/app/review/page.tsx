import ReviewClient from "@/components/review/ReviewClient";

export const dynamic = "force-dynamic";
export const metadata = { title: "Ôn tập hôm nay | HSK 3.0" };

export default function ReviewPage() {
  const today = new Date().toISOString().split("T")[0];
  return <ReviewClient today={today} />;
}
