Extract key facts and obligations from the document.
<document>
{document_text}
</document>

<definitions>
{definitions}
</definitions>

Task:
1. Extract key facts like dates, money amounts, lock-in periods, notice periods.
2. List obligations for the user ({user_role}) and the counterparty ({counterparty_role}).
3. Write summaries at three levels: simple, standard, detailed.
4. Ensure every fact and obligation has a valid citation to a clause_id. If a fact is absent, return null.
