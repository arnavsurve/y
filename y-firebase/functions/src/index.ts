import { onRequest } from "firebase-functions/v2/https";
import * as logger from "firebase-functions/logger";
import { GoogleGenerativeAI } from "@google/generative-ai";
import { extractTextFromImages, ImageFile } from "./utils/ocr";
import { formatVibeCheckPrompt } from "./utils/llm";
import busboy from "busboy";
import { Readable } from "stream";

const genaiClient = new GoogleGenerativeAI(process.env.GEMINI_API_KEY || "");
const model = genaiClient.getGenerativeModel({ model: "gemini-2.0-flash" });

export const vibeCheck = onRequest(async (request, response) => {
  if (request.method !== "POST") {
    response.status(405).send("Method not allowed");
    return;
  }

  const imageFiles: ImageFile[] = [];
  let userPrompt = "";

  try {
    const bb = busboy({ headers: request.headers });

    bb.on("field", (name: string, val: string) => {
      logger.info(`Field: ${name}, Value: ${val}`);
      if (name === "prompt") {
        userPrompt = val;
      }
    });

    bb.on(
      "file",
      (
        name: string,
        fileStream: Readable,
        info: { filename: string; mimeType: string },
      ) => {
        logger.info(`File: ${name}, FileInfo: ${JSON.stringify(info)}`);
        if (name !== "images") {
          // Skip other file fields.
          fileStream.resume();
          return;
        }

        const chunks: Buffer[] = [];
        fileStream.on("data", (chunk: Buffer) => {
          chunks.push(chunk);
        });
        fileStream.on("end", () => {
          const buffer = Buffer.concat(chunks);
          imageFiles.push({
            name: info.filename,
            mimeType: info.mimeType,
            data: buffer.toString("base64"),
          });
        });
      },
    );

    // Wrap Busboy processing in a promise so that we wait for it to finish.
    await new Promise<void>((resolve, reject) => {
      bb.once("close", resolve).once("error", reject);
      bb.end(request.rawBody);
    });

    if (imageFiles.length === 0) {
      response.status(400).send("No images were uploaded");
      return;
    }

    // Now that Busboy has finished processing, perform OCR.
    const ocrText = await extractTextFromImages(genaiClient, imageFiles);
    const vibeCheckResult = await model.generateContent(
      formatVibeCheckPrompt(userPrompt, ocrText.join("\n\n")),
    );

    const resultText = vibeCheckResult.response.text();
    const bubbles = resultText
      .split("$endbubble")
      .filter((bubble) => bubble.trim().length > 0);

    response.json({
      result: resultText,
      bubbles: bubbles,
      fileCount: imageFiles.length,
      hasUserPrompt: Boolean(userPrompt),
    });
  } catch (error) {
    logger.error("Error processing vibe check:", error);
    response.status(500).send("Error processing your request");
  }
});
