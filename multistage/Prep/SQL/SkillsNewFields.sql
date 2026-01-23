ALTER TABLE MasterSkills
ADD SkillCode nvarchar(200) null,
Tokens nvarchar(MAX);

CREATE TABLE SoftSignals
(
	SoftSignalId varchar(255) not null PRIMARY KEY,
	[Description] varchar(500) null,
	EvidenceRules nvarchar(MAX) not null,
	IsDisabled bit default 0 null,
);

CREATE TABLE SkillNormalizationCache (
    Fingerprint CHAR(40) PRIMARY KEY,
    NormalizedText NVARCHAR(200) NOT NULL,
    ResolvedSkillId VARCHAR(64) NULL,
    CreatedAt DATETIME2 DEFAULT SYSUTCDATETIME()
);