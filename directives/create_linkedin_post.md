# Directive: Create LinkedIn Post

## Purpose

Generate high-quality, engaging LinkedIn posts using proven templates while ensuring content uniqueness and compliance with platform best practices.

---

## Inputs

**Required:**
- `topic`: The main subject or theme of the post (string)
- `post_type`: One of: `story`, `value`, `contrarian`, `insight`, `learning`
- `tone`: Professional, casual, enthusiastic, thought-leader, vulnerable (default: professional)
- `key_points`: 3-5 bullet points to include in the post (list of strings)

**Optional:**
- `target_audience`: Who should engage with this post? (default: "industry peers")
- `call_to_action`: Specific question or engagement prompt (default: auto-generated)
- `include_hashtags`: Boolean (default: true)
- `media_suggestion`: Type of media that would complement the post (image, carousel, video, none)

---

## Execution Scripts Used

1. **`execution/generate_post_content.py`** - Main content generation
2. **`execution/check_rate_limits.py`** - Verify posting frequency compliance
3. **`execution/utils/data_storage.py`** - Save generated post to queue

---

## Step-by-Step Process

### Phase 1: Validation (Orchestration Layer)

1. **Validate inputs**
   - Check that `topic` is not empty
   - Verify `post_type` is one of the 5 allowed types
   - Ensure `key_points` has at least 2 items
   - Reject if topic is overly promotional or spam-like

2. **Check recent posts**
   - Load `.tmp/generated_posts.json`
   - Load `posts` table from SQLite
   - Compare topic against last 10 posts
   - Reject if similarity score > 70% (avoid repetition)

3. **Verify posting schedule**
   - Check daily post count from activity log
   - Confirm within safe limits (1-2 posts/day depending on account age)
   - If limit reached, queue for next day

### Phase 2: Content Generation (Execution Layer)

4. **Run `generate_post_content.py`**
   ```bash
   python execution/generate_post_content.py \
     --topic "{topic}" \
     --type {post_type} \
     --tone {tone} \
     --points "{key_points_json}" \
     --output ".tmp/generated_posts.json"
   ```

5. **Generation process inside script:**
   - Select appropriate template based on `post_type`
   - Structure hook (first 150 characters critical)
   - Develop body using key points
   - Add authentic voice/tone markers
   - Craft compelling call-to-action
   - Generate 3-5 relevant hashtags
   - Suggest media type if applicable

6. **Quality checks:**
   - Length: 1000-3000 characters (optimal engagement)
   - Readability: Flesch-Kincaid grade 8-10
   - Hook strength: First line must grab attention
   - Spacing: Short paragraphs (2-3 lines max)
   - Emoji usage: Sparse and professional (0-3 emojis)

### Phase 3: Storage & Queue Management

7. **Save to `.tmp/generated_posts.json`**
   ```json
   {
     "post_id": "uuid_timestamp",
     "topic": "AI trends in 2026",
     "post_type": "insight",
     "content": "Full post text here...",
     "hashtags": ["#AI", "#MachineLearning", "#TechTrends"],
     "created_at": "2026-03-13T10:30:00Z",
     "status": "draft",
     "scheduled_for": null,
     "media_suggestion": "carousel",
     "uniqueness_score": 0.92
   }
   ```

8. **Update activity log**
   - Log content generation event
   - Track time spent
   - Record template used

---

## Expected Outputs

**Primary Output:**
- New entry in `.tmp/generated_posts.json` with status `draft`

**Secondary Outputs:**
- Console confirmation message
- Activity log entry in SQLite database
- Uniqueness validation report

**Success Criteria:**
- ✅ Post follows selected template structure
- ✅ Content is unique (>85% uniqueness score)
- ✅ Within character limits (1000-3000 chars)
- ✅ Includes relevant hashtags (if enabled)
- ✅ Clear call-to-action present
- ✅ No spelling/grammar errors

---

## Error Handling

### Error Types & Responses

| Error | Detection | Response |
|-------|-----------|----------|
| Empty topic | Input validation fails | Request user to provide topic |
| Invalid post_type | Not in allowed list | Auto-correct to closest match or ask user |
| Too few key_points | < 2 points provided | Ask user to elaborate or use AI to expand |
| Duplicate content | Similarity > 70% | Regenerate with different angle |
| Overly promotional | Contains sales language | Warn user, suggest value-first approach |
| Generation failure | Script returns error | Retry up to 3 times with varied prompts |
| File write error | JSON save fails | Log error, attempt backup storage |

