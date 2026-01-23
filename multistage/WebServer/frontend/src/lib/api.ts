// API client functions
const API_BASE = '/api';

export async function submitCandidateJob(file: File): Promise<string> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE}/jobs/candidate`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to submit job');
  }

  const data = await response.json();
  return data.job_id;
}

export async function submitEmployerJob(jobDescription: string): Promise<string> {
  const response = await fetch(`${API_BASE}/jobs/employer`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ job_description: jobDescription }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to submit job');
  }

  const data = await response.json();
  return data.job_id;
}

export async function getJobStatus(jobId: string) {
  const response = await fetch(`${API_BASE}/jobs/${jobId}`);

  if (!response.ok) {
    throw new Error('Failed to get job status');
  }

  return response.json();
}
