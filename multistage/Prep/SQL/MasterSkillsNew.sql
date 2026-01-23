INSERT INTO dbo.MasterSkills (SkillName, Category, SkillCode, Tokens, Aliases)
SELECT * FROM (VALUES
('C#','Programming Language','language_csharp','["c#"]','["csharp","c sharp"]'),
('Java','Programming Language','language_java','["java"]','[]'),
('JavaScript','Programming Language','language_javascript','["javascript"]','["js"]'),
('TypeScript','Programming Language','language_typescript','["typescript"]','["ts"]'),
('Python','Programming Language','language_python','["python"]','[]'),
('Go','Programming Language','language_go','["go"]','["golang"]'),
('Rust','Programming Language','language_rust','["rust"]','[]'),
('PHP','Programming Language','language_php','["php"]','[]'),
('Ruby','Programming Language','language_ruby','["ruby"]','[]'),
('Kotlin','Programming Language','language_kotlin','["kotlin"]','[]'),
('Swift','Programming Language','language_swift','["swift"]','[]'),
('Scala','Programming Language','language_scala','["scala"]','[]'),
('R','Programming Language','language_r','["r"]','[]'),
('Objective-C','Programming Language','language_objective_c','["objective","c"]','[]'),
('C','Programming Language','language_c','["c"]','[]'),
('C++','Programming Language','language_cpp','["c++"]','[]'),
('Bash','Programming Language','language_bash','["bash"]','["shell"]'),
('PowerShell','Programming Language','language_powershell','["powershell"]','[]'),
('Perl','Programming Language','language_perl','["perl"]','[]'),
('Haskell','Programming Language','language_haskell','["haskell"]','[]')
) s (SkillName, Category, SkillCode, Tokens, Aliases)
WHERE NOT EXISTS (SELECT 1 FROM dbo.MasterSkills m WHERE m.SkillCode = s.SkillCode);

INSERT INTO dbo.MasterSkills (SkillName, Category, SkillCode, Tokens, Aliases, ParentSkillId)
SELECT SkillName,Category,SkillCode,Tokens,Aliases,
       (SELECT SkillID FROM dbo.MasterSkills WHERE SkillCode = ParentCode)
FROM (VALUES
('.NET','Backend Framework','framework_dotnet','["dotnet"]','[".net"]',NULL),
('.NET Core','Backend Framework','framework_dotnet_core','["dotnet","core"]','[]','framework_dotnet'),
('ASP.NET MVC','Backend Framework','framework_dotnet_aspnet_mvc','["asp","mvc"]','[]','framework_dotnet'),
('ASP.NET Web API','Backend Framework','framework_dotnet_webapi','["web","api"]','[]','framework_dotnet'),
('Spring','Backend Framework','framework_spring','["spring"]','[]','language_java'),
('Spring Boot','Backend Framework','framework_spring_boot','["spring","boot"]','[]','framework_spring'),
('Django','Backend Framework','framework_django','["django"]','[]','language_python'),
('Flask','Backend Framework','framework_flask','["flask"]','[]','language_python'),
('FastAPI','Backend Framework','framework_fastapi','["fastapi"]','[]','language_python'),
('Node.js','Backend Framework','framework_nodejs','["node","js"]','["nodejs"]','language_javascript'),
('Express.js','Backend Framework','framework_expressjs','["express","js"]','[]','framework_nodejs'),
('NestJS','Backend Framework','framework_nestjs','["nestjs"]','[]','framework_nodejs'),
('Laravel','Backend Framework','framework_laravel','["laravel"]','[]','language_php'),
('Symfony','Backend Framework','framework_symfony','["symfony"]','[]','language_php'),
('Ruby on Rails','Backend Framework','framework_rails','["rails"]','[]','language_ruby')
) s(SkillName,Category,SkillCode,Tokens,Aliases,ParentCode)
WHERE NOT EXISTS (SELECT 1 FROM dbo.MasterSkills m WHERE m.SkillCode = s.SkillCode);


