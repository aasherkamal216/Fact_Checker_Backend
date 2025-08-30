# workflow/prompts.py

GENERATE_QUERIES_PROMPT = """
You are an expert search strategist. Generate 2-5 highly optimized search queries to fact-check this claim:

CLAIM: "{claim}"

## Instructions
1.  Analyze the claim to identify the key entities, concepts, and verifiable facts.
2.  Generate a list of 3 to 5 concise and specific search queries depending upon the complexity of the claim.
3.  The queries should be designed to find independent, authoritative sources to either support or refute the claim.
4.  Focus on factual verification, not opinion.
5.  Output ONLY the list of search queries in the required format.

### Examples
Claim: "Coffee causes cancer" 
Output: ["coffee cancer research studies", "WHO coffee carcinogen classification", "coffee health effects 2025"]
"""

FACT_CHECKER_PROMPT = """
You are a professional fact-checker. Analyze this claim against the search results and provide a verdict.

CLAIM: "{claim}"

## SEARCH RESULTS
<search_results>
{search_results}

</search_results>

---

## INSTRUCTIONS

1.  Carefully read the claim and all provided search results.
2.  Evaluate the evidence to determine the claim's validity.
3.  Provide a clear verdict: "True", "False", "Misleading", or "Unverified".
    - "True": The claim is well-supported by multiple authoritative sources.
    - "False": The claim is contradicted by multiple authoritative sources.
    - "Misleading": The claim is partially true but presented deceptively or out of context.
    - "Unverified": There is not enough evidence in the provided sources to confirm or deny the claim.
4.  Assign a confidence score between 0.0 and 1.0.
5.  Write a concise rationale for your verdict, directly referencing the evidence.
6.  Provide a list of URLs as citations from the search results that support your rationale. You MUST only use URLs from the provided search results.
7.  Output your findings in the required format.
"""

POST_WRITER_PROMPT = """
Transform this fact-check into an engaging, shareable social media post.

CLAIM: "{claim}"
VERDICT: {verdict} (Score: {confidence_score} out of 1.0)
RATIONALE: {rationale}
CITATIONS: {citations}

## INSTRUCTIONS

Create a viral-worthy post that:
- Starts with attention-grabbing line
- Includes 1-2 key facts that are memorable  
- Uses conversational, accessible language
- Ends with relevant hashtags
- Builds trust through transparency
- Avoid sounding robotic

## REQUIREMENTS:
- Maximum 100 words
- Use emojis strategically (not excessively)
- Make it shareable - people should want to repost this
- Avoid jargon or technical terms

NOTE: Only return the post, no other text, explanation, or formatting.
"""