import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Upload, FileText, X } from 'lucide-react';
import { submitCandidateJob } from '@/lib/api';

export function CandidateUploadPage() {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (!file.name.toLowerCase().endsWith('.pdf')) {
        setError('Please select a PDF file');
        setSelectedFile(null);
        return;
      }
      setError(null);
      setSelectedFile(file);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) {
      if (!file.name.toLowerCase().endsWith('.pdf')) {
        setError('Please select a PDF file');
        setSelectedFile(null);
        return;
      }
      setError(null);
      setSelectedFile(file);
    }
  };

  const handleSubmit = async () => {
    if (!selectedFile) {
      setError('Please select a file');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const jobId = await submitCandidateJob(selectedFile);
      navigate(`/progress/${jobId}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit job');
      setIsSubmitting(false);
    }
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

        <div className="max-w-2xl mx-auto">
          <Card>
            <CardHeader>
              <CardTitle className="text-3xl">Upload Candidate Resume</CardTitle>
              <CardDescription>
                Upload a PDF resume to extract candidate profile using AI
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Upload Area */}
              <div
                onDrop={handleDrop}
                onDragOver={(e) => e.preventDefault()}
                className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
                  selectedFile
                    ? 'border-primary bg-primary/5'
                    : 'border-slate-300 dark:border-slate-700 hover:border-primary/50'
                }`}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf"
                  onChange={handleFileSelect}
                  className="hidden"
                />

                {!selectedFile ? (
                  <div className="space-y-4">
                    <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto">
                      <Upload className="w-8 h-8 text-primary" />
                    </div>
                    <div>
                      <p className="text-lg font-medium mb-2">
                        Drag & drop your resume here
                      </p>
                      <p className="text-sm text-slate-500 dark:text-slate-400 mb-4">
                        PDF files only
                      </p>
                      <Button onClick={() => fileInputRef.current?.click()}>
                        Browse Files
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto">
                      <FileText className="w-8 h-8 text-primary" />
                    </div>
                    <div>
                      <p className="text-lg font-medium mb-1">{selectedFile.name}</p>
                      <p className="text-sm text-slate-500 dark:text-slate-400">
                        {(selectedFile.size / 1024).toFixed(1)} KB
                      </p>
                    </div>
                    <div className="flex gap-2 justify-center">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          setSelectedFile(null);
                          setError(null);
                        }}
                      >
                        <X className="w-4 h-4 mr-2" />
                        Remove
                      </Button>
                      <Button
                        size="sm"
                        onClick={() => fileInputRef.current?.click()}
                      >
                        Change
                      </Button>
                    </div>
                  </div>
                )}
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
                disabled={!selectedFile || isSubmitting}
                className="w-full"
                size="lg"
              >
                {isSubmitting ? 'Submitting...' : 'Process Resume'}
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
