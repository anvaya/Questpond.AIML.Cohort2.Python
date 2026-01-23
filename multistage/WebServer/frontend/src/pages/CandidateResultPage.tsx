import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { User, Calendar, Code, Globe, Linkedin, Github, MapPin, CheckCircle2 } from 'lucide-react';
import { getJobStatus } from '@/lib/api';
import type { CandidateProfile } from '@/types';

export function CandidateResultPage() {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();
  const [profile, setProfile] = useState<CandidateProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchResult = async () => {
      try {
        const job = await getJobStatus(jobId!);
        if (job.status === 'completed' && job.result?.profile) {
          setProfile(job.result.profile);
        } else if (job.status === 'failed') {
          setError(job.error_message || 'Job failed');
        } else {
          setError('Job not completed');
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch result');
      } finally {
        setLoading(false);
      }
    };

    fetchResult();
  }, [jobId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center p-4">
        <Card className="w-full max-w-2xl">
          <CardContent className="pt-6 text-center">
            <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
            <p>Loading candidate profile...</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6 text-center space-y-4">
            <p className="text-destructive">{error || 'Failed to load profile'}</p>
            <Button onClick={() => navigate('/')}>Go Home</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <Button variant="ghost" onClick={() => navigate('/')}>
            ← Back Home
          </Button>
          <Badge variant="default" className="flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3" />
            Processed Successfully
          </Badge>
        </div>

        <div className="max-w-4xl mx-auto space-y-6">
          {/* Identity Card */}
          <Card>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center">
                    <User className="w-8 h-8 text-primary" />
                  </div>
                  <div>
                    <CardTitle className="text-2xl">{profile.identity.full_name}</CardTitle>
                    <CardDescription>Candidate Profile</CardDescription>
                  </div>
                </div>
                <div className="flex gap-2">
                  {profile.identity.linkedin && (
                    <Badge variant="outline" className="flex items-center gap-1">
                      <Linkedin className="w-3 h-3" />
                      LinkedIn
                    </Badge>
                  )}
                  {profile.identity.github && (
                    <Badge variant="outline" className="flex items-center gap-1">
                      <Github className="w-3 h-3" />
                      GitHub
                    </Badge>
                  )}
                </div>
              </div>
            </CardHeader>
          </Card>

          {/* Experience Roles */}
          <div className="space-y-4">
            <h2 className="text-xl font-semibold flex items-center gap-2">
              <BriefcaseIcon className="w-5 h-5" />
              Work Experience
            </h2>
            {profile.candidate_roles.map((role, idx) => (
              <Card key={idx}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-lg">{role.title}</CardTitle>
                      <CardDescription className="flex items-center gap-2 mt-1">
                        <Calendar className="w-4 h-4" />
                        {role.verified_duration} months verified
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Technologies */}
                  <div>
                    <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
                      <Code className="w-4 h-4" />
                      Technologies
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {role.raw_technologies.map((tech) => (
                        <Badge key={tech} variant="secondary">
                          {tech}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  {/* Domains */}
                  {role.domains.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
                        <Globe className="w-4 h-4" />
                        Domains
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {role.domains.map((domain) => (
                          <Badge key={domain} variant="outline">
                            {domain}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Action Buttons */}
          <div className="flex gap-4">
            <Button onClick={() => navigate('/')} variant="outline" className="flex-1">
              Process Another Resume
            </Button>
            <Button onClick={() => navigate('/employer')} className="flex-1">
              Try Candidate Matching
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

function BriefcaseIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <rect width="20" height="14" x="2" y="7" rx="2" ry="2" />
      <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" />
    </svg>
  );
}
