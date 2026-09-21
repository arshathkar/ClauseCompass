Analyze the following batch of clauses for risks based on the taxonomy keys.

<document>
{document_text}
</document>

<definitions>
{definitions}
</definitions>

<taxonomy_keys>
{taxonomy_keys}
</taxonomy_keys>

<law_pack>
{law_pack}
</law_pack>

Task:
Return a list of findings for any clauses that present a risk. The `category` must be one of the provided taxonomy keys.
Do not provide findings for clauses without issues.