### Retry Logic

```python
MAX_RETRIES = 3
BACKOFF_SECONDS = 30

for attempt in range(MAX_RETRIES):
    try:
        result = generate_post_content(...)
        break
    except RateLimitError:
        wait(BACKOFF_SECONDS * (attempt + 1))
    except TemplateError as e:
        log(f"Template error: {e}")
        switch_template()
    except Exception as e:
        if attempt == MAX_RETRIES - 1:
            raise CriticalError(f"Generation failed after {MAX_RETRIES} attempts")
        continue
```

---

## Edge Cases

### 1. Controversial Topics
**Scenario**: Topic involves politics, sensitive social issues
**Handling**: 
- Warn user about potential engagement impact
- Suggest neutral framing
- Offer to postpone or skip

### 2. Technical/Complex Subjects
**Scenario**: Topic requires specialized knowledge (quantum computing, biotech)
**Handling**:
- Request additional context from user
- Use simpler analogies
- Focus on implications rather than technical details

### 3. Breaking News/Trending Topics
**Scenario**: User wants to comment on very recent event
**Handling**:
- Prioritize speed over perfection
- Reduce uniqueness threshold to 60%
- Flag for immediate publishing

### 4. Multi-Language Requests
**Scenario**: User requests post in non-English language
**Handling**:
- Check if generation model supports language
- Validate grammar with native speaker rules
- Adjust hashtag strategy for language community

### 5. Very Short Posts (Micro-content)
**Scenario**: User wants punchy 1-2 sentence posts
**Handling**:
- Allow override of minimum length
- Ensure hook is still strong
- Compensate with powerful imagery suggestion

### 6. Industry Jargon
**Scenario**: Topic requires niche terminology
**Handling**:
- Balance jargon with accessibility
- Define acronyms on first use
- Target 80% general audience comprehension

---

## Quality Metrics

After generation, evaluate:

1. **Hook Score** (1-10): Does first line stop the scroll?
2. **Clarity Score** (1-10): Is message easy to understand?
3. **Value Score** (1-10): Does audience gain something useful?
4. **Authenticity Score** (1-10): Does it sound human and genuine?
5. **Engagement Potential** (1-10): Will people comment/share?

**Threshold**: Only queue posts with average score ≥ 7.0

---

## Compliance Checklist

Before finalizing:

- [ ] No false or misleading claims
- [ ] No medical/legal/financial advice without disclaimer
- [ ] Respectful language (no hate speech, discrimination)
- [ ] Proper attribution for quotes/statistics
- [ ] No competitor bashing
- [ ] Privacy-respecting (no doxxing, oversharing)
- [ ] Compliant with LinkedIn Professional Community Policies

---

## Example Usage

### Example 1: Value Post
```
Input:
  topic: "Time management for remote workers"
  post_type: value
  tone: professional
  key_points:
    - "Time blocking technique"
    - "Async communication benefits"
    - "Setting boundaries with family"
    - "Tools that help (Notion, Calendly)"

Output:
  Post ID: post_20260313_103000
  Status: draft
  Location: .tmp/generated_posts.json
```

### Example 2: Story Post
```
Input:
  topic: "My biggest career mistake"
  post_type: story
  tone: vulnerable
  key_points:
    - "Turned down dream job in 2020"
    - "Thought I knew better"
    - "Company went public year later"
    - "Learned to trust my gut less"

Output:
  Post ID: post_20260313_141500
  Status: draft
  Location: .tmp/generated_posts.json
```

---

## Continuous Improvement

After post publishes and gathers engagement data:

1. **Track metrics**: impressions, likes, comments, shares
2. **Analyze performance**: Which templates work best?
3. **A/B test**: Try variations of hooks, CTAs, posting times
4. **Update templates**: Refine based on data
5. **Log learnings**: Update this directive with new insights

**Feedback Loop:**
```
Post Performance → Analysis → Template Adjustment → Better Posts → Repeat
```

---

## Related Directives

- **publish_linkedin_post.md** - Next step: actually publish the generated post
- **content_scheduler.md** - Schedule when to publish
- **engagement_tracking.md** - Measure post performance after publishing

---

*Last Updated: 2026-03-13*  
*Version: 1.0*
