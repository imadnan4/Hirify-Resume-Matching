import React, { useState } from 'react';

interface FaqItem {
  question: string;
  answer: string;
}

export const FaqSection: React.FC = () => {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  const faqs: FaqItem[] = [
    {
      question: 'How does Hirify eliminate hallucinated qualifications?',
      answer: 'Hirify requires every score facet (Skills 35%, Experience 30%, Impact 20%, Edu 5%, Clarity 10%) to be grounded in direct verbatim quotations retrieved from the candidate’s uploaded CV via local MiniLM-384 embeddings. If a claim cannot be quoted, it cannot contribute to the score.'
    },
    {
      question: 'How do Knock-Out (KO) rules work under ADR-0005?',
      answer: 'When a candidate fails an essential threshold (such as missing required work authorization or falling below minimum years of experience), the agent tags the candidate (e.g. KO:missing_work_auth) and strictly caps the overall score at ≤40. Knockouts are never dropped silently — full sub-scores and verbatim quotes are preserved for recruiter audit.'
    },
    {
      question: 'What model architecture powers the autonomous agent loop?',
      answer: 'Hirify utilizes Qwen 3.8-Max via OpenAI-compatible endpoints with native function-calling tools (`score_candidate`, `tag_candidate`, `schedule_interview_stub`). If native tool-calling fails, a structured JSON object fallback automatically activates.'
    },
    {
      question: 'Does scheduling an interview trigger external emails or calendar invites?',
      answer: 'Per ADR-0004, Hirify runs in a sandboxed demo workspace. The "Schedule Interview" action generates and stores an auditable database stub (`INT-xxxx`) without sending live outbound calendar or email communications.'
    }
  ];

  const toggle = (i: number) => {
    setOpenIndex(openIndex === i ? null : i);
  };

  return (
    <section style={{ padding: '64px 24px', maxWidth: '880px', margin: '0 auto' }}>
      <div style={{ textAlign: 'center', marginBottom: '40px' }}>
        <div style={{ fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.08em', fontWeight: 700, color: 'var(--color-olive-600, #5c624b)', marginBottom: '8px' }}>
          Frequently Asked Questions
        </div>
        <h2 style={{
          fontFamily: "'Familjen Grotesk', sans-serif",
          fontSize: '32px',
          fontWeight: 700,
          color: 'var(--color-olive-950, #1b1d16)',
          margin: 0
        }}>
          Grounded screening, explained.
        </h2>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {faqs.map((faq, i) => {
          const isOpen = openIndex === i;
          return (
            <div
              key={i}
              style={{
                borderRadius: '12px',
                background: 'var(--color-olive-50, #ffffff)',
                border: '1px solid var(--color-olive-200, #e9ece0)',
                overflow: 'hidden'
              }}
            >
              <button
                type="button"
                onClick={() => toggle(i)}
                style={{
                  width: '100%',
                  padding: '18px 20px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  textAlign: 'left'
                }}
              >
                <span style={{
                  fontFamily: "'Familjen Grotesk', sans-serif",
                  fontSize: '16.5px',
                  fontWeight: 700,
                  color: 'var(--color-olive-950, #1b1d16)'
                }}>
                  {faq.question}
                </span>
                <span style={{ fontSize: '18px', fontWeight: 600, color: 'var(--color-olive-600, #5c624b)', marginLeft: '16px' }}>
                  {isOpen ? '−' : '+'}
                </span>
              </button>
              {isOpen && (
                <div style={{
                  padding: '0 20px 18px',
                  fontSize: '14px',
                  color: 'var(--color-olive-700, #404434)',
                  lineHeight: '1.6'
                }}>
                  {faq.answer}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
};
