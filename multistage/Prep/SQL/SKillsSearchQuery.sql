use ATSCohort;
/*
DECLARE @vec VECTOR(768) = AI_GENERATE_EMBEDDINGS(CONCAT('Skill: ' , 'Java' ,'. Category: ', '.NET Framework for web development') USE MODEL OLLAMA_NOMIC_EMBED_TEXT_768 )
SELECT TOP (1000) [SkillID]
      ,[SkillName]
      ,[Category]
      ,[Information]
      ,[IsProgrammingLanguage]
      ,[IsFramework]
      ,[IsTool]
      ,[Backend]
      ,[Testing]
      ,[SkillVector]
  FROM [ATSCohort].[dbo].[MasterSkills] 
  order by VECTOR_DISTANCE('cosine', CAST(SkillVector AS VECTOR(768)), @vec);
  */
  