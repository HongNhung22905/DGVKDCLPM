import Link from "next/link";
import { BookText, ChevronRight } from "lucide-react";
import ProtectedRoute from "@/components/auth/ProtectedRoute";

export const metadata = { title: "Ngữ pháp | HSK 3.0" };

const LEVELS = [
  { num: 1, label: "HSK 1", points: 50,  color: "#C0392B", bg: "rgba(192,57,43,0.12)" },
  { num: 2, label: "HSK 2", points: 75,  color: "#2563EB", bg: "rgba(37,99,235,0.12)" },
  { num: 3, label: "HSK 3", points: 79,  color: "#059669", bg: "rgba(5,150,105,0.12)" },
  { num: 4, label: "HSK 4", points: 106, color: "#B45309", bg: "rgba(180,83,9,0.12)" },
  { num: 5, label: "HSK 5", points: 117, color: "#7C3AED", bg: "rgba(124,58,237,0.12)" },
  { num: 6, label: "HSK 6", points: 45,  color: "#EA580C", bg: "rgba(234,88,12,0.12)" },
];

export default function GrammarPage() {
  return (
    <ProtectedRoute>
      <div className="min-h-[calc(100vh-48px)] px-4 py-10" style={{ background: "#FFFBEA" }}>
      <style>{`
        .grammar-level-link {
          border-color: #E8D98A;
          background-color: #FFF8D6;
          transition: border-color 0.15s, background-color 0.15s, box-shadow 0.15s;
        }
        .grammar-level-link:hover {
          background-color: #FFF3B0;
          box-shadow: 0 2px 12px rgba(180,83,9,0.10);
        }
      `}</style>
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div
              className="w-10 h-10 rounded-xl flex items-center justify-center"
              style={{ background: "linear-gradient(135deg,#7C3AED,#B45309)" }}
            >
              <BookText size={20} className="text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold" style={{ color: "#1C1408" }}>Ngữ pháp</h1>
              <p className="text-xs" style={{ color: "#78614A" }}>472 điểm ngữ pháp · 5048 câu ví dụ</p>
            </div>
          </div>
          <p className="text-sm mt-3" style={{ color: "#78614A" }}>
            Học điểm ngữ pháp, luyện điền từ, và game sắp xếp câu theo từng cấp độ HSK.
          </p>
        </div>

        {/* Level grid */}
        <div className="grid grid-cols-1 gap-3">
          {LEVELS.map(({ num, label, points, color, bg }) => (
            <Link
              key={num}
              href={`/grammar/${num}`}
              className="grammar-level-link flex items-center justify-between rounded-2xl border p-5 active:scale-[0.99]"
            >
              <div className="flex items-center gap-4">
                <div
                  className="w-12 h-12 rounded-xl flex items-center justify-center text-lg font-bold"
                  style={{ background: bg, color }}
                >
                  {num}
                </div>
                <div>
                  <p className="font-semibold" style={{ color: "#1C1408" }}>{label}</p>
                  <p className="text-xs mt-0.5" style={{ color: "#78614A" }}>{points} điểm ngữ pháp</p>
                </div>
              </div>
              <ChevronRight size={18} style={{ color: "#A8956A" }} />
            </Link>
          ))}
        </div>

        {/* Info box */}
        <div
          className="mt-8 rounded-2xl border p-4 text-sm"
          style={{ borderColor: "#E8D98A", backgroundColor: "#FFF8D6", color: "#78614A" }}
        >
          <p className="font-semibold mb-2" style={{ color: "#1C1408" }}>3 chế độ luyện tập</p>
          <div className="space-y-1.5">
            <p><span className="font-medium" style={{ color: "#7C3AED" }}>Điểm ngữ pháp</span> — đọc cấu trúc và ví dụ minh họa</p>
            <p><span className="font-medium" style={{ color: "#2563EB" }}>Điền từ</span> — hoàn thành câu bằng cách chọn từ đúng</p>
            <p><span className="font-medium" style={{ color: "#059669" }}>Sắp xếp câu</span> — kéo thả từ để tạo thành câu hoàn chỉnh</p>
          </div>
        </div>
      </div>
    </div>
    </ProtectedRoute>
  );
}
