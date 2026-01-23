import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { LandingPage } from '@/pages/LandingPage';
import { CandidateUploadPage } from '@/pages/CandidateUploadPage';
import { EmployerJobPage } from '@/pages/EmployerJobPage';
import { JobProgressPage } from '@/pages/JobProgressPage';
import { CandidateResultPage } from '@/pages/CandidateResultPage';
import { EmployerResultPage } from '@/pages/EmployerResultPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/candidate" element={<CandidateUploadPage />} />
        <Route path="/employer" element={<EmployerJobPage />} />
        <Route path="/progress/:jobId" element={<JobProgressPage />} />
        <Route path="/candidate/result/:jobId" element={<CandidateResultPage />} />
        <Route path="/employer/result/:jobId" element={<EmployerResultPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