INSERT INTO dbo.MasterSkills (SkillName, Category, SkillCode, Tokens, Aliases)
SELECT * FROM (VALUES
('React','Frontend Framework','web_react','["react"]','["reactjs"]'),
('Angular','Frontend Framework','web_angular','["angular"]','["angularjs"]'),
('Vue.js','Frontend Framework','web_vue','["vue"]','["vuejs"]'),
('Svelte','Frontend Framework','web_svelte','["svelte"]','[]'),
('Blazor','Frontend Framework','web_blazor','["blazor"]','[]'),
('Next.js','Frontend Framework','web_nextjs','["next","js"]','[]'),
('Nuxt.js','Frontend Framework','web_nuxtjs','["nuxt","js"]','[]'),
('HTML','Web Technology','web_html','["html"]','[]'),
('CSS','Web Technology','web_css','["css"]','[]'),
('SCSS','Web Technology','web_scss','["scss"]','[]'),
('Tailwind CSS','Web Technology','web_tailwind','["tailwind"]','[]'),
('Bootstrap','Web Technology','web_bootstrap','["bootstrap"]','[]')
) s (SkillName, Category, SkillCode, Tokens, Aliases)
WHERE NOT EXISTS (SELECT 1 FROM dbo.MasterSkills m WHERE m.SkillCode = s.SkillCode);

INSERT INTO dbo.MasterSkills (SkillName, Category, SkillCode, Tokens, Aliases)
SELECT * FROM (VALUES
('SQL Server','Database','db_sql_server','["sql","server"]','["mssql"]'),
('PostgreSQL','Database','db_postgres','["postgresql"]','["postgres"]'),
('MySQL','Database','db_mysql','["mysql"]','[]'),
('Oracle','Database','db_oracle','["oracle"]','[]'),
('MongoDB','Database','db_mongodb','["mongodb"]','["mongo"]'),
('Redis','Database','db_redis','["redis"]','[]'),
('Elasticsearch','Database','db_elasticsearch','["elasticsearch"]','["elastic"]'),
('Cassandra','Database','db_cassandra','["cassandra"]','[]'),
('DynamoDB','Database','db_dynamodb','["dynamodb"]','[]'),
('SQLite','Database','db_sqlite','["sqlite"]','[]')
) s(SkillName, Category, SkillCode, Tokens, Aliases)
WHERE NOT EXISTS (SELECT 1 FROM dbo.MasterSkills m WHERE m.SkillCode = s.SkillCode);


INSERT INTO dbo.MasterSkills (SkillName, Category, SkillCode, Tokens, Aliases)
SELECT * FROM (VALUES
('Docker','DevOps Tool','tool_docker','["docker"]','[]'),
('Kubernetes','DevOps Tool','tool_kubernetes','["kubernetes"]','["k8s"]'),
('Terraform','DevOps Tool','tool_terraform','["terraform"]','[]'),
('Ansible','DevOps Tool','tool_ansible','["ansible"]','[]'),
('Jenkins','CI/CD','tool_jenkins','["jenkins"]','[]'),
('GitHub Actions','CI/CD','tool_github_actions','["github","actions"]','[]'),
('Azure DevOps','CI/CD','tool_azure_devops','["azure","devops"]','["ado"]'),
('GitLab CI','CI/CD','tool_gitlab_ci','["gitlab","ci"]','[]'),
('CircleCI','CI/CD','tool_circleci','["circleci"]','[]')
) s(SkillName, Category, SkillCode, Tokens, Aliases)
WHERE NOT EXISTS (SELECT 1 FROM dbo.MasterSkills m WHERE m.SkillCode = s.SkillCode);

INSERT INTO dbo.MasterSkills (SkillName, Category, SkillCode, Tokens, Aliases)
SELECT * FROM (VALUES
('Amazon Web Services','Cloud','cloud_aws','["aws"]','[]'),
('Microsoft Azure','Cloud','cloud_azure','["azure"]','[]'),
('Google Cloud Platform','Cloud','cloud_gcp','["gcp"]','[]'),
('AWS EC2','Cloud Service','cloud_aws_ec2','["ec2"]','[]'),
('AWS S3','Cloud Service','cloud_aws_s3','["s3"]','[]'),
('Azure App Service','Cloud Service','cloud_azure_app_service','["app","service"]','[]'),
('Azure Functions','Cloud Service','cloud_azure_functions','["functions"]','[]'),
('AWS Lambda','Cloud Service','cloud_aws_lambda','["lambda"]','[]')
) s(SkillName, Category, SkillCode, Tokens, Aliases)
WHERE NOT EXISTS (SELECT 1 FROM dbo.MasterSkills m WHERE m.SkillCode = s.SkillCode);

