# Scoring System

Website quality is scored out of 100. Lower scores indicate a weaker website and a stronger redesign or transformation opportunity.

## Website Quality Categories

| Category | Max Points |
| --- | ---: |
| UI/UX Design Quality | 20 |
| Mobile Responsiveness | 15 |
| Page Speed | 15 |
| SEO Basics | 15 |
| Conversion / CTA | 15 |
| Trust Signals | 10 |
| Technology Modernity | 10 |

## Lead Priority

| Website Score | Priority |
| ---: | --- |
| 0-40 | Very Hot Lead |
| 41-60 | Hot Lead |
| 61-75 | Warm Lead |
| 76-100 | Low Priority |

## Final Lead Score

The final lead score is normalized to 100:

```text
Final Lead Score =
  Website Weakness Score
  + Business Value Score
  + Contactability Score
  + Industry Priority Score
  + Location Priority Score
  + AI Closing Probability
```

The first five inputs are deterministic platform scores. AI closing probability is included only after an AI report exists. If no AI report exists, final scoring uses the deterministic inputs only.

## Interpretation

- High final score means the lead is commercially attractive for Siru.
- Low website quality increases opportunity when the business appears valuable and contactable.
- AI output should influence prioritization after a successful AI job, but deterministic scores remain visible for auditability.

