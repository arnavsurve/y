import { GoogleGenerativeAI, Part } from "@google/generative-ai";

export interface ImageFile {
  name: string;
  mimeType: string;
  data: string; // base64 encoded image data
}

export const extractTextFromImages = async (
  client: GoogleGenerativeAI,
  images: ImageFile[],
): Promise<string[]> => {
  const extractedTexts = await Promise.all(
    images.map((image) => extractTextFromImage(client, image)),
  );
  return extractedTexts;
};

export const extractTextFromImage = async (
  client: GoogleGenerativeAI,
  image: ImageFile,
): Promise<string> => {
  const promptContents: string[] = [];
  promptContents.push(
    "Read the text from this image. If possible, include the platform that you estimate this image originated from at the beginning of your response. Make sure you parse the post or text messages for relevant conversational or post content. Include this in your response. For an image or images withing the screenshot content, describe them in maximum detail.",
  );

  const imagePart: Part = {
    inlineData: {
      data: image.data,
      mimeType: image.mimeType,
    },
  };
  try {
    const model = client.getGenerativeModel({ model: "gemini-2.0-flash" });
    const result = await model.generateContent([...promptContents, imagePart]);
    const response = result.response;
    return response.text();
  } catch (error) {
    console.error("Error extracting text: ", error);
    throw new Error("Failed to extract text from image");
  }
};

// Function for analyzing social media vibes
export const analyzeVibeFromImage = async (
  client: GoogleGenerativeAI,
  image: ImageFile,
): Promise<string> => {
  // First get the raw text
  const rawText = await extractTextFromImage(client, image);

  // Then analyze the vibe using a separate prompt
  const vibePrompt = `Analyze the following social media content and describe its vibe:
  
${rawText}

Please describe:
1. The overall tone and mood
2. Any notable slang or language patterns
3. The general sentiment
4. Any cultural references or trends`;

  const model = client.getGenerativeModel({ model: "gemini-2.0-flash" });
  const result = await model.generateContent([vibePrompt]);
  const response = result.response;
  return response.text();
};

// Function for extracting structured conversation
export const extractConversationFromImage = async (
  client: GoogleGenerativeAI,
  image: ImageFile,
): Promise<string> => {
  // First get the raw text
  const rawText = await extractTextFromImage(client, image);

  // Then structure the conversation
  const conversationPrompt = `Parse this text into a structured conversation, identifying:
  
${rawText}

Please extract:
1. The platform (if identifiable)
2. The participants
3. The conversation flow
4. Any relevant context or metadata`;

  const model = client.getGenerativeModel({ model: "gemini-2.0-flash" });
  const result = await model.generateContent([conversationPrompt]);
  const response = result.response;
  return response.text();
};
