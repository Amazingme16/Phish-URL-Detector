import { GoogleGenAI, Type, Schema } from "@google/genai";
import { AnalysisResult, ThreatLevel } from "../types";

// Initialize Gemini Client
const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

const analysisSchema: Schema = {
  type: Type.OBJECT,
  properties: {
    threatLevel: {
      type: Type.STRING,
      enum: ["SAFE", "SUSPICIOUS", "PHISHING"],
      description: "The classification of the URL based on the analysis.",
    },
    probability: {
      type: Type.NUMBER,
      description: "A probability score between 0 and 1 indicating the likelihood of being phishing (1 is 100% phishing).",
    },
    features: {
      type: Type.ARRAY,
      description: "List of features extracted for the logistic regression model.",
      items: {
        type: Type.OBJECT,
        properties: {
          featureName: { type: Type.STRING, description: "Name of the feature (e.g., 'URL Length', 'Has IP Address')." },
          weight: { type: Type.NUMBER, description: "The calculated weight/impact of this feature on the score. Positive for phishing indicators, negative for safety indicators." },
          description: { type: Type.STRING, description: "Brief explanation of why this feature matters." }
        },
        required: ["featureName", "weight", "description"]
      }
    },
    reasoning: {
      type: Type.STRING,
      description: "A summary explanation of the verdict."
    }
  },
  required: ["threatLevel", "probability", "features", "reasoning"]
};

export const analyzeUrlWithGemini = async (url: string): Promise<AnalysisResult> => {
  try {
    const model = "gemini-2.5-flash";
    
    const prompt = `
      Act as a cybersecurity expert and a logistic regression classifier. 
      Analyze the following URL for potential phishing threats: "${url}".
      
      Simulate the feature extraction and weighting process of a logistic regression model trained on phishing datasets.
      Consider features such as:
      - URL Length
      - Presence of IP address
      - Suspicious characters (@, -, etc.)
      - Number of subdomains
      - HTTPS/SSL validity (inferred)
      - Keyword analysis (e.g., 'secure', 'login', 'update' in non-standard places)
      - TLD reputation
      
      Assign weights to these features to calculate a final probability score.
      Return the result in JSON format.
    `;

    const response = await ai.models.generateContent({
      model: model,
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: analysisSchema,
        temperature: 0.3, // Lower temperature for more deterministic/analytical results
      },
    });

    const text = response.text;
    if (!text) {
      throw new Error("No response received from Gemini.");
    }

    const data = JSON.parse(text);

    // Map the string enum from JSON to our TypeScript Enum
    let mappedThreatLevel = ThreatLevel.SAFE;
    if (data.threatLevel === "PHISHING") mappedThreatLevel = ThreatLevel.PHISHING;
    else if (data.threatLevel === "SUSPICIOUS") mappedThreatLevel = ThreatLevel.SUSPICIOUS;

    return {
      url: url,
      threatLevel: mappedThreatLevel,
      probability: data.probability,
      features: data.features,
      reasoning: data.reasoning
    };

  } catch (error) {
    console.error("Gemini Analysis Error:", error);
    throw new Error("Failed to analyze the URL. Please check the API key or try again.");
  }
};