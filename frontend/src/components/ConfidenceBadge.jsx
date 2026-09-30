import React from 'react';

export default function ConfidenceBadge({ score, label }) {
  if (score === undefined || score === null) return null;

  const pct = Math.round(score * 100);
  
  // Determine color class based on score
  let cls = 'badge-medium';
  if (pct >= 80) cls = 'badge-high';
  else if (pct <= 50) cls = 'badge-low';

  // Fallback label if not provided
  let displayLabel = label;
  if (!displayLabel) {
    if (pct >= 80) displayLabel = 'High';
    else if (pct > 50) displayLabel = 'Medium';
    else displayLabel = 'Low';
  }

  return (
    <span className={`badge ${cls}`} title={`Confidence Score: ${pct}%`}>
      {displayLabel} ({pct}%)
    </span>
  );
}
