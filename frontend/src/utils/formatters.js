// utils/formatters.js
// Numbers ane data format karvani helper functions

// Number ne clean format maa show kare che
export const formatNumber = (num) => {
  if (num === null || num === undefined) return '0';
  if (Number.isInteger(num)) return num.toString();
  return parseFloat(num.toFixed(4)).toString();
};

// Confidence score ne percentage maa show kare che
export const formatConfidence = (confidence) => {
  return `${parseFloat(confidence).toFixed(1)}%`;
};

// Sequence array ne string maa convert kare che
export const formatSequence = (sequence) => {
  return sequence.map(formatNumber).join(', ');
};

// Predictions ne readable format maa show kare che
export const formatPredictions = (predictions) => {
  return predictions.map(formatNumber).join(', ');
};

// Confidence na base par color return kare che
export const getConfidenceColor = (confidence) => {
  if (confidence >= 90) return 'text-green-400';
  if (confidence >= 70) return 'text-yellow-400';
  return 'text-red-400';
};

// Confidence na base par background color
export const getConfidenceBg = (confidence) => {
  if (confidence >= 90) return 'bg-green-400';
  if (confidence >= 70) return 'bg-yellow-400';
  return 'bg-red-400';
};