import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { FileText, Users } from 'lucide-react';

export function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <div className="container mx-auto px-4 py-16">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-slate-900 dark:text-slate-50 mb-4">
            AI-Powered ATS
          </h1>
          <p className="text-xl text-slate-600 dark:text-slate-400">
            Proof of Concept - Intelligent Resume Parsing & Candidate Matching
          </p>
        </div>

        {/* Action Cards */}
        <div className="max-w-4xl mx-auto grid md:grid-cols-2 gap-8">
          {/* Candidate Processing Card */}
          <Card className="hover:shadow-lg transition-shadow cursor-pointer border-2 hover:border-primary/50">
            <CardHeader>
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                <FileText className="w-6 h-6 text-primary" />
              </div>
              <CardTitle className="text-2xl">Process Candidate Resume</CardTitle>
              <CardDescription className="text-base">
                Upload a PDF resume to extract candidate profile, skills, and experience using AI
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button
                onClick={() => navigate('/candidate')}
                className="w-full"
                size="lg"
              >
                Upload Resume
              </Button>
            </CardContent>
          </Card>

          {/* Employer Matching Card */}
          <Card className="hover:shadow-lg transition-shadow cursor-pointer border-2 hover:border-primary/50">
            <CardHeader>
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                <Users className="w-6 h-6 text-primary" />
              </div>
              <CardTitle className="text-2xl">Match Candidates to Job</CardTitle>
              <CardDescription className="text-base">
                Submit a job description to find and rank matching candidates from the database
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button
                onClick={() => navigate('/employer')}
                className="w-full"
                size="lg"
              >
                Find Candidates
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Info Section */}
        <div className="max-w-4xl mx-auto mt-16 text-center">
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Powered by LLM-based parsing and vector similarity matching
          </p>
        </div>
      </div>
    </div>
  );
}
