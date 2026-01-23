import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Users, Trophy, Medal, Award, CheckCircle2, Briefcase, ChevronDown, ChevronUp, XCircle } from 'lucide-react';
import { getJobStatus } from '@/lib/api';
import type { EmployerResult, MatchCandidate, SkillBreakdown } from '@/types';

export function EmployerResultPage() {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();
  const [result, setResult] = useState<EmployerResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedCards, setExpandedCards] = useState<Set<number>>(new Set());

  const toggleCard = (idx: number) => {
    const newExpanded = new Set(expandedCards);
    if (newExpanded.has(idx)) {
      newExpanded.delete(idx);
    } else {
      newExpanded.add(idx);
    }
    setExpandedCards(newExpanded);
  };

  useEffect(() => {
    const fetchResult = async () => {
      try {
        const job = await getJobStatus(jobId!);
        if (job.status === 'completed' && job.result?.matches) {
          console.log('Job result data:', job.result);
          console.log('First candidate skill_breakdown:', job.result.matches[0]?.skill_breakdown);

          setResult({
            matches: job.result.matches,
            role_context: job.result.role_context || 'General'
          });
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
            <p>Loading candidate matches...</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error || !result) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6 text-center space-y-4">
            <p className="text-destructive">{error || 'Failed to load matches'}</p>
            <Button onClick={() => navigate('/')}>Go Home</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const getConfidenceIcon = (confidence: string) => {
    switch (confidence) {
      case 'Strong Match':
        return <Trophy className="w-5 h-5 text-yellow-500" />;
      case 'Good Match':
        return <Medal className="w-5 h-5 text-slate-400" />;
      default:
        return <Award className="w-5 h-5 text-orange-500" />;
    }
  };

  const formatRoleContext = (roleContext: string | Record<string, string>): string => {
    if (typeof roleContext === 'string') {
      return roleContext;
    }
    // It's an object with primary_domain and seniority_level
    const domain = roleContext.primary_domain || 'General';
    const seniority = roleContext.seniority_level || '';
    return seniority ? `${seniority} ${domain}` : domain;
  };

  const getConfidenceVariant = (confidence: string): "default" | "secondary" | "destructive" | "outline" => {
    switch (confidence) {
      case 'Strong Match':
        return 'default';
      case 'Good Match':
        return 'secondary';
      case 'Partial Match':
        return 'outline';
      default:
        return 'outline';
    }
  };

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
            {result.matches.length} Candidates Found
          </Badge>
        </div>

        <div className="max-w-4xl mx-auto space-y-6">
          {/* Title */}
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-2">
              <Users className="w-8 h-8" />
              Matching Candidates
            </h1>
            <div className="flex items-center gap-2 mt-2 text-slate-600 dark:text-slate-400">
              <Briefcase className="w-4 h-4" />
              <span>Matching for: <span className="font-medium text-foreground">{formatRoleContext(result.role_context)}</span></span>
            </div>
            <p className="text-slate-600 dark:text-slate-400 mt-1">
              Candidates ranked by match score based on skills, experience, and domain relevance
            </p>
          </div>

          {/* No Results */}
          {result.matches.length === 0 && (
            <Card>
              <CardContent className="pt-6 text-center py-12">
                <Users className="w-16 h-16 text-slate-300 dark:text-slate-700 mx-auto mb-4" />
                <p className="text-lg font-medium mb-2">No matches found</p>
                <p className="text-slate-500 dark:text-slate-400 mb-4">
                  Try submitting a different job description
                </p>
                <Button onClick={() => navigate('/employer')}>
                  Submit New Job Description
                </Button>
              </CardContent>
            </Card>
          )}

          {/* Candidate Cards */}
          {result.matches.map((candidate, idx) => {
            const isExpanded = expandedCards.has(idx);
            return (
              <Card key={idx} className="overflow-hidden">
                <CardHeader className="bg-muted/50">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center font-bold text-primary text-lg">
                        {idx + 1}
                      </div>
                      <div>
                        <CardTitle className="text-xl">{candidate.name}</CardTitle>
                        <CardDescription className="flex items-center gap-2 mt-1">
                          {getConfidenceIcon(candidate.confidence)}
                          <span className="font-medium">{candidate.confidence}</span>
                        </CardDescription>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <div className="text-3xl font-bold text-primary">
                          {Math.round(candidate.score)}%
                        </div>
                        <div className="text-xs text-slate-500 dark:text-slate-400">Match Score</div>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => toggleCard(idx)}
                        className="flex items-center gap-1"
                      >
                        {isExpanded ? (
                          <span>Hide Details <ChevronUp className="w-4 h-4 inline" /></span>
                        ) : (
                          <span>View Details <ChevronDown className="w-4 h-4 inline" /></span>
                        )}
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="pt-6 space-y-4">
                  {/* Score Bar */}
                  <div>
                    <Progress value={candidate.score} className="h-2" />
                  </div>

                  {/* Summary Stats */}
                  {candidate.total_jd_skills && (
                    <div className="flex gap-4 text-sm">
                      <div className="flex items-center gap-2">
                        <CheckCircle2 className="w-4 h-4 text-green-500" />
                        <span className="text-slate-600 dark:text-slate-400">
                          <span className="font-semibold text-green-600 dark:text-green-400">{candidate.matched_skill_count}</span> / {candidate.total_jd_skills} skills matched
                        </span>
                      </div>
                      {candidate.unmatched_skill_count && candidate.unmatched_skill_count > 0 && (
                        <div className="flex items-center gap-2">
                          <XCircle className="w-4 h-4 text-orange-500" />
                          <span className="text-slate-600 dark:text-slate-400">
                            <span className="font-semibold text-orange-600 dark:text-orange-400">{candidate.unmatched_skill_count}</span> missing
                          </span>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Matched Skills */}
                  <div>
                    <h4 className="text-sm font-medium mb-3">Matched Skills</h4>
                    <div className="flex flex-wrap gap-2">
                      {candidate.matches.map((match) => {
                        const isVerified = match.includes('(verified)');
                        return (
                          <Badge
                            key={match}
                            variant={isVerified ? 'default' : 'secondary'}
                            className={isVerified ? 'bg-green-500/20 text-green-700 hover:bg-green-500/30' : ''}
                          >
                            {match}
                          </Badge>
                        );
                      })}
                    </div>
                    <div className="flex gap-4 mt-3 text-xs text-slate-500 dark:text-slate-400">
                      <span className="flex items-center gap-1">
                        <Badge variant="default" className="w-2 h-2 p-0 rounded-full" />
                        Verified (work experience)
                      </span>
                      <span className="flex items-center gap-1">
                        <Badge variant="secondary" className="w-2 h-2 p-0 rounded-full" />
                        Inferred/Unmapped
                      </span>
                    </div>
                  </div>

                  {/* Detailed Skill Breakdown (Expandable) */}
                  {isExpanded && (
                    <div className="border-t pt-4 space-y-4">
                      <h4 className="text-sm font-semibold">Detailed Skill Analysis</h4>

                      {!candidate.skill_breakdown || candidate.skill_breakdown.length === 0 ? (
                        <div className="text-sm text-slate-500 dark:text-slate-400 italic">
                          No detailed breakdown available. Check browser console for data structure.
                        </div>
                      ) : (
                        <>
                        {/* Skill Breakdown Table */}
                        <div className="rounded-lg border overflow-hidden">
                          <table className="w-full text-sm">
                            <thead className="bg-muted">
                              <tr>
                                <th className="px-3 py-2 text-left font-medium">Skill</th>
                                <th className="px-3 py-2 text-left font-medium">Type</th>
                                <th className="px-3 py-2 text-left font-medium">Match</th>
                                <th className="px-3 py-2 text-right font-medium">Weight</th>
                                <th className="px-3 py-2 text-right font-medium">Exp (Months)</th>
                                <th className="px-3 py-2 text-center font-medium">Last Used</th>
                                <th className="px-3 py-2 text-right font-medium">Recency</th>
                                <th className="px-3 py-2 text-right font-medium">Competency</th>
                                <th className="px-3 py-2 text-right font-medium">Contribution</th>
                              </tr>
                            </thead>
                            <tbody className="divide-y">
                              {candidate.skill_breakdown.map((skill, skillIdx) => (
                                <tr key={skillIdx} className="hover:bg-muted/50">
                                  <td className="px-3 py-2 font-medium">{skill.skill_name}</td>
                                  <td className="px-3 py-2">
                                    <Badge variant={skill.type === 'Explicit' ? 'default' : 'secondary'} className="text-xs">
                                      {skill.type}
                                    </Badge>
                                  </td>
                                  <td className="px-3 py-2">
                                    <Badge
                                      variant={skill.match_type === 'Verified' ? 'default' : 'outline'}
                                      className={`text-xs ${skill.match_type === 'Verified' ? 'bg-green-500/20 text-green-700' : 'bg-orange-500/20 text-orange-700'}`}
                                    >
                                      {skill.match_type}
                                    </Badge>
                                  </td>
                                  <td className="px-3 py-2 text-right">{skill.weight?.toFixed(2)}</td>
                                  <td className="px-3 py-2 text-right">{skill.experience_months}</td>
                                  <td className="px-3 py-2 text-center text-xs text-slate-600 dark:text-slate-400">
                                    {skill.last_used_date}
                                  </td>
                                  <td className="px-3 py-2 text-right">{(skill.recency_score??0 * 100).toFixed(0)}%</td>
                                  <td className="px-3 py-2 text-right">{(skill.competency_score??0 * 100).toFixed(0)}%</td>
                                  <td className="px-3 py-2 text-right font-semibold">{(skill.contribution_to_total??0 * 100).toFixed(1)}%</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>

                        {/* Unmatched Skills */}
                        {candidate.unmatched_skills && candidate.unmatched_skills.length > 0 && (
                          <div>
                            <h5 className="text-sm font-medium mb-2 text-orange-600 dark:text-orange-400">
                              Unmatched Skills
                            </h5>
                            <div className="flex flex-wrap gap-2">
                              {candidate.unmatched_skills.map((unmatched, skillIdx) => (
                                <Badge key={skillIdx} variant="outline" className="bg-orange-500/10 text-orange-700 border-orange-500/30">
                                  {unmatched.skill_name} ({unmatched.type})
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}
                        </>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            );
          })}

          {/* Action Buttons */}
          {result.matches.length > 0 && (
            <div className="flex gap-4">
              <Button onClick={() => navigate('/employer')} variant="outline" className="flex-1">
                Submit New Job Description
              </Button>
              <Button onClick={() => navigate('/candidate')} className="flex-1">
                Add Candidate Resume
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
