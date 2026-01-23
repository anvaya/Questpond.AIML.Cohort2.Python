USE [ATSCohort]
GO
/****** Object:  UserDefinedFunction [dbo].[BuildSkillEmbeddingText]    Script Date: 20-01-2026 22:38:01 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE   FUNCTION [dbo].[BuildSkillEmbeddingText]
(
    @SkillName NVARCHAR(255),
    @Category NVARCHAR(255),
    @SkillType NVARCHAR(100),
    @Aliases NVARCHAR(MAX)
)
RETURNS NVARCHAR(MAX)
AS
BEGIN
    DECLARE @AliasText NVARCHAR(MAX) = '';

    IF (@Aliases IS NOT NULL AND ISJSON(@Aliases) = 1)
    BEGIN
        SELECT @AliasText = STRING_AGG(value, ' ')
        FROM OPENJSON(@Aliases);
    END

    RETURN LTRIM(RTRIM(
        CONCAT(
            @SkillName, ' ',
            @Category, ' ',
            @SkillType, ' ',
            @AliasText
        )
    ));
END;
GO
/****** Object:  Table [dbo].[MasterSkills]    Script Date: 20-01-2026 22:42:58 ******/
CREATE TABLE [dbo].[MasterSkills](
	[SkillID] [int] IDENTITY(1,1) NOT NULL,
	[SkillName] [nvarchar](255) NULL,
	[Category] [nvarchar](255) NULL,
	[Information] [nvarchar](max) NULL,
	[IsProgrammingLanguage] [bit] NULL,
	[IsFramework] [bit] NULL,
	[IsTool] [bit] NULL,
	[Backend] [bit] NULL,
	[Testing] [bit] NULL,
	[SkillVector] [vector](768) NULL,
	[InformationVector] [vector](768) NULL,
	[SkillCode] [nvarchar](200) NULL,
	[Tokens] [nvarchar](max) NULL,
	[ParentSkillId] [nvarchar](200) NULL,
	[Aliases] [nvarchar](max) NULL,
	[DisambiguationRules] [nvarchar](max) NULL,
	[SkillType] [nvarchar](100) NULL,
PRIMARY KEY CLUSTERED 
(
	[SkillID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO

/****** Object:  Table [dbo].[EmbeddingCache]    Script Date: 20-01-2026 22:43:44 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[EmbeddingCache](
	[CacheID] [int] IDENTITY(1,1) NOT NULL,
	[InputText] [nvarchar](1000) NOT NULL,
	[Embedding] [vector](768) NOT NULL,
	[CreatedAt] [datetime] NULL,
	[AccessedAt] [datetime] NULL,
	[AccessCount] [int] NULL,
PRIMARY KEY CLUSTERED 
(
	[CacheID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
 CONSTRAINT [UQ_InputText] UNIQUE NONCLUSTERED 
(
	[InputText] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

ALTER TABLE [dbo].[EmbeddingCache] ADD  DEFAULT (getdate()) FOR [CreatedAt]
GO

ALTER TABLE [dbo].[EmbeddingCache] ADD  DEFAULT (getdate()) FOR [AccessedAt]
GO

ALTER TABLE [dbo].[EmbeddingCache] ADD  DEFAULT ((1)) FOR [AccessCount]
GO

/****** Object:  Table [dbo].[Candidates]    Script Date: 20-01-2026 22:38:01 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Candidates](
	[CandidateID] [int] IDENTITY(1,1) NOT NULL,
	[FullName] [nvarchar](255) NOT NULL,
	[Status] [nchar](10) NULL,
	[DocumentName] [nvarchar](150) NULL,
	[DocumentHash] [nvarchar](150) NULL,
	[ExperienceJson] [json] NULL,
PRIMARY KEY CLUSTERED 
(
	[CandidateID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[CandidateSkills]    Script Date: 20-01-2026 22:38:01 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[CandidateSkills](
	[CandidateSkillID] [int] IDENTITY(1,1) NOT NULL,
	[CandidateID] [int] NULL,
	[MasterSkillID] [int] NULL,
	[ExperienceMonths] [int] NULL,
	[LastUsedDate] [date] NULL,
	[MatchConfidence] [float] NULL,
	[TotalMonths] [int] NULL,
	[JuniorMonths] [int] NOT NULL,
	[MidMonths] [int] NOT NULL,
	[SeniorMonths] [int] NOT NULL,
	[FirstUsedDate] [date] NULL,
	[EvidenceSources] [nvarchar](255) NULL,
	[EvidenceScore] [decimal](4, 2) NOT NULL,
	[NormalizationConfidence] [decimal](4, 2) NOT NULL,
	[NormalizationMethod] [nvarchar](50) NULL,
	[MaxEvidenceStrength] [int] NULL,
PRIMARY KEY CLUSTERED 
(
	[CandidateSkillID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[EvidenceTypes]    Script Date: 20-01-2026 22:38:01 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[EvidenceTypes](
	[EvidenceType] [nvarchar](50) NOT NULL,
	[Strength] [int] NOT NULL,
	[Description] [nvarchar](255) NULL,
PRIMARY KEY CLUSTERED 
(
	[EvidenceType] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Jobs]    Script Date: 20-01-2026 22:38:01 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Jobs](
	[JobID] [uniqueidentifier] NOT NULL,
	[JobType] [nvarchar](50) NOT NULL,
	[Status] [nvarchar](50) NOT NULL,
	[Progress] [int] NOT NULL,
	[Message] [nvarchar](max) NULL,
	[Result] [nvarchar](max) NULL,
	[InputData] [nvarchar](max) NULL,
	[CreatedAt] [datetime2](7) NOT NULL,
	[UpdatedAt] [datetime2](7) NOT NULL,
	[CompletedAt] [datetime2](7) NULL,
	[ErrorMessage] [nvarchar](max) NULL,
PRIMARY KEY CLUSTERED 
(
	[JobID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[RoleSkillMappings]    Script Date: 20-01-2026 22:38:01 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[RoleSkillMappings](
	[RolePattern] [nvarchar](200) NOT NULL,
	[SkillCode] [nvarchar](200) NOT NULL,
	[EvidenceType] [nvarchar](50) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[RolePattern] ASC,
	[SkillCode] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[RoleSkillTypeWeights]    Script Date: 20-01-2026 22:38:01 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[RoleSkillTypeWeights](
	[RoleCode] [nvarchar](100) NOT NULL,
	[SkillType] [nvarchar](100) NOT NULL,
	[WeightMultiplier] [decimal](5, 2) NOT NULL,
	[Description] [nvarchar](255) NULL,
	[PrimaryDomain] [nvarchar](50) NULL,
	[SeniorityLevel] [nvarchar](30) NULL,
 CONSTRAINT [PK_RoleSkillTypeWeights] PRIMARY KEY CLUSTERED 
(
	[RoleCode] ASC,
	[SkillType] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SkillImplications]    Script Date: 20-01-2026 22:38:01 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SkillImplications](
	[FromSkillCode] [nvarchar](200) NOT NULL,
	[ToSkillCode] [nvarchar](200) NOT NULL,
	[Confidence] [float] NOT NULL,
	[Explanation] [nvarchar](255) NULL,
PRIMARY KEY CLUSTERED 
(
	[FromSkillCode] ASC,
	[ToSkillCode] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SkillNormalizationCache]    Script Date: 20-01-2026 22:38:01 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SkillNormalizationCache](
	[Fingerprint] [char](40) NOT NULL,
	[NormalizedText] [nvarchar](200) NOT NULL,
	[ResolvedSkillId] [varchar](64) NULL,
	[CreatedAt] [datetime2](7) NULL,
PRIMARY KEY CLUSTERED 
(
	[Fingerprint] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SkillTypeWeights]    Script Date: 20-01-2026 22:38:01 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SkillTypeWeights](
	[SkillType] [nvarchar](100) NOT NULL,
	[BaseWeight] [decimal](5, 2) NOT NULL,
	[Description] [nvarchar](255) NULL,
PRIMARY KEY CLUSTERED 
(
	[SkillType] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SoftSignals]    Script Date: 20-01-2026 22:38:01 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SoftSignals](
	[SoftSignalId] [varchar](255) NOT NULL,
	[Description] [varchar](500) NULL,
	[EvidenceRules] [nvarchar](max) NOT NULL,
	[IsDisabled] [bit] NULL,
PRIMARY KEY CLUSTERED 
(
	[SoftSignalId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[UnmappedSkills]    Script Date: 20-01-2026 22:38:01 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[UnmappedSkills](
	[UnmappedSkillID] [int] IDENTITY(1,1) NOT NULL,
	[CandidateID] [int] NOT NULL,
	[RawSkillName] [nvarchar](255) NOT NULL,
	[RoleTitle] [nvarchar](255) NULL,
	[ExperienceMonths] [int] NULL,
	[LastUsedDate] [date] NULL,
	[DiscoveryDate] [datetime] NULL,
	[ClosestMasterSkillID] [int] NULL,
	[VectorDistance] [float] NULL,
PRIMARY KEY CLUSTERED 
(
	[UnmappedSkillID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
ALTER TABLE [dbo].[CandidateSkills] ADD  DEFAULT ((0)) FOR [JuniorMonths]
GO
ALTER TABLE [dbo].[CandidateSkills] ADD  DEFAULT ((0)) FOR [MidMonths]
GO
ALTER TABLE [dbo].[CandidateSkills] ADD  DEFAULT ((0)) FOR [SeniorMonths]
GO
ALTER TABLE [dbo].[CandidateSkills] ADD  DEFAULT ((0.0)) FOR [EvidenceScore]
GO
ALTER TABLE [dbo].[CandidateSkills] ADD  DEFAULT ((0.0)) FOR [NormalizationConfidence]
GO
ALTER TABLE [dbo].[Jobs] ADD  DEFAULT (newid()) FOR [JobID]
GO
ALTER TABLE [dbo].[Jobs] ADD  DEFAULT ((0)) FOR [Progress]
GO
ALTER TABLE [dbo].[Jobs] ADD  DEFAULT (getdate()) FOR [CreatedAt]
GO
ALTER TABLE [dbo].[Jobs] ADD  DEFAULT (getdate()) FOR [UpdatedAt]
GO
ALTER TABLE [dbo].[SkillImplications] ADD  DEFAULT ((1.0)) FOR [Confidence]
GO
ALTER TABLE [dbo].[SkillNormalizationCache] ADD  DEFAULT (sysutcdatetime()) FOR [CreatedAt]
GO
ALTER TABLE [dbo].[SoftSignals] ADD  DEFAULT ((0)) FOR [IsDisabled]
GO
ALTER TABLE [dbo].[UnmappedSkills] ADD  DEFAULT (getdate()) FOR [DiscoveryDate]
GO
ALTER TABLE [dbo].[CandidateSkills]  WITH CHECK ADD FOREIGN KEY([CandidateID])
REFERENCES [dbo].[Candidates] ([CandidateID])
GO
ALTER TABLE [dbo].[CandidateSkills]  WITH CHECK ADD FOREIGN KEY([MasterSkillID])
REFERENCES [dbo].[MasterSkills] ([SkillID])
GO
ALTER TABLE [dbo].[UnmappedSkills]  WITH CHECK ADD FOREIGN KEY([CandidateID])
REFERENCES [dbo].[Candidates] ([CandidateID])
GO
ALTER TABLE [dbo].[UnmappedSkills]  WITH CHECK ADD FOREIGN KEY([ClosestMasterSkillID])
REFERENCES [dbo].[MasterSkills] ([SkillID])
GO
