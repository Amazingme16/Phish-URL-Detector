export enum AnalysisStatus {
  IDLE = 'IDLE',
  ANALYZING = 'ANALYZING',
  COMPLETED = 'COMPLETED',
  ERROR = 'ERROR'
}

export enum ThreatLevel {
  SAFE = 'SAFE',
  SUSPICIOUS = 'SUSPICIOUS',
  PHISHING = 'PHISHING'
}

export interface FeatureWeight {
  featureName: string;
  weight: number; // Positive means contributes to phishing, negative means contributes to safety
  description: string;
}

export interface AnalysisResult {
  url: string;
  threatLevel: ThreatLevel;
  probability: number; // 0 to 1
  features: FeatureWeight[];
  reasoning: string;
}

export interface GeminiError {
  message: string;
}