INSERT INTO dbo.MasterSkills (SkillName, Category, SkillCode, Tokens, Aliases)
SELECT * FROM (VALUES
('Unit Testing','Testing','testing_unit','["unit","testing"]','[]'),
('Integration Testing','Testing','testing_integration','["integration","testing"]','[]'),
('Selenium','Testing','testing_selenium','["selenium"]','[]'),
('JUnit','Testing','testing_junit','["junit"]','[]'),
('xUnit','Testing','testing_xunit','["xunit"]','[]'),
('OAuth 2.0','Security','security_oauth2','["oauth2"]','[]'),
('JWT','Security','security_jwt','["jwt"]','[]'),
('Microservices','Architecture','arch_microservices','["microservices"]','[]'),
('REST API','Architecture','arch_rest','["rest","api"]','[]'),
('Event-Driven Architecture','Architecture','arch_event_driven','["event","driven"]','[]'),
('CQRS','Architecture','arch_cqrs','["cqrs"]','[]'),
('Domain-Driven Design','Architecture','arch_ddd','["ddd"]','[]')
) s(SkillName, Category, SkillCode, Tokens, Aliases)
WHERE NOT EXISTS (SELECT 1 FROM dbo.MasterSkills m WHERE m.SkillCode = s.SkillCode);



IF NOT EXISTS (
    SELECT 1 FROM dbo.MasterSkills WHERE SkillCode = 'ai_root'
)
BEGIN
    INSERT INTO dbo.MasterSkills (
        SkillName,
        Category,
        Information,
        SkillCode,
        Tokens,
        Aliases,
        DisambiguationRules
    )
    VALUES (
        'Artificial Intelligence',
        'AI Domain',
        'Root domain for AI, ML, LLM, and GenAI skills',
        'ai_root',
        '["artificial","intelligence"]',
        '["ai"]',
        '{"confidence_weight":"low"}'
    );
END


DECLARE @AiRootId INT = (SELECT SkillID FROM dbo.MasterSkills WHERE SkillCode = 'ai_root');

INSERT INTO dbo.MasterSkills (SkillName, Category, Information, SkillCode, Tokens, Aliases, ParentSkillId)
SELECT * FROM (
    SELECT 'Machine Learning','AI Concept','ML fundamentals','ai_concept_machine_learning',
           '["machine","learning"]','["ml"]',@AiRootId
    UNION ALL
    SELECT 'Deep Learning','AI Concept','Neural networks and deep models','ai_concept_deep_learning',
           '["deep","learning"]','["dl"]',
           (SELECT SkillID FROM dbo.MasterSkills WHERE SkillCode='ai_concept_machine_learning')
    UNION ALL
    SELECT 'Natural Language Processing','AI Concept','Text and language processing','ai_concept_nlp',
           '["natural","language","processing"]','["nlp"]',
           (SELECT SkillID FROM dbo.MasterSkills WHERE SkillCode='ai_concept_machine_learning')
    UNION ALL
    SELECT 'Computer Vision','AI Concept','Image and video processing','ai_concept_computer_vision',
           '["computer","vision"]','["cv"]',
           (SELECT SkillID FROM dbo.MasterSkills WHERE SkillCode='ai_concept_machine_learning')
) s (SkillName, Category, Information, SkillCode, Tokens, Aliases, ParentSkillId)
WHERE NOT EXISTS (
    SELECT 1 FROM dbo.MasterSkills m WHERE m.SkillCode = s.SkillCode
);


INSERT INTO dbo.MasterSkills (SkillName, Category, Information, SkillCode, Tokens, Aliases, ParentSkillId)
SELECT * FROM (
    SELECT 'TensorFlow','AI Framework','Deep learning framework','ai_framework_tensorflow',
           '["tensorflow"]','["tf"]',
           (SELECT SkillID FROM dbo.MasterSkills WHERE SkillCode='ai_concept_machine_learning')
    UNION ALL
    SELECT 'PyTorch','AI Framework','Deep learning framework','ai_framework_pytorch',
           '["pytorch"]','["torch"]',
           (SELECT SkillID FROM dbo.MasterSkills WHERE SkillCode='ai_concept_machine_learning')
    UNION ALL
    SELECT 'scikit-learn','AI Framework','ML utilities and algorithms','ai_framework_scikit_learn',
           '["scikit","learn"]','["sklearn"]',
           (SELECT SkillID FROM dbo.MasterSkills WHERE SkillCode='ai_concept_machine_learning')
) s (SkillName, Category, Information, SkillCode, Tokens, Aliases, ParentSkillId)
WHERE NOT EXISTS (
    SELECT 1 FROM dbo.MasterSkills m WHERE m.SkillCode = s.SkillCode
);


