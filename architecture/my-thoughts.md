# My Thoughts - The ATS Cohort

##Cohort Concepts I used:

1. LLM for extraction, summarization and grouping of data.
2. Vectorization (Embeddings) to store master skills, vector search for matching ( candidate skills, JD requirements )

## Key Learnings:

1. LLMs with fine tuning are excellent at identifying mentioned skills as well as inferring requirements. However, LLMs
can ignore explicit instructions at times, you need to have a validation and retry mechanism in place. Also, don't trust 
LLMs with calculations. I am calcualting experince manually through a dedicated function.

2. For a predictable system, it still critical to have your master data with a lot of internal context defined.
For example, ASP.NET belongs to .NET family, OR the Bootstrap, Tailwind, etc. can be alternatives to each other, or 
a candidate that knows bootstrap can be considered as knowing CSS. (Hence I created an hierachy Skill - Parent Skill )

3. Normalization of data before matching can be extremely helpful to avoid misses and false positives. A system with 
prededfined rules also avoids false positives. I created Disambiguity rules with skill master database, to check for mismatches and 
false positives.

4. Vector search is useful, but it's not the silver bullet: I had initially began with vector search for skill matching as my primary
strategy, this proved to be error-prone and slower. A normalized skill matching and alias matching proved a far better first step giving
100% accurate matching, with vector search being an excellent fallback. How you build your vector embeddings (what you include) also matters a lot.

5. Parsing candidate resumes, carefully inferring skills (and not blindly associating skills not mentioned) is critical to have a trustworthy skills 
builder. I was initially reading only explictly mentioned skills, later I also included Job Titles to infer skills. Somewhat opposite goes with JDs, 
it could be beneficial to infer skill requirements from JD to find better candidates (and not to miss eligible candidates)

6. Caching: I noticed I was generating embeddings for the same stuff repeatedly, I thefore built a embedding cache (DB based) to improve 
performance. Caching can be critical in such projects to improve performance and optimize costs.

## Features:

1. I used IBM dockling to read pdf resumes, with an OCR like functionality and ability to read more context (like headings), it proved to be an
excellent pre-LLM step.

2. I tried to evaluate experience on several factors rather than taking it at face value. For example, I gave weight on recency, if a skill has not 
been used in a while, it get's lesser weight. I also calculated experience months manually from the experience blocks. Skills were also given weight
based on where they are mentioned, explicitly in experince or job roles or other sections in the resume.  I am also storing experience separately, so two junior job experience
items do not combine to become a senior experience qualification. 

3. The system is also pretty dynamic, with database configuration of Skills, Weights, Softskill mappings, it's easily customizable. Confidence scores 
are given to virtually every mapping type, giving more accurate results. 

4. Capping: Somebody with a 10-year experience doesn't dominate if there are candidates with 3+ year experience as well, somewhat leveling the playing field 
(this is debatable, but I went with it)


## Possible Alternatives:

I am still tempted to offload the task of actual matching (resume and JD) to a LLM. I also experiemented with it, I extracted skills from a resume,
requirements from a JD and simply asked the LLM to match and give me a summary. It actually worked well. In a production system, this could be 
operationalized either as the only solution, or even as an additional layer. You could technically bypass storing master skills database and simply use
the LLM to match (and perhaps give it additional tools like a websearch Or some technical database RAG to be more accurate).

## My Experiments:

1. When I began researching this project, I thought I will use standarized data as my master skills base to match against. I searched for such data, and 
came across options like O*NET, ESCO (European Union), LightCast Skills Taxonomy. etc. I experiemented a lot with ESCO APIs and it was fruitful, however, 
it still required a lot of additional work. I had built functions to match resume skill with ESCO Id, and then do the same from JD, and then match using the 
ESCO id. This approach can prove extremely beneficial especially if you are building a EU compatible system. 

2. As I mentioned earlier, I also built a direct LLM matching functionality, Extract Resume - Extract JD - Ask the LLM to match. This also showed a lot of promise.

3. I also experiemented with weights (skills, roles, experience), vector combinations for search.