/**
 * Gemini AI wrapper — server-only
 * Chỉ import từ API routes (không bao giờ dùng ở client)
 * SDK: @google/genai (thay thế @google/generative-ai đã EOL)
 */
import { GoogleGenAI } from "@google/genai";

const API_KEY = process.env.GEMINI_API_KEY ?? "";

if (!API_KEY || API_KEY === "REPLACE_WITH_GEMINI_API_KEY") {
  if (process.env.NODE_ENV !== "production") {
    console.warn("[gemini] GEMINI_API_KEY chưa được set. AI features sẽ trả lỗi 503.");
  }
}

const genAI = new GoogleGenAI({ apiKey: API_KEY });

export async function generateText(prompt: string): Promise<string> {
  if (!API_KEY || API_KEY === "REPLACE_WITH_GEMINI_API_KEY") {
    throw new Error("GEMINI_API_KEY chưa được cấu hình.");
  }
  const response = await genAI.models.generateContent({
    model: "gemini-2.0-flash",
    contents: prompt,
    config: {
      temperature: 0.4,
      topP: 0.95,
      maxOutputTokens: 1024,
    },
  });
  return response.text ?? "";
}

// ─── Prompts chuẩn cho từng tính năng ────────────────────────────────────────

export const PROMPTS = {
  /**
   * Chấm ngữ pháp: nhận câu tiếng Trung → phân tích lỗi
   */
  grammar: (sentence: string) => `
Bạn là gia sư tiếng Trung chuyên nghiệp. Hãy phân tích câu sau:

Câu: "${sentence}"

Trả lời theo định dạng JSON chính xác:
{
  "isCorrect": true/false,
  "correctedSentence": "câu đúng (nếu có lỗi, giữ nguyên nếu đúng)",
  "errors": [
    {
      "type": "loại lỗi (ngữ pháp/từ vựng/thứ tự từ/...)",
      "original": "phần sai",
      "suggestion": "gợi ý sửa",
      "explanation": "giải thích ngắn bằng tiếng Việt"
    }
  ],
  "score": 0-100,
  "overallFeedback": "nhận xét tổng quan bằng tiếng Việt (1-2 câu)"
}
Chỉ trả JSON, không thêm markdown hay text khác.`,

  /**
   * Chấm bài dịch: so sánh bản dịch của học viên với câu gốc
   */
  translation: (original: string, userTranslation: string, direction: "zh2vi" | "vi2zh") => `
Bạn là gia sư tiếng Trung. Hãy đánh giá bài dịch của học viên.

${direction === "zh2vi"
  ? `Câu gốc (tiếng Trung): "${original}"\nBản dịch của học viên (tiếng Việt): "${userTranslation}"`
  : `Câu gốc (tiếng Việt): "${original}"\nBản dịch của học viên (tiếng Trung): "${userTranslation}"`
}

Trả lời theo định dạng JSON chính xác:
{
  "score": 0-100,
  "referenceSolution": "bản dịch mẫu tốt nhất",
  "feedback": "nhận xét chi tiết bằng tiếng Việt",
  "strengths": ["điểm tốt 1", "điểm tốt 2"],
  "improvements": ["cần cải thiện 1", "cần cải thiện 2"]
}
Chỉ trả JSON, không thêm markdown hay text khác.`,

  /**
   * Giải thích từ: nhận chữ Hán → giải thích chi tiết
   */
  explainWord: (hanzi: string, pinyin: string, context?: string) => `
Bạn là gia sư tiếng Trung. Hãy giải thích từ sau bằng tiếng Việt:

Từ: ${hanzi} (${pinyin})
${context ? `Ngữ cảnh: "${context}"` : ""}

Trả lời theo định dạng JSON chính xác:
{
  "meanings": ["nghĩa 1", "nghĩa 2"],
  "examples": [
    { "zh": "câu ví dụ tiếng Trung", "vi": "nghĩa tiếng Việt", "pinyin": "phiên âm" }
  ],
  "synonyms": ["từ đồng nghĩa 1", "từ đồng nghĩa 2"],
  "antonyms": ["từ trái nghĩa 1"],
  "memoryTip": "mẹo nhớ từ bằng tiếng Việt",
  "usageNote": "lưu ý khi dùng từ này (nếu có)"
}
Chỉ trả JSON, không thêm markdown hay text khác.`,

  /**
   * Tạo câu ví dụ cho từ
   */
  makeExamples: (hanzi: string, level: string) => `
Tạo 3 câu ví dụ tự nhiên với từ "${hanzi}" phù hợp trình độ ${level.replace("new-", "HSK ")}.

Trả JSON:
{
  "examples": [
    { "zh": "câu tiếng Trung", "pinyin": "phiên âm", "vi": "nghĩa tiếng Việt" }
  ]
}
Chỉ trả JSON.`,
};