INSERT INTO dbo.MasterSkills (SkillName, Category, Information, SkillCode, Tokens, Aliases, ParentSkillId)
SELECT * FROM (
    SELECT 'Large Language Models','AI Specialization','Transformer-based language models','ai_llm',
           '["large","language","model"]','["llm"]',
           (SELECT SkillID FROM dbo.MasterSkills WHERE SkillCode='ai_concept_nlp')
    UNION ALL
    SELECT 'Prompt Engineering','AI Specialization','Designing effective prompts','ai_prompt_engineering',
           '["prompt","engineering"]','[]',
           (SELECT SkillID FROM dbo.MasterSkills WHERE SkillCode='ai_llm')
    UNION ALL
    SELECT 'Retrieval-Augmented Generation','AI Specialization','RAG pipelines','ai_rag',
           '["retrieval","augmented","generation"]','["rag"]',
           (SELECT SkillID FROM dbo.MasterSkills WHERE SkillCode='ai_llm')
    UNION ALL
    SELECT 'LLM Fine-tuning','AI Specialization','Model adaptation','ai_llm_finetuning',
           '["fine","tuning"]','[]',
           (SELECT SkillID FROM dbo.MasterSkills WHERE SkillCode='ai_llm')
) s (SkillName, Category, Information, SkillCode, Tokens, Aliases, ParentSkillId)
WHERE NOT EXISTS (
    SELECT 1 FROM dbo.MasterSkills m WHERE m.SkillCode = s.SkillCode
);

INSERT INTO dbo.MasterSkills (SkillName, Category, Information, SkillCode, Tokens, Aliases, ParentSkillId)
SELECT * FROM (
    SELECT 'Vector Databases','AI Infrastructure','Embedding storage systems','ai_vector_database',
           '["vector","database"]','[]',
           (SELECT SkillID FROM dbo.MasterSkills WHERE SkillCode='ai_rag')
    UNION ALL
    SELECT 'FAISS','AI Tool','Vector similarity search','ai_vector_faiss',
           '["faiss"]','[]',
           (SELECT SkillID FROM dbo.MasterSkills WHERE SkillCode='ai_vector_database')
    UNION ALL
    SELECT 'Pinecone','AI Tool','Managed vector database','ai_vector_pinecone',
           '["pinecone"]','[]',
           (SELECT SkillID FROM dbo.MasterSkills WHERE SkillCode='ai_vector_database')
    UNION ALL
    SELECT 'GPU Computing','AI Infrastructure','GPU-based workloads','ai_infra_gpu',
           '["gpu"]','[]',NULL
) s (SkillName, Category, Information, SkillCode, Tokens, Aliases, ParentSkillId)
WHERE NOT EXISTS (
    SELECT 1 FROM dbo.MasterSkills m WHERE m.SkillCode = s.SkillCode
);


INSERT INTO dbo.MasterSkills (SkillName, Category, Information, SkillCode, Tokens, Aliases, ParentSkillId)
SELECT * FROM (
    SELECT 'MLOps','AI DevOps','ML lifecycle management','ai_mlops',
           '["mlops"]','[]',
           (SELECT SkillID FROM dbo.MasterSkills WHERE SkillCode='ai_concept_machine_learning')
    UNION ALL
    SELECT 'Model Deployment','AI Engineering','Serving ML models','ai_model_deployment',
           '["model","deployment"]','[]',
           (SELECT SkillID FROM dbo.MasterSkills WHERE SkillCode='ai_mlops')
    UNION ALL
    SELECT 'Model Monitoring','AI Engineering','Model health tracking','ai_model_monitoring',
           '["model","monitoring"]','[]',
           (SELECT SkillID FROM dbo.MasterSkills WHERE SkillCode='ai_mlops')
) s (SkillName, Category, Information, SkillCode, Tokens, Aliases, ParentSkillId)
WHERE NOT EXISTS (
    SELECT 1 FROM dbo.MasterSkills m WHERE m.SkillCode = s.SkillCode
);

