import { useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Loader2, CheckCircle2, XCircle, AlertCircle } from 'lucide-react';
import { useJobPolling } from '@/hooks/useJobPolling';
import type { Job } from '@/types';

export function JobProgressPage() {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();
  const { job, error, isPolling } = useJobPolling(jobId || null);

  useEffect(() => {
    // Auto-navigate to result page when job completes successfully
    if (job?.status === 'completed' && job?.type) {
      const targetPage = job.type === 'candidate' ? '/candidate/result' : '/employer/result';
      setTimeout(() => {
        navigate(`${targetPage}/${jobId}`, { replace: true });
      }, 500);
    }
  }, [job?.status, job?.type, jobId, navigate]);

  if (!job) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6 text-center">
            <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4" />
            <p>Loading job status...</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const getStatusIcon = () => {
    switch (job.status) {
      case 'queued':
        return <Loader2 className="w-12 h-12 text-slate-400 animate-spin" />;
      case 'processing':
        return <Loader2 className="w-12 h-12 text-primary animate-spin" />;
      case 'completed':
        return <CheckCircle2 className="w-12 h-12 text-green-500" />;
      case 'failed':
        return <XCircle className="w-12 h-12 text-destructive" />;
    }
  };

  const getStatusText = () => {
    switch (job.status) {
      case 'queued':
        return 'Queued';
      case 'processing':
        return 'Processing';
      case 'completed':
        return 'Completed';
      case 'failed':
        return 'Failed';
    }
  };

  const getStatusVariant = (): "default" | "secondary" | "destructive" | "outline" => {
    switch (job.status) {
      case 'queued':
        return 'secondary';
      case 'processing':
        return 'default';
      case 'completed':
        return 'default';
      case 'failed':
        return 'destructive';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="flex justify-center mb-4">{getStatusIcon()}</div>
          <CardTitle className="text-2xl">
            {job.type === 'candidate' ? 'Resume Processing' : 'Candidate Matching'}
          </CardTitle>
          <CardDescription className="flex items-center justify-center gap-2">
            {getStatusText()}
            <Badge variant={getStatusVariant()}>{job.status}</Badge>
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Progress Bar */}
          {job.status !== 'failed' && (
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-slate-500 dark:text-slate-400">Progress</span>
                <span className="font-medium">{job.progress}%</span>
              </div>
              <Progress value={job.progress} />
            </div>
          )}

          {/* Status Message */}
          <div className="text-center">
            <p className="text-slate-600 dark:text-slate-400">{job.message}</p>
          </div>

          {/* Error Display */}
          {(job.status === 'failed' || error) && (
            <div className="bg-destructive/10 text-destructive p-4 rounded-lg">
              <div className="flex items-start gap-2">
                <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                <div className="text-sm">
                  <p className="font-medium mb-1">Processing Failed</p>
                  <p>{error || job.error_message || 'An unknown error occurred'}</p>
                </div>
              </div>
            </div>
          )}

          {/* Actions */}
          {job.status === 'failed' && (
            <div className="flex gap-2">
              <Button
                variant="outline"
                className="flex-1"
                onClick={() => navigate(-1)}
              >
                Go Back
              </Button>
              <Button
                className="flex-1"
                onClick={() => navigate('/')}
              >
                Start Over
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
