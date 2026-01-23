USE [ATSCohort]
GO

-- Drop table if exists
IF OBJECT_ID('dbo.EmbeddingCache', 'U') IS NOT NULL
    DROP TABLE dbo.EmbeddingCache
GO

-- Create EmbeddingCache table to store pre-computed embeddings
CREATE TABLE dbo.EmbeddingCache
(
    CacheID INT IDENTITY(1,1) PRIMARY KEY,
    InputText NVARCHAR(1000) NOT NULL,
    Embedding VECTOR(768) NOT NULL,
    CreatedAt DATETIME DEFAULT GETDATE(),
    AccessedAt DATETIME DEFAULT GETDATE(),
    AccessCount INT DEFAULT 1,
    CONSTRAINT UQ_InputText UNIQUE (InputText)
)
GO

-- Create index on InputText for faster lookups
CREATE INDEX IX_EmbeddingCache_InputText ON dbo.EmbeddingCache(InputText)
GO

-- Create index on AccessedAt for cache management
CREATE INDEX IX_EmbeddingCache_AccessedAt ON dbo.EmbeddingCache(AccessedAt)
GO

PRINT 'EmbeddingCache table created successfully.'
GO
