export async function extractTextPlain(file: File): Promise<{text: string, pageCount: number}> {
  const text = await file.text();
  return {
    text: `[[page:1]]\n${text}`,
    pageCount: 1
  };
}
