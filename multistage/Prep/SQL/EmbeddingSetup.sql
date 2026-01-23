
USE master;
GO

-- Enable rest endpoint
sp_configure 'external rest endpoint enabled', 1
GO
RECONFIGURE WITH OVERRIDE;
GO

-- Turn on Trace Flags for Vector Search
DBCC TRACEON (466, 474, 13981, -1) 
GO

-- Check trace flags status
DBCC TraceStatus
GO

USE ATSCohort;

DROP EXTERNAL MODEL OLLAMA_NOMIC_EMBED_TEXT_768;

CREATE EXTERNAL MODEL OLLAMA_NOMIC_EMBED_TEXT_768
WITH
(
 LOCATION  = 'https://localhost:7368/api/embed',
 MODEL_TYPE = EMBEDDINGS,
 MODEL = 'nomic-embed-text', 
 API_FORMAT = 'Ollama'
);


EXECUTE sp_configure 'external rest endpoint enabled', 1;
RECONFIGURE WITH OVERRIDE;


Update m1
SET SkillVector = AI_GENERATE_EMBEDDINGS(CONCAT(SkillName, '.', iif(al.als is null,'', concat(' Also known as: ', al.als,'.'))) USE MODEL OLLAMA_NOMIC_EMBED_TEXT_768)
from MasterSkills m1
left join 
(SELECT SkillId,STRING_AGG(j.value, ',') AS als FROM MasterSkills m CROSS APPLY OPENJSON(m.Aliases) as j group by SkillId) al
on m1.SkillId = al.SkillId