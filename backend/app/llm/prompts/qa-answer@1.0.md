Answer the user's question using ONLY the provided clauses and definitions.

<clauses>
{document_text}
</clauses>

<definitions>
{definitions}
</definitions>

<recent_chat_history>
{chat_history}
</recent_chat_history>

Question: {question}

Task:
If the answer cannot be found in the clauses, set `answerable` to false and suggest follow-up questions.
If answerable, break the answer into segments, each with exact citations.
