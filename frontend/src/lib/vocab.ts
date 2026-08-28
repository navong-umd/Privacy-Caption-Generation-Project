// Fixed label vocabularies from the pipeline schema (not data, the schema itself).

export const PI_CATEGORIES = [
  "LOCATION_INFORMATION",
  "UNIQUE_IDENTIFIER",
  "PHONE_INFORMATION",
  "ACCOUNT_INFORMATION",
  "CONTACT_INFORMATION",
  "CALENDAR_INFORMATION",
  "SMS_MMS",
  "BROWSER_INFORMATION",
  "NETWORK_INFORMATION",
  "BLUETOOTH_INFORMATION",
  "DATABASE_INFORMATION",
  "FILE_INFORMATION",
  "IMAGE",
  "AUDIO",
];

export const SINK_TYPES = ["network", "storage", "logging", "ipc", "serialization", "heuristic_unknown"];

export const PRACTICE_LABELS = ["Collecting", "Processing", "Sharing", "Other"];
export const PURPOSE_LABELS = ["Functionality", "Advertisement", "Analytics", "Other"];
export const LABEL_SOURCES = ["weak", "llm", "human"];
export const SPLITS = ["train", "val", "test"];
