import express from "express";
import path from "path";
import { createServer as createViteServer } from "vite";
import { GoogleGenAI } from "@google/genai";

let geminiClient: GoogleGenAI | null = null;

function getGeminiClient(): GoogleGenAI | null {
  if (!geminiClient) {
    const key = process.env.GEMINI_API_KEY;
    if (key) {
      geminiClient = new GoogleGenAI({
        apiKey: key,
        httpOptions: {
          headers: {
            "User-Agent": "aistudio-build",
          },
        },
      });
    }
  }
  return geminiClient;
}

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json());

  // Health check
  app.get("/api/health", (req, res) => {
    res.json({ status: "ok", mode: "full-stack", time: new Date().toISOString() });
  });

  // AI Coach endpoint using Gemini 3.7 Flash
  app.post("/api/gemini/coach", async (req, res) => {
    try {
      const { message, context } = req.body;
      if (!message) {
        return res.status(400).json({ error: "Message is required" });
      }

      const client = getGeminiClient();
      if (!client) {
        // Safe intelligent fallback response when API key is not yet configured
        return res.json({
          reply: `سلام قهرمان! من مربی هوش مصنوعی برنامه سلامت ۳۶۵ روزه شما هستم. 
در مورد سن ۱۵ سال، قد ۱۷۲ سانتی‌متر و وزن ۴۵ کیلوگرم:
۱. **تغذیه:** برای رشد بهینه و وزن‌گیری سالم، مصرف ۶ وعده منظم با پروتئین بالا (تخم‌مرغ، مرغ، لبنیات غنی از کلسیم) و کربوهیدرات‌های پیچیده حیاتی است.
۲. **تمرینات:** استفاده از بارفیکس (کاهش فشار مهره‌ها)، کش ورزشی و تردمیل باعث تقویت کمربند شانه و راستای ستون فقرات می‌شود.
۳. **خواب:** ترشح حداکثری هورمون رشد بین ساعت ۲۳:۰۰ تا ۰۳:۰۰ در خواب عمیق اتفاق می‌افتد.
هر سوالی درباره تکنیک حرکات یا تغذیه داری از من بپرس!`,
          source: "smart_advisor"
        });
      }

      const systemInstruction = `شما "مک‌آی (MacAI Coach)" هستید، یک مربی و فیزیولوژیست ورزشی و مشاور تغذیه متخصص برای نوجوان ۱۵ ساله با قد ۱۷۲ سانتیمتر و وزن ۴۵ کیلوگرم.
تجهیزات کاربر شامل: تردمیل، بارفیکس، توپ بزرگ ورزشی (Swiss Ball)، کش ورزشی و دستگاه مسگری است.
قوانین اکید:
۱. لحن شما باید بسیار صمیمی، علمی، انگیزه بخش، مودبانه و حرفه‌ای به زبان فارسی باشد.
۲. هرگز وعده یا تضمین افزایش قد قطعی ندهید؛ تاکید کنید که هدف سلامت اسکلتی، اصلاح پاسچر (قامت)، رفع قوز و تغذیه/خواب استاندارد برای پتانسیل طبیعی رشد است.
۳. اگر کاربر از درد تیز شکایت کرد، بلافاصله توصیه به توقف تمرین و استراحت کنید.
۴. پاسخ‌ها را ساختاریافته، با نکات گلوله‌ای و بسیار تمیز و شبیه دستیار مدرن اپل/مک ارائه دهید.`;

      const prompt = `مشخصات کاربر: سن ۱۵ سال | قد ۱۷۲cm | وزن ۴۵kg | تجهیزات: تردمیل، بارفیکس، توپ ورزشی، کش، مسگری.
زمینه گفتگو: ${context ? JSON.stringify(context) : "ندارد"}

پیام یا سوال کاربر:
"${message}"`;

      const response = await client.models.generateContent({
        model: "gemini-3.7-flash",
        contents: prompt,
        config: {
          systemInstruction,
          temperature: 0.7,
        },
      });

      const replyText = response.text || "پاسخی از مربی دریافت نشد. لطفا مجددا تلاش کنید.";
      return res.json({ reply: replyText, source: "gemini-3.7-flash" });
    } catch (error: unknown) {
      console.error("Gemini API error:", error);
      const errMsg = error instanceof Error ? error.message : "Internal error";
      return res.status(500).json({
        error: errMsg,
        fallbackReply: "در حال حاضر ارتباط با سرور هوش مصنوعی برقرار نشد، اما توصیه کلی این است که تمرین را با فرم صحیح ادامه دهید و خواب ساعت ۲۳:۰۰ را از دست ندهید!"
      });
    }
  });

  // Vite middleware for development
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`MacOS Health App Server running on http://0.0.0.0:${PORT}`);
  });
}

startServer();
