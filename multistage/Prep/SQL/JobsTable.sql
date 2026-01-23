-- Job table for async orchestration of AI workflows
CREATE TABLE Jobs (
    JobID UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    JobType NVARCHAR(50) NOT NULL, -- 'candidate' or 'employer'
    Status NVARCHAR(50) NOT NULL, -- 'queued', 'processing', 'completed', 'failed'
    Progress INT NOT NULL DEFAULT 0, -- 0-100
    Message NVARCHAR(MAX), -- Human-readable status message
    Result NVARCHAR(MAX), -- JSON output payload
    InputData NVARCHAR(MAX), -- JSON input payload (file path, JD text, etc.)
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    UpdatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    CompletedAt DATETIME2 NULL,
    ErrorMessage NVARCHAR(MAX) NULL -- Detailed error information
);

-- Index for faster lookups
CREATE INDEX IX_Jobs_Status ON Jobs(Status);
CREATE INDEX IX_Jobs_JobType ON Jobs(JobType);