IF NOT EXISTS (
    SELECT 1 FROM dbo.MasterSkills WHERE SkillCode = 'ai_usage_assisted_dev'
)
BEGIN
    INSERT INTO dbo.MasterSkills (
        SkillName,
        Category,
        Information,
        SkillCode,
        Tokens,
        Aliases,
        DisambiguationRules
    )
    VALUES (
        'AI-Assisted Development',
        'AI Soft Signal',
        'Using AI tools for development assistance',
        'ai_usage_assisted_dev',
        '["ai","assistant"]',
        '["chatgpt","copilot"]',
        '{"confidence_weight":"very_low"}'
    );
END

CREATE TABLE dbo.SkillTypeWeights (
    SkillType NVARCHAR(100) NOT NULL PRIMARY KEY,
    BaseWeight DECIMAL(5,2) NOT NULL,
    Description NVARCHAR(255) NULL
);

CREATE TABLE dbo.RoleSkillTypeWeights (
    RoleCode NVARCHAR(100) NOT NULL,
    SkillType NVARCHAR(100) NOT NULL,
    WeightMultiplier DECIMAL(5,2) NOT NULL,
    Description NVARCHAR(255) NULL,
    CONSTRAINT PK_RoleSkillTypeWeights PRIMARY KEY (RoleCode, SkillType)
);

INSERT INTO dbo.RoleSkillTypeWeights

SELECT * FROM (VALUES
('backend_developer','programming_language',1.15,'Primary backend language'),
('backend_developer','framework',1.15,'Backend frameworks'),
('backend_developer','database',1.10,'Data persistence'),
('backend_developer','architecture',1.05,'System design'),
('backend_developer','webframework',0.80,'Frontend less critical'),
('backend_developer','soft_signal',0.50,'Low influence')
) s (RoleCode, SkillType, WeightMultiplier, Description)
WHERE NOT EXISTS (
    SELECT 1 FROM dbo.RoleSkillTypeWeights r
    WHERE r.RoleCode = s.RoleCode AND r.SkillType = s.SkillType
);


INSERT INTO dbo.RoleSkillTypeWeights
SELECT * FROM (VALUES
('backend_developer','programming_language',1.15,'Primary backend language'),
('backend_developer','framework',1.15,'Backend frameworks'),
('backend_developer','database',1.10,'Data persistence'),
('backend_developer','architecture',1.05,'System design'),
('backend_developer','webframework',0.80,'Frontend less critical'),
('backend_developer','soft_signal',0.50,'Low influence')
) s (RoleCode, SkillType, WeightMultiplier, Description)

WHERE NOT EXISTS (
    SELECT 1 FROM dbo.RoleSkillTypeWeights r
    WHERE r.RoleCode = s.RoleCode AND r.SkillType = s.SkillType
);

INSERT INTO dbo.RoleSkillTypeWeights(RoleCode, SkillType, WeightMultiplier, Description)
SELECT * FROM (VALUES
('frontend_developer','webframework',1.20,'Frontend frameworks'),
('frontend_developer','programming_language',1.10,'JS/TS'),
('frontend_developer','framework',0.80,'Backend frameworks'),
('frontend_developer','database',0.70,'Indirect DB usage'),
('frontend_developer','testing',1.05,'UI testing'),
('frontend_developer','soft_signal',0.50,'Low influence')
) s(RoleCode,SkillType,WeightMultiplier,Description)
WHERE NOT EXISTS (
    SELECT 1 FROM dbo.RoleSkillTypeWeights r
    WHERE r.RoleCode = s.RoleCode AND r.SkillType = s.SkillType
);

INSERT INTO dbo.RoleSkillTypeWeights(RoleCode, SkillType, WeightMultiplier, Description)
SELECT * FROM (VALUES
('fullstack_developer','programming_language',1.10,'Multiple languages'),
('fullstack_developer','framework',1.10,'Backend frameworks'),
('fullstack_developer','webframework',1.10,'Frontend frameworks'),
('fullstack_developer','database',1.00,'Balanced DB usage'),
('fullstack_developer','architecture',1.05,'Design responsibility')
) s (RoleCode, SkillType, WeightMultiplier, Description)

WHERE NOT EXISTS (
    SELECT 1 FROM dbo.RoleSkillTypeWeights r
    WHERE r.RoleCode = s.RoleCode AND r.SkillType = s.SkillType
);

