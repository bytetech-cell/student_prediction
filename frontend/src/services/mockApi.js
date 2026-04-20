const simulateLatency = (ms = 180) => new Promise((resolve) => setTimeout(resolve, ms));

export const predictPerformance = async (data) => {
  await simulateLatency(150); // Simulating < 200ms latency
  
  // Rule-based dummy logic for demonstration purposes to look realistic
  let score = 50; 
  score += (data.studyHours / 10) * 15;
  score += (data.assignmentMarks / 100) * 15;
  score += (data.attendance / 100) * 20;
  score -= (data.socialMedia / 10) * 15;
  score += (data.sgpa / 10) * 20;
  if(data.sleep >= 6 && data.sleep <= 8) score += 10;
  else if (data.sleep < 6) score -= 5;
  
  if(data.extracurricular === 'Heavy') score -= 5;
  if(data.extracurricular === 'Balanced') score += 5;

  score = Math.min(Math.max(Math.round(score), 0), 100);

  let risk = 'Low Risk';
  if(score < 42) risk = 'High Risk';
  else if (score >= 42 && score < 68) risk = 'Medium Risk';

  return {
    score,
    risk,
    latency: '154ms',
    features: [
      { name: 'Study Hours', impact: 0.35, type: 'positive' },
      { name: 'Attendance', impact: 0.25, type: 'positive' },
      { name: 'Previous SGPA', impact: 0.20, type: 'positive' },
      { name: 'Social Media', impact: 0.15, type: 'negative' },
      { name: 'Sleep Hours', impact: 0.05, type: 'neutral' },
    ],
    ensemble: {
      rf: { score: score + 2, weight: 0.45 },
      svm: { score: score - 1, weight: 0.35 },
      lr: { score: score - 3, weight: 0.20 }
    }
  };
};

export const getAnalytics = async () => {
  await simulateLatency();
  return {
    riskDistribution: [
      { name: 'Low Risk', value: 45, fill: '#22c55e' },
      { name: 'Medium Risk', value: 35, fill: '#eab308' },
      { name: 'High Risk', value: 20, fill: '#ef4444' }
    ],
    performanceTrends: [
      { month: 'Jan', avgScore: 65 },
      { month: 'Feb', avgScore: 67 },
      { month: 'Mar', avgScore: 70 },
      { month: 'Apr', avgScore: 68 },
      { month: 'May', avgScore: 75 }
    ]
  };
};
