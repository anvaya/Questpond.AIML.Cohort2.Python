import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { submitEmployerJob } from '@/lib/api';

export function EmployerJobPage() {
  const navigate = useNavigate();
  const [jobDescription, setJobDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    const trimmed = jobDescription.trim();

    if (trimmed.length < 50) {
      setError('Job description must be at least 50 characters');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const jobId = await submitEmployerJob(trimmed);
      navigate(`/progress/${jobId}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit job');
      setIsSubmitting(false);
    }
  };

  const sampleJD = `Looking for a Java developer with 3 years of experience in AWS and Microservices architecture.

Requirements:
- 3+ years of Java development experience
- Experience with Spring Boot framework
- AWS cloud services (EC2, S3, Lambda)
- Microservices architecture
- Docker and Kubernetes
- RESTful API design
- Knowledge of Agile methodologies`;

  const loadSample = () => {
    setJobDescription(sampleJD);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <Button variant="ghost" onClick={() => navigate('/')}>
            ← Back
          </Button>
        </div>

        <div className="max-w-3xl mx-auto">
          <Card>
            <CardHeader>
              <CardTitle className="text-3xl">Submit Job Description</CardTitle>
              <CardDescription>
                Paste a job description to find matching candidates
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Job Description Input */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="jd">Job Description</Label>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={loadSample}
                    className="text-xs"
                  >
                    Load Sample
                  </Button>
                </div>
                <Textarea
                  id="jd"
                  placeholder="Paste the job description here..."
                  value={jobDescription}
                  onChange={(e) => {
                    setJobDescription(e.target.value);
                    setError(null);
                  }}
                  rows={12}
                  className="resize-none"
                />
                <div className="text-sm text-slate-500 dark:text-slate-400 text-right">
                  {jobDescription.trim().length} characters (min. 50)
                </div>
              </div>

              {/* Error Message */}
              {error && (
                <div className="bg-destructive/10 text-destructive p-4 rounded-lg text-sm">
                  {error}
                </div>
              )}

              {/* Submit Button */}
              <Button
                onClick={handleSubmit}
                disabled={jobDescription.trim().length < 50 || isSubmitting}
                className="w-full"
                size="lg"
              >
                {isSubmitting ? 'Submitting...' : 'Find Matching Candidates'}
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