INSERT INTO dbo.RoleSkillTypeWeights(RoleCode, SkillType, WeightMultiplier, Description)
SELECT * FROM (VALUES
('devops_engineer','devops',1.25,'Core responsibility'),
('devops_engineer','tool',1.15,'Automation tools'),
('devops_engineer','cloud',1.20,'Cloud platforms'),
('devops_engineer','programming_language',0.80,'Scripting'),
('devops_engineer','framework',0.60,'App frameworks'),
('devops_engineer','architecture',1.10,'Infra design')
) s (RoleCode, SkillType, WeightMultiplier, Description)

WHERE NOT EXISTS (
    SELECT 1 FROM dbo.RoleSkillTypeWeights r
    WHERE r.RoleCode = s.RoleCode AND r.SkillType = s.SkillType
);

INSERT INTO dbo.RoleSkillTypeWeights(RoleCode, SkillType, WeightMultiplier, Description)

SELECT * FROM (VALUES
('cloud_engineer','cloud',1.30,'Primary skill'),
('cloud_engineer','devops',1.15,'IaC & automation'),
('cloud_engineer','tool',1.10,'Cloud tooling'),
('cloud_engineer','programming_language',0.85,'Glue code'),
('cloud_engineer','architecture',1.10,'System design')
) s (RoleCode, SkillType, WeightMultiplier, Description)

WHERE NOT EXISTS (
    SELECT 1 FROM dbo.RoleSkillTypeWeights r
    WHERE r.RoleCode = s.RoleCode AND r.SkillType = s.SkillType
);

INSERT INTO dbo.RoleSkillTypeWeights(RoleCode, SkillType, WeightMultiplier, Description)

SELECT * FROM (VALUES
('ai_engineer','ai_specialization',1.25,'LLM / ML focus'),
('ai_engineer','ai_framework',1.20,'ML frameworks'),
('ai_engineer','ai_engineering',1.15,'Deployment & monitoring'),
('ai_engineer','ai_concept',0.70,'Concepts only'),
('ai_engineer','programming_language',1.00,'Python etc'),
('ai_engineer','soft_signal',0.40,'Minimal impact')
) s (RoleCode, SkillType, WeightMultiplier, Description)

WHERE NOT EXISTS (
    SELECT 1 FROM dbo.RoleSkillTypeWeights r
    WHERE r.RoleCode = s.RoleCode AND r.SkillType = s.SkillType
);

INSERT INTO dbo.RoleSkillTypeWeights(RoleCode, SkillType, WeightMultiplier, Description)

SELECT * FROM (VALUES
('genai_developer','ai_specialization',1.30,'RAG, prompting'),
('genai_developer','ai_framework',1.10,'Supporting ML'),
('genai_developer','database',1.05,'Vector DBs'),
('genai_developer','programming_language',1.00,'Python/JS'),
('genai_developer','soft_signal',0.50,'Low weight')
) s (RoleCode, SkillType, WeightMultiplier, Description)

WHERE NOT EXISTS (
    SELECT 1 FROM dbo.RoleSkillTypeWeights r
    WHERE r.RoleCode = s.RoleCode AND r.SkillType = s.SkillType
);

INSERT INTO dbo.RoleSkillTypeWeights(RoleCode, SkillType, WeightMultiplier, Description)

SELECT * FROM (VALUES
('qa_engineer','testing',1.30,'Primary skill'),
('qa_engineer','tool',1.10,'Automation tools'),
('qa_engineer','programming_language',0.80,'Test scripts'),
('qa_engineer','framework',0.70,'App knowledge')
) s (RoleCode, SkillType, WeightMultiplier, Description)

WHERE NOT EXISTS (
    SELECT 1 FROM dbo.RoleSkillTypeWeights r
    WHERE r.RoleCode = s.RoleCode AND r.SkillType = s.SkillType
);

INSERT INTO dbo.RoleSkillTypeWeights(RoleCode, SkillType, WeightMultiplier, Description)

SELECT * FROM (VALUES
('architect','architecture',1.40,'Primary responsibility'),
('architect','cloud',1.20,'Cloud design'),
('architect','framework',0.90,'Framework familiarity'),
('architect','programming_language',0.80,'Hands-on optional'),
('architect','soft_signal',0.30,'Minimal impact')
) s (RoleCode, SkillType, WeightMultiplier, Description)

WHERE NOT EXISTS (
    SELECT 1 FROM dbo.RoleSkillTypeWeights r
    WHERE r.RoleCode = s.RoleCode AND r.SkillType = s.SkillType
);